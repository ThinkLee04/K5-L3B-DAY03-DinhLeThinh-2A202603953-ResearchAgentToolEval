from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from tools._shared import err


def deduplicate_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item for each URL, ignoring host case and fragments."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of objects")

        seen: set[tuple[str, str, str, str]] = set()
        unique: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be an object")
            url = item.get("url")
            if not isinstance(url, str) or not url.strip():
                raise ValueError(f"items[{index}].url must be a non-empty string")

            # urlsplit can raise ValueError for malformed URLs (e.g. broken IPv6).
            parsed = urlsplit(url.strip())
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                raise ValueError(f"items[{index}].url must be an absolute HTTP(S) URL")
            if parsed.username is not None or parsed.password is not None:
                raise ValueError(f"items[{index}].url must not contain credentials")

            # Preserve path case and query: they can identify different resources.
            # Keep the original item/URL for citation; normalize only the key.
            key = (parsed.scheme, parsed.netloc.lower(), parsed.path, parsed.query)
            if key not in seen:
                seen.add(key)
                unique.append(item)

        return {
            "tool": "deduplicate",
            "items": unique,
            "input_count": len(items),
            "unique_count": len(unique),
            "removed_count": len(items) - len(unique),
        }
    except Exception as exc:
        return err("deduplicate", exc)
