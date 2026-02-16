"""Awareness tools for discovering available sources and metadata.

These tools mirror Claude Code's approach: know what exists, understand structure,
before diving into search.
"""

from datetime import datetime, timezone
from pathlib import Path

from agno.tools import tool

from ..context.source_registry import SOURCE_REGISTRY


def _format_size(size: int) -> str:
    """Format file size in human-readable format."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def create_list_sources_tool():
    """Create list_sources tool."""

    @tool
    def list_sources(
        source_type: str | None = None,
        include_details: bool = False,
    ) -> str:
        """List available knowledge sources.

        Use this to understand what sources are connected and what they contain.
        Always start here if you're unsure where to look.

        Args:
            source_type: Filter to specific source type (files).
                        If None, lists all sources.
            include_details: Include detailed info about each source's contents.
        """
        lines: list[str] = ["## Available Sources", ""]

        sources = SOURCE_REGISTRY.get("sources", [])

        if source_type:
            sources = [s for s in sources if s["source_type"] == source_type]

        if not sources:
            return f"No sources found for type: {source_type}" if source_type else "No sources configured."

        for source in sources:
            lines.append(f"### {source['source_name']} (`{source['source_type']}`)")
            if source.get("description"):
                lines.append(source["description"])
            lines.append("")

            if include_details:
                if source.get("capabilities"):
                    lines.append("**Capabilities:**")
                    for cap in source["capabilities"][:5]:
                        lines.append(f"  - {cap}")
                    lines.append("")

                if source.get("common_locations"):
                    lines.append("**Where to find things:**")
                    for key, value in list(source["common_locations"].items())[:6]:
                        lines.append(f"  - {key}: `{value}`")
                    lines.append("")

                if source["source_type"] == "files" and source.get("directories"):
                    lines.append("**Directories:**")
                    for directory in source["directories"]:
                        lines.append(f"  - **{directory['name']}**: {directory.get('description', '')}")
                    lines.append("")

            lines.append("")

        return "\n".join(lines)

    return list_sources


def create_get_metadata_tool(base_dir: Path):
    """Create get_metadata tool backed by local filesystem."""

    @tool
    def get_metadata(
        source: str,
        path: str | None = None,
    ) -> str:
        """Get metadata about a source or specific path without reading content.

        Use this to understand structure before searching or reading.
        For files: lists directories, folder contents, or file metadata.

        Args:
            source: Source type (files).
            path: Optional path to inspect. Examples:
                  - None: show top-level directories
                  - "company-docs": show contents of company-docs/
                  - "company-docs/policies/employee-handbook.md": show file metadata
        """
        if source != "files":
            return f"Unknown source: {source}. Available: files"

        if not base_dir.is_dir():
            return f"Data directory not found: {base_dir}"

        try:
            if not path:
                # List top-level directories with file counts
                lines = ["## Data Directory Structure", ""]
                entries = sorted(base_dir.iterdir())
                if not entries:
                    return "## Data Directory\n\nEmpty directory."

                for entry in entries:
                    if entry.is_dir():
                        count = sum(1 for _ in entry.rglob("*") if _.is_file())
                        lines.append(f"[dir] **{entry.name}/**  ({count} files)")
                    elif entry.is_file():
                        lines.append(f"[file] {entry.name}  ({_format_size(entry.stat().st_size)})")
                return "\n".join(lines)

            # Normalize path
            clean = path.strip("/")
            target = base_dir / clean

            if target.is_file():
                # File metadata
                stat = target.stat()
                modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
                lines = [f"## File: {clean}", ""]
                lines.append(f"**Size:** {_format_size(stat.st_size)}")
                lines.append(f"**Modified:** {modified}")

                # Line count for text files
                if target.suffix.lower() in {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py", ".js", ".ts"}:
                    try:
                        line_count = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
                        lines.append(f"**Lines:** {line_count}")
                    except OSError:
                        pass

                return "\n".join(lines)

            if target.is_dir():
                # Directory listing
                lines = [f"## Contents of {clean}", ""]
                entries = sorted(target.iterdir())

                if not entries:
                    return f"Empty directory: {clean}"

                for entry in entries:
                    if entry.is_dir():
                        count = sum(1 for _ in entry.rglob("*") if _.is_file())
                        lines.append(f"[dir] **{entry.name}/**  ({count} files)")
                    elif entry.is_file():
                        stat = entry.stat()
                        size_info = f" ({_format_size(stat.st_size)})"
                        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
                        lines.append(f"[file] {entry.name}{size_info} - {modified}")

                return "\n".join(lines)

            return f"Path not found: {path}"

        except OSError as e:
            return f"Error inspecting {source}: {e}"

    return get_metadata
