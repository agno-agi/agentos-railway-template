"""
S3 Tools
========

Generic S3 browsing toolkit for agents.

Provides list, search, read, and write operations against S3-compatible
storage using virtual buckets (prefixes in a single real bucket).
"""

from agno.tools import Toolkit, tool

from storage.client import bucket_name, get_s3_client, is_authenticated, is_configured

# Virtual buckets (prefixes in the real S3 bucket)
VIRTUAL_BUCKETS = [
    {"name": "company-docs", "description": "Company documents and policies"},
    {"name": "engineering-docs", "description": "Technical docs, runbooks, architecture"},
    {"name": "data-exports", "description": "Reports, metrics, data exports"},
]

TEXT_EXTENSIONS = {
    ".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".xml",
    ".py", ".js", ".ts", ".html", ".css", ".sql", ".sh", ".toml",
    ".cfg", ".ini", ".log", ".rst",
}


def _is_text_file(key: str) -> bool:
    return any(key.lower().endswith(ext) for ext in TEXT_EXTENSIONS)


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
        return content[:context_chars * 2] + "..."
    start = max(0, idx - context_chars)
    end = min(len(content), idx + len(query) + context_chars)
    snippet = content[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    return snippet


class S3Tools(Toolkit):
    def __init__(self):
        super().__init__(name="s3_tools")
        self.register(self.list_buckets)
        self.register(self.list_files)
        self.register(self.search_files)
        self.register(self.read_file)
        self.register(self.write_file)

    @tool
    def list_buckets(self) -> str:
        """List available S3 buckets (virtual buckets organized by topic)."""
        if not is_configured:
            return "Error: S3 storage is not configured."
        lines = ["Available buckets:\n"]
        for b in VIRTUAL_BUCKETS:
            lines.append(f"  s3://{b['name']}/  -- {b['description']}")
        return "\n".join(lines)

    @tool
    def list_files(self, path: str | None = None, limit: int = 50) -> str:
        """List files and directories in an S3 path.

        Args:
            path: S3 path like 'company-docs/policies/' or 's3://company-docs/'. Omit to list all buckets.
            limit: Max files to return (default 50).
        """
        if not is_configured:
            return "Error: S3 storage is not configured."

        if path is None or path.strip() == "":
            return self.list_buckets()

        clean = path.replace("s3://", "").strip("/")
        prefix = clean + "/" if clean else ""

        try:
            client = get_s3_client()
            resp = client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                Delimiter="/",
                MaxKeys=limit,
            )

            dirs = [p["Prefix"] for p in resp.get("CommonPrefixes", [])]
            files = resp.get("Contents", [])

            if not dirs and not files:
                return f"No files found at `s3://{clean}/`"

            lines = [f"Contents of `s3://{clean}/`:\n"]
            for d in dirs:
                display = d[len(prefix) :].rstrip("/")
                lines.append(f"  {display}/")
            for f in files:
                key = f["Key"]
                if key == prefix:
                    continue
                display = key[len(prefix) :]
                lines.append(f"  {display}  ({_format_size(f['Size'])})")

            return "\n".join(lines)
        except Exception as e:
            return f"Error listing `s3://{clean}/`: {e}"

    @tool
    def search_files(self, query: str, bucket: str | None = None, limit: int = 10) -> str:
        """Search for files by name or content (grep-like).

        Args:
            query: Search term to match against filenames and file contents.
            bucket: Optional bucket to scope search (e.g. 'company-docs'). Searches all if omitted.
            limit: Max results to return (default 10).
        """
        if not is_configured:
            return "Error: S3 storage is not configured."

        prefix = ""
        if bucket:
            prefix = bucket.replace("s3://", "").strip("/") + "/"

        try:
            client = get_s3_client()
            paginator = client.get_paginator("list_objects_v2")
            params = {"Bucket": bucket_name}
            if prefix:
                params["Prefix"] = prefix

            query_lower = query.lower()
            results = []

            for page in paginator.paginate(**params):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    size = obj["Size"]

                    name_match = query_lower in key.lower()

                    content_match = False
                    snippet = ""
                    if _is_text_file(key) and size < 500_000:
                        try:
                            body = client.get_object(Bucket=bucket_name, Key=key)["Body"].read().decode("utf-8", errors="replace")
                            if query_lower in body.lower():
                                content_match = True
                                snippet = _extract_snippet(body, query)
                        except Exception:
                            pass

                    if name_match or content_match:
                        entry = f"s3://{key}  ({_format_size(size)})"
                        if snippet:
                            entry += f"\n    > {snippet}"
                        results.append(entry)

                    if len(results) >= limit:
                        break
                if len(results) >= limit:
                    break

            if not results:
                scope = f"in `{bucket}`" if bucket else "across all buckets"
                return f"No matches for '{query}' {scope}."

            header = f"Found {len(results)} match(es) for '{query}':\n"
            return header + "\n".join(f"  {r}" for r in results)
        except Exception as e:
            return f"Error searching for '{query}': {e}"

    @tool
    def read_file(self, path: str) -> str:
        """Read the full content of a file from S3.

        Args:
            path: File path like 'company-docs/policies/pto-policy.md' or 's3://company-docs/policies/pto-policy.md'.
        """
        if not is_configured:
            return "Error: S3 storage is not configured."

        key = path.replace("s3://", "").strip("/")

        try:
            client = get_s3_client()
            resp = client.get_object(Bucket=bucket_name, Key=key)
            body = resp["Body"].read()

            if _is_text_file(key):
                content = body.decode("utf-8", errors="replace")
                return f"## `s3://{key}`\n\n{content}"
            else:
                return f"Binary file `s3://{key}` ({_format_size(len(body))}). Cannot display content."
        except client.exceptions.NoSuchKey:
            return f"File not found: `s3://{key}`"
        except Exception as e:
            return f"Error reading `s3://{key}`: {e}"

    @tool
    def write_file(self, path: str, content: str) -> str:
        """Write content to a file in S3 (requires authenticated access).

        Args:
            path: Destination path like 'company-docs/notes/my-note.md'.
            content: Text content to write.
        """
        if not is_authenticated:
            return "Error: Write access requires authenticated S3 credentials."

        key = path.replace("s3://", "").strip("/")

        try:
            client = get_s3_client()
            client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content.encode("utf-8"),
                ContentType="text/plain",
            )
            return f"Written to `s3://{key}` ({_format_size(len(content.encode('utf-8')))})"
        except Exception as e:
            return f"Error writing to `s3://{key}`: {e}"
