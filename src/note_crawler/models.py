from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


@dataclass
class Creator:
    id: int
    urlname: str
    nickname: str
    profile: str
    note_count: int
    follower_count: int
    following_count: int
    profile_image_url: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Creator":
        d = data["data"] if "data" in data else data
        return cls(
            id=d["id"],
            urlname=d["urlname"],
            nickname=d.get("nickname") or d.get("name", ""),
            profile=d.get("profile", ""),
            note_count=d.get("noteCount", 0),
            follower_count=d.get("followerCount", 0),
            following_count=d.get("followingCount", 0),
            profile_image_url=d.get("profileImageUrl"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Article:
    key: str
    slug: str
    title: str
    type: str
    status: str
    url: str
    publish_at: str | None
    like_count: int
    price: int
    is_paid: bool
    description: str | None
    eyecatch: str | None
    body_html: str | None = None
    body_markdown: str | None = None
    comment_count: int = 0
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_list_item(cls, item: dict[str, Any], creator_urlname: str) -> "Article":
        key = item["key"]
        return cls(
            key=key,
            slug=item.get("slug", key),
            title=item.get("name", ""),
            type=item.get("type", ""),
            status=item.get("status", ""),
            url=f"https://note.com/{creator_urlname}/n/{key}",
            publish_at=item.get("publishAt"),
            like_count=item.get("likeCount", 0),
            price=item.get("price", 0),
            is_paid=bool(item.get("price", 0)),
            description=item.get("description"),
            eyecatch=item.get("eyecatch"),
            raw=item,
        )

    def attach_detail(self, detail: dict[str, Any]) -> None:
        d = detail["data"] if "data" in detail else detail
        self.body_html = d.get("body")
        self.comment_count = d.get("comment_count", self.comment_count)
        if d.get("description"):
            self.description = d["description"]

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out.pop("raw", None)
        return out

    @property
    def filename_stem(self) -> str:
        date = ""
        if self.publish_at:
            try:
                date = datetime.fromisoformat(self.publish_at).strftime("%Y-%m-%d")
            except ValueError:
                date = self.publish_at[:10]
        safe_title = "".join(
            ch for ch in self.title if ch not in '/\\:*?"<>|\n\t'
        ).strip()[:80] or self.key
        return f"{date}_{safe_title}_{self.key}" if date else f"{safe_title}_{self.key}"
