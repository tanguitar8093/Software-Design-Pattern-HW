from abc import ABC, abstractmethod
from typing import List, Optional

class Event(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

class Member:
    def __init__(self, id: str, is_admin: bool = False):
        self.id = id
        self.is_admin = is_admin

class Message:
    def __init__(self, author_id: str, content: str, tags: List[str]):
        self.author_id = author_id
        self.content = content
        self.tags = tags

class Post:
    def __init__(self, id: str, author_id: str, title: str, content: str, tags: List[str]):
        self.id = id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.tags = tags

class Comment:
    def __init__(self, post_id: str, author_id: str, content: str, tags: List[str]):
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.tags = tags
