from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

from .crawler import Crawler

URL_RE = re.compile(r"note\.com/([^/?#]+)")


def _resolve_urlname(target: str) -> str:
    target = target.strip()
    if target.startswith("@"):
        return target[1:]
    m = URL_RE.search(target)
    if m:
        return m.group(1)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="note-crawl",
        description="Crawl all articles from a note.com creator.",
    )
    parser.add_argument(
        "target",
        help="creator urlname, @handle, or note.com profile URL",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="output directory (default: ./out/<urlname>)",
    )
    parser.add_argument(
        "--format",
        default="json,markdown",
        help="comma-separated formats: json,markdown,html (default: json,markdown)",
    )
    parser.add_argument(
        "--include-paid",
        action="store_true",
        help="also save metadata for paid (preview-only) notes",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="seconds to wait between article fetches (default: 1.0)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    urlname = _resolve_urlname(args.target)
    output = Path(args.output) if args.output else Path("out") / urlname
    formats = [f.strip() for f in args.format.split(",") if f.strip()]

    crawler = Crawler(
        urlname=urlname,
        output_dir=output,
        sleep_seconds=args.sleep,
        include_paid=args.include_paid,
        formats=formats,
        progress=lambda msg: print(msg, flush=True),
    )
    summary = crawler.run()
    print(f"\n{summary['article_count']} articles saved to {summary['output_dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
