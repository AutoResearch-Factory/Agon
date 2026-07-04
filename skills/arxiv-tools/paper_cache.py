"""论文元数据 SQLite 缓存"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = Path(os.environ.get("ARXIV_CACHE_DIR", Path(__file__).parent / ".arxiv"))
DB_PATH = CACHE_DIR / "paper_cache.db"
CACHE_TTL_DAYS = 7

_CREATE_TABLE_SQL = """\
CREATE TABLE IF NOT EXISTS papers (
    arxiv_id   TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    authors    TEXT NOT NULL,
    abstract   TEXT NOT NULL DEFAULT '',
    categories TEXT NOT NULL DEFAULT '[]',
    pdf_url    TEXT NOT NULL DEFAULT '',
    bibtex     TEXT NOT NULL,
    cached_at  TEXT NOT NULL
)"""


@dataclass
class CachedAuthor:
    name: str


@dataclass
class CachedPaper:
    title: str
    authors: list[CachedAuthor]
    abstract: str = ""
    categories: list[str] = field(default_factory=list)
    pdf_url: str = ""


def _migrate(conn: sqlite3.Connection) -> None:
    """Migrate old schema"""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(papers)")}
    if not cols:
        return
    if "summary" in cols and "abstract" not in cols:
        conn.execute("ALTER TABLE papers RENAME COLUMN summary TO abstract")
    if "published" in cols:
        conn.execute("ALTER TABLE papers DROP COLUMN published")
    if "updated" in cols:
        conn.execute("ALTER TABLE papers DROP COLUMN updated")


def _get_conn() -> sqlite3.Connection:
    CACHE_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(_CREATE_TABLE_SQL)
    _migrate(conn)
    return conn


def _id_variants(arxiv_id: str) -> tuple[str, ...]:
    """返回 clean id 和 arxiv: 前缀两种形式, 用于兼容查询."""
    if arxiv_id.startswith("arxiv:"):
        return (arxiv_id, arxiv_id[len("arxiv:"):])
    return (arxiv_id, f"arxiv:{arxiv_id}")


def get_cached_paper(arxiv_id: str) -> CachedPaper | None:
    conn = _get_conn()
    try:
        variants = _id_variants(arxiv_id)
        row = conn.execute(
            "SELECT title, authors, abstract, categories, pdf_url, cached_at"
            " FROM papers WHERE arxiv_id IN (?, ?)",
            variants,
        ).fetchone()
        if row is None:
            return None
        title, authors_json, abstract, categories_json, pdf_url, cached_at = row
        if CACHE_TTL_DAYS > 0:
            try:
                cached_dt = datetime.fromisoformat(cached_at)
                if datetime.now() - cached_dt > timedelta(days=CACHE_TTL_DAYS):
                    return None
            except (ValueError, TypeError):
                pass
        return CachedPaper(
            title=title,
            authors=[CachedAuthor(name) for name in json.loads(authors_json)],
            abstract=abstract,
            categories=json.loads(categories_json),
            pdf_url=pdf_url,
        )
    finally:
        conn.close()


def cache_paper(arxiv_id: str, paper: CachedPaper, bibtex: str) -> None:
    conn = _get_conn()
    try:
        with conn:
            date_suffix = datetime.now().strftime("%y%m%d")
            variants = _id_variants(arxiv_id)
            existing = conn.execute(
                "SELECT arxiv_id FROM papers WHERE arxiv_id IN (?, ?)",
                variants,
            ).fetchone()
            if existing:
                old_id = existing[0]
                archive_id = f"{old_id}_{date_suffix}"
                already_archived = conn.execute(
                    "SELECT 1 FROM papers WHERE arxiv_id = ?", (archive_id,),
                ).fetchone()
                if not already_archived:
                    conn.execute(
                        "UPDATE papers SET arxiv_id = ? WHERE arxiv_id = ?",
                        (archive_id, old_id),
                    )
                else:
                    conn.execute(
                        "DELETE FROM papers WHERE arxiv_id = ?", (old_id,),
                    )
            conn.execute(
                """INSERT INTO papers
                   (arxiv_id, title, authors, abstract, categories, pdf_url, bibtex, cached_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    arxiv_id,
                    paper.title,
                    json.dumps([a.name for a in paper.authors]),
                    paper.abstract,
                    json.dumps(paper.categories),
                    paper.pdf_url,
                    bibtex,
                    datetime.now().isoformat(),
                ),
            )
    finally:
        conn.close()


def get_cached_bibtex(arxiv_id: str) -> str | None:
    conn = _get_conn()
    try:
        variants = _id_variants(arxiv_id)
        row = conn.execute(
            "SELECT bibtex FROM papers WHERE arxiv_id IN (?, ?)",
            variants,
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()
