from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Iterable

import html2text

from .client import NoteClient
from .models import Article, Creator

logger = logging.getLogger(__name__)


def _make_html2text() -> html2text.HTML2Text:
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_links = False
    h.ignore_images = False
    h.protect_links = True
    h.unicode_snob = True
    return h


class Crawler:
    """Crawl all notes from a single creator and persist them to disk."""

    def __init__(
        self,
        urlname: str,
        output_dir: str | Path,
        client: NoteClient | None = None,
        sleep_seconds: float = 1.0,
        include_paid: bool = False,
        formats: Iterable[str] = ("json", "markdown"),
        progress: Callable[[str], None] | None = None,
    ) -> None:
        self.urlname = urlname
        self.output_dir = Path(output_dir)
        self.client = client or NoteClient()
        self._owns_client = client is None
        self.sleep_seconds = sleep_seconds
        self.include_paid = include_paid
        self.formats = set(formats)
        self.progress = progress or (lambda msg: logger.info(msg))
        self._md = _make_html2text()

    def run(self) -> dict[str, object]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        articles_dir = self.output_dir / "articles"
        articles_dir.mkdir(exist_ok=True)

        creator = Creator.from_api(self.client.get_creator(self.urlname))
        self._write_json(self.output_dir / "creator.json", creator.to_dict())
        self.progress(
            f"creator: {creator.nickname} (@{creator.urlname}) "
            f"notes={creator.note_count}"
        )

        index: list[dict[str, object]] = []
        seen_keys: set[str] = set()

        for raw in self.client.iter_creator_contents(self.urlname, kind="note"):
            article = Article.from_list_item(raw, self.urlname)
            if article.key in seen_keys:
                continue
            seen_keys.add(article.key)

            if article.is_paid and not self.include_paid:
                self.progress(f"skip paid: {article.title}")
                index.append(article.to_dict())
                continue

            self._fetch_body(article)
            self._save_article(articles_dir, article)
            index.append(article.to_dict())
            self.progress(f"saved: {article.title}")
            time.sleep(self.sleep_seconds)

        self._write_json(self.output_dir / "index.json", index)
        self.progress(f"done: {len(index)} articles -> {self.output_dir}")

        if self._owns_client:
            self.client.close()

        return {
            "creator": creator.to_dict(),
            "article_count": len(index),
            "output_dir": str(self.output_dir),
        }

    def _fetch_body(self, article: Article) -> None:
        try:
            detail = self.client.get_note(article.key)
        except Exception as exc:  # pragma: no cover - network paths
            logger.warning("failed to fetch %s: %s", article.key, exc)
            return
        article.attach_detail(detail)
        if article.body_html and "markdown" in self.formats:
            article.body_markdown = self._md.handle(article.body_html).strip()

    def _save_article(self, articles_dir: Path, article: Article) -> None:
        stem = article.filename_stem
        if "json" in self.formats:
            self._write_json(articles_dir / f"{stem}.json", article.to_dict())
        if "markdown" in self.formats and article.body_markdown:
            front = self._front_matter(article)
            (articles_dir / f"{stem}.md").write_text(
                front + article.body_markdown + "\n",
                encoding="utf-8",
            )
        if "html" in self.formats and article.body_html:
            (articles_dir / f"{stem}.html").write_text(
                article.body_html, encoding="utf-8"
            )

    @staticmethod
    def _front_matter(article: Article) -> str:
        meta = {
            "title": article.title,
            "url": article.url,
            "publish_at": article.publish_at,
            "like_count": article.like_count,
            "key": article.key,
        }
        lines = ["---"]
        for k, v in meta.items():
            if v is None:
                continue
            lines.append(f'{k}: {json.dumps(v, ensure_ascii=False)}')
        lines.append("---\n\n")
        lines.append(f"# {article.title}\n\n")
        return "\n".join(lines)

    @staticmethod
    def _write_json(path: Path, data: object) -> None:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
