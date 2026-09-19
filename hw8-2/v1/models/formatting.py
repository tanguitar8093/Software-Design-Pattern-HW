from typing import List


def format_tags(tags: List[str]) -> str:
    return ", ".join(f"@{tag}" for tag in tags)


def with_tags(content: str, tags: List[str]) -> str:
    tag_str = format_tags(tags)
    return f"{content} {tag_str}" if tag_str else content
