<div align="center">

# 📝 note-crawler

**Archive every article from a [note.com](https://note.com) creator — in one command.**

A tiny, dependency-light Python toolkit that turns any creator page into a clean, offline-readable corpus of JSON + Markdown.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](#-license)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)
[![Made with httpx](https://img.shields.io/badge/built%20with-httpx-005571.svg)](https://www.python-httpx.org/)

```bash
$ note-crawl ishida_yuko
creator: 石田裕子（サイバーエージェント専務執行役員） notes=126
saved: 継続することの難しさと意義について…
saved: 「働きがい」と「経済成長」は両立できるのか。…
... (124 more) ...
done: 126 articles -> out/ishida_yuko
```

</div>

---

## ✨ Features

- 🔓 **No login required** — uses note.com's public JSON endpoints only
- 📚 **Full body text** — grabs the complete article HTML, not just previews
- 🧾 **Multi-format output** — JSON, Markdown (with YAML front-matter), and raw HTML
- 🔁 **Resilient by default** — exponential backoff, configurable rate limit, automatic pagination
- 🧩 **Library + CLI** — drop into a notebook, a script, or your shell
- 🪶 **Tiny footprint** — three runtime deps (`httpx`, `html2text`, `tenacity`)
- 🧪 **Tested** — typed dataclasses, deterministic filename layout, unit-tested core

---

## 🚀 Quickstart

### 1. Install

```bash
git clone <this-repo>
cd note-crawler
pip install -e .
```

> Need dev tooling? `pip install -e ".[dev]"`

### 2. Crawl

```bash
note-crawl ishida_yuko                       # urlname
note-crawl @ishida_yuko                      # @handle
note-crawl https://note.com/ishida_yuko      # full URL
```

### 3. Read

```bash
$ tree out/ishida_yuko -L 2
out/ishida_yuko
├── creator.json
├── index.json
└── articles
    ├── 2025-10-24_継続することの難しさ…_n195aa4cc08c5.json
    ├── 2025-10-24_継続することの難しさ…_n195aa4cc08c5.md
    └── …
```

Every Markdown file ships with YAML front-matter, ready for Obsidian, MkDocs, Hugo, or your favourite RAG pipeline:

```markdown
---
title: "継続することの難しさと意義について…"
url: "https://note.com/ishida_yuko/n/n195aa4cc08c5"
publish_at: "2025-10-24T11:46:58+09:00"
like_count: 48
key: "n195aa4cc08c5"
---

# 継続することの難しさと意義について…

皆さん、こんにちは。5年にわたってnoteで発信を…
```

---

## 🛠 CLI Reference

```
note-crawl <target> [options]
```

| Option              | Default            | Description                                                  |
| ------------------- | ------------------ | ------------------------------------------------------------ |
| `-o, --output DIR`  | `out/<urlname>`    | Where to write the corpus                                    |
| `--format`          | `json,markdown`    | Comma-separated subset of `json` / `markdown` / `html`       |
| `--include-paid`    | `off`              | Save metadata for paid notes (bodies stay preview-only)      |
| `--sleep SEC`       | `1.0`              | Delay between article fetches — be a good citizen            |
| `-v, --verbose`     | `off`              | DEBUG-level logging                                          |

---

## 🐍 Python API

### High-level

```python
from note_crawler import Crawler

summary = Crawler(
    urlname="ishida_yuko",
    output_dir="out/ishida_yuko",
    formats=["json", "markdown"],
    sleep_seconds=1.0,
).run()

print(summary)
# {'creator': {...}, 'article_count': 126, 'output_dir': 'out/ishida_yuko'}
```

### Low-level

Stream raw API payloads — perfect for ad-hoc analysis:

```python
from note_crawler import NoteClient

with NoteClient() as client:
    creator = client.get_creator("ishida_yuko")

    for item in client.iter_creator_contents("ishida_yuko"):
        detail = client.get_note(item["key"])
        body = detail["data"]["body"] or ""
        print(f"{item['name']:60s}  {len(body):>6,} chars")
```

---

## 🏗 How it works

```
┌──────────────┐    GET /api/v2/creators/{urlname}
│   Crawler    │ ─────────────────────────────────► Creator profile
│              │
│              │    GET /api/v2/creators/{urlname}/contents?page=N
│              │ ─────────────────────────────────► Paginated index
│              │
│              │    GET /api/v3/notes/{key}
│              │ ─────────────────────────────────► Full article body
└──────┬───────┘
       │
       ▼
  out/<urlname>/{creator.json, index.json, articles/*.{json,md,html}}
```

Three public endpoints, three responsibilities. No scraping, no headless browser, no auth.

---

## ⚖️ Be a good citizen

- 🤝 Respect note.com's [Terms of Service](https://note.com/terms) and `robots.txt`.
- 🐢 Don't crank `--sleep` to zero. The default 1 s/article is intentionally polite.
- 💰 Paid notes return preview-only bodies via the API — by design. `--include-paid` saves the metadata anyway.
- 📰 Need magazines, likes, or comments? `NoteClient.list_creator_contents(kind=...)` accepts other `kind` values.

---

## 🗺 Roadmap

- [ ] Resume / incremental sync (skip already-downloaded `key`s)
- [ ] Image asset download (`eyecatch` + inline images)
- [ ] Magazine + circle support out of the box
- [ ] Async crawler (`httpx.AsyncClient` + bounded concurrency)
- [ ] Publish to PyPI

PRs and issues welcome — see below.

---

## 🤝 Contributing

```bash
pip install -e ".[dev]"
pytest -q
```

Then open a PR. Small, focused changes are easiest to land.

---

## 📜 License

[MIT](LICENSE) © note-crawler contributors

<div align="center">
<sub>Built with ❤️ for archivists, researchers, and anyone who believes good writing deserves to outlive a webpage.</sub>
</div>
