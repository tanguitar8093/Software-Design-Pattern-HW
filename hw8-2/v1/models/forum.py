from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .formatting import with_tags


@dataclass
class Comment:
    author_id: str
    content: str
    tags: List[str] = field(default_factory=list)


class Post:
    def __init__(self, id: str, author_id: str, title: str, content: str, tags: List[str]) -> None:
        self.id = id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.tags = tags
        self.comments: List[Comment] = []

    def add_comment(self, comment: Comment) -> None:
        self.comments.append(comment)


class Forum:
    """對應 OOA-Clean.mmd Forum：管理貼文、轉發留言，並於新貼文時通報 Bot。"""

    def __init__(self) -> None:
        self.bot: Optional["Bot"] = None  # noqa: F821 (由 WaterballCommunity 組裝時注入)
        self._posts: Dict[str, Post] = {}

    def create_post(self, post: Post) -> None:
        self._posts[post.id] = post
        print(f"{post.author_id}: 【{post.title}】{with_tags(post.content, post.tags)}")
        self.bot.on_post_published(post)

    def add_comment(self, post_id: str, comment: Comment) -> None:
        post = self._posts.get(post_id)
        if post is None:
            return
        post.add_comment(comment)
        print(f"🤖 comment in post {post_id}: {with_tags(comment.content, comment.tags)}")
