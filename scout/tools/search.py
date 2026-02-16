"""Content search tool for local file storage."""

from pathlib import Path

from agno.tools import tool

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".sql",
    ".sh",
    ".toml",
    ".cfg",
    ".ini",
    ".log",
    ".rst",
}


def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def _extract_snippet(content: str, query: str, context_chars: int = 200) -> str:
    query_lower = query.lower()
    content_lower = content.lower()
    idx = content_lower.find(query_lower)
    if idx == -1:
        for word in query_lower.split():
            idx = content_lower.find(word)
            if idx != -1:
                break
    if idx == -1:
        return content[: context_chars * 2] + "..."
    start = max(0, idx - context_chars)
    end = min(len(content), idx + len(query) + context_chars)
    snippet = content[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    return snippet


def create_search_content_tool(base_dir: Path):
    """Create a grep-like content search tool scoped to base_dir."""

    @tool
    def search_content(query: str, directory: str | None = None, limit: int = 10) -> str:
        """Search for files by name or content (grep-like).

        Args:
            query: Search term to match against filenames and file contents.
            directory: Optional directory to scope search (e.g. 'company-docs'). Searches all if omitted.
            limit: Max results to return (default 10).
        """
        search_root = base_dir
        if directory:
            clean = directory.strip("/")
            search_root = base_dir / clean
            if not search_root.is_dir():
                return f"Directory not found: {clean}"

        if not search_root.is_dir():
            return f"Data directory not found: {search_root}"

        query_lower = query.lower()
        results: list[str] = []

        for filepath in sorted(search_root.rglob("*")):
            if not filepath.is_file():
                continue

            rel_path = filepath.relative_to(base_dir)
            name_match = query_lower in str(rel_path).lower()

            content_match = False
            snippet = ""
            if filepath.suffix.lower() in TEXT_EXTENSIONS and filepath.stat().st_size < 500_000:
                try:
                    content = filepath.read_text(encoding="utf-8", errors="replace")
                    if query_lower in content.lower():
                        content_match = True
                        snippet = _extract_snippet(content, query)
                except OSError:
                    pass

            if name_match or content_match:
                size = _format_size(filepath.stat().st_size)
                entry = f"{rel_path}  ({size})"
                if snippet:
                    entry += f"\n    > {snippet}"
                results.append(entry)

            if len(results) >= limit:
                break

        if not results:
            scope = f"in `{directory}`" if directory else "across all directories"
            return f"No matches for '{query}' {scope}."

        header = f"Found {len(results)} match(es) for '{query}':\n"
        return header + "\n".join(f"  {r}" for r in results)

    return search_content
