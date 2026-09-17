from __future__ import annotations
from typing import List, Optional
from ...common.events import PostPublishedEvent
from ...common.observer import Observable


class Comment:
    def __init__(self, authorId: str, content: str, tags: Optional[List[str]] = None):
        self.authorId: str = authorId
        self.content: str = content
        self.tags: List[str] = tags if tags is not None else []


class Post:
    def __init__(self, id: str, authorId: str, title: str, content: str, tags: Optional[List[str]] = None):
        self.id: str = id
        self.authorId: str = authorId
        self.title: str = title
        self.content: str = content
        self.tags: List[str] = tags if tags is not None else []
        self._comments: List[Comment] = []

    def addComment(self, comment: Comment) -> None:
        self._comments.append(comment)


class Forum(Observable):
    def __init__(self, output_sink: Optional[List[str]] = None):
        super().__init__()
        self._posts: List[Post] = []
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink

    def createPost(self, post: Post) -> None:
        self._posts.append(post)
        tags_str = ""
        if post.tags:
            tags_str = " " + ", ".join([f"@{t}" for t in post.tags])
        self._output_sink.append(f"{post.authorId}: 【{post.title}】{post.content}{tags_str}")
        self.notify(PostPublishedEvent(post))

    def addComment(self, postId: str, comment: Comment) -> None:
        tags_str = ""
        if comment.tags:
            tags_str = " " + ", ".join([f"@{t}" for t in comment.tags])
        if comment.authorId == "bot":
            self._output_sink.append(f"🤖 comment in post {postId}: {comment.content}{tags_str}")
        else:
            self._output_sink.append(f"💬 comment in post {postId} by {comment.authorId}: {comment.content}{tags_str}")
