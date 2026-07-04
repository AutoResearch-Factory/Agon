#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "arxiv",
#     "json5",
#     "pymupdf",
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
arXiv 论文搜索与全文获取工具

功能：
1. search - 搜索论文（关键词、标题、摘要）
2. info - 获取论文信息（标题、作者、摘要等，不下载）
3. bib - 生成 BibTeX 引用（自动生成 citation key）
4. tex - 下载 LaTeX 源文件并解压（失败时自动 fallback 到 PDF 下载）
5. cited - 被引反查（Semantic Scholar 首选，OpenAlex 备选）
6. references - 正引查询：查看该论文引用了哪些论文（Semantic Scholar）
7. infotex - info + tex 组合：先打印论文信息，再下载 LaTeX

使用方法（通过 uv run）：
    uv run arxiv_tool.py search "PINN" --max 5
    uv run arxiv_tool.py info 2401.12345
    uv run arxiv_tool.py bib 2401.12345 -o refs.bib
    uv run arxiv_tool.py tex 2401.12345
    uv run arxiv_tool.py infotex 2401.12345
    uv run arxiv_tool.py cited 1711.10561 --max 20
    uv run arxiv_tool.py cited 1711.10561 --offset 20  # 翻页
    uv run arxiv_tool.py cited 1711.10561 --source openalex
    uv run arxiv_tool.py references 1711.10561 --max 20
"""

from __future__ import annotations

import argparse
import fcntl
import gzip
import io
import json
import os
import re
import shutil
import sys
import tarfile
import time
from pathlib import Path
import arxiv
import fitz  # PyMuPDF
import json5
import requests
from dotenv import load_dotenv

from datetime import date as _date
from datetime import datetime as _datetime
from datetime import timedelta as _timedelta

from paper_cache import CACHE_TTL_DAYS, CachedAuthor, CachedPaper, cache_paper, get_cached_bibtex, get_cached_paper

SCRIPT_DIR = Path(__file__).parent
# 缓存目录：优先读 ARXIV_CACHE_DIR 环境变量，默认在脚本同目录下 .arxiv/
CACHE_DIR = Path(os.environ.get("ARXIV_CACHE_DIR", SCRIPT_DIR / ".arxiv"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 从缓存目录加载 .env，这样共享缓存的用户自动共享 API key
load_dotenv(CACHE_DIR / ".env", override=False)

# API Keys（有就用，没有也不影响基本功能）
S2_API_KEY: str | None = os.environ.get("S2_API_KEY")
OPENALEX_API_KEY: str | None = os.environ.get("OPENALEX_API_KEY")
CONTACT_EMAIL: str = os.environ.get("CONTACT_EMAIL", "")

# API 基础 URL
S2_API_BASE = "https://api.semanticscholar.org/graph/v1"
OPENALEX_API_BASE = "https://api.openalex.org"

# Feature flag: OpenAlex 上游 metadata 污染 (e.g. arXiv:2001.08361 Kaplan Scaling Laws 的 abstract
# 被替换成 LLM-生成的 agentic AI theory 段落; title/authors 正确 但 abstract swap). 背景见
# 2024 年 Crossref fabricated-metadata 事件, Springer/Elsevier 2025 从 OpenAlex 撤 abstract,
# ICLR 2026 20% submissions 含 AI 幻觉 citation. S2 和 arXiv 干净.
# 暂时 disable, 所有 fetch/search/cited 入口早 return None 走 fallback. 代码/token 保留.
OPENALEX_ENABLED = False

# Audit log: append one JSONL line per CLI invocation to CACHE_DIR/.audit.jsonl.
# 共享文件, 多进程安全 (append on POSIX is atomic for <4KB, single JSON line 远小于此).
# 用于回答诸如 "tex vs info 比例" / "search 关键词 top-N" / "cited 有没有人用" 之类统计.
AUDIT_LOG = CACHE_DIR / ".audit.jsonl"

# 模块级 var: 每个 fetch/search/cited 成功路径把自己的来源标签写进来,
# main() 的 audit wrapper 读取后写进 log 的 source_hit 字段.
_LAST_SOURCE: str = "unknown"


def _set_source(src: str) -> None:
    """Fetcher 成功返回前 call 这个函数打标, audit wrapper 最后读."""
    global _LAST_SOURCE
    _LAST_SOURCE = src


def _write_audit_entry(entry: dict) -> None:
    """Append 一行 JSON 到 AUDIT_LOG. 失败静默, 不让 audit 打断工具主流程."""
    try:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass

# HTTP 请求头（arXiv 推荐设置 User-Agent）
_mailto = f" (mailto:{CONTACT_EMAIL})" if CONTACT_EMAIL else ""
HTTP_HEADERS = {
    "User-Agent": f"arxiv-tool/1.0{_mailto}",
}

OUTPUT_DIR = CACHE_DIR

_RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
_MIN_PDF_BYTES = 10_240  # 10 KB — 小于此值大概率是错误页面而非 PDF


def _brief_error(e: requests.RequestException) -> str:
    """从 RequestException 中提取简短错误信息，不打印完整 URL"""
    if isinstance(e, requests.HTTPError) and e.response is not None:
        return f"HTTP {e.response.status_code}"
    return type(e).__name__


def _request_with_retry(method, url, *, service: str, **kwargs) -> requests.Response:
    """带限流和指数退避重试的 HTTP 请求

    自动调用 RateLimiter.acquire() 限流，429/5xx 时按 backoff() 指数退避。
    """
    last_err: requests.RequestException | None = None
    for attempt in range(RateLimiter.RETRIES + 1):
        RateLimiter.acquire(service)
        try:
            resp = method(url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            retryable = (
                e.response is not None
                and e.response.status_code in _RETRYABLE_STATUS_CODES
            )
            if not retryable or attempt >= RateLimiter.RETRIES:
                raise
            msg = f"HTTP {e.response.status_code}"  # type: ignore[union-attr]
            last_err = e
        except requests.ConnectionError as e:
            if attempt >= RateLimiter.RETRIES:
                raise
            msg = "Connection error"
            last_err = e
        wait = RateLimiter.backoff(service, attempt)
        print(f"{msg}, {wait:.0f}s后重试...", file=sys.stderr)
        time.sleep(wait)
    raise last_err  # type: ignore[misc]


class RateLimiter:
    """跨进程 rate limit 管理，用 json5 lock 文件实现

    所有限流和重试参数统一在此管理：
    - INTERVALS: 各服务最小请求间隔（秒）
    - RETRIES: 最大重试次数
    - backoff(): 指数退避 = INTERVALS[service] * 2^attempt
    """

    LOCK_FILE = CACHE_DIR / ".ratelimit.lock"
    RETRIES = 3
    INTERVALS = {
        "s2": 2.0,  # Semantic Scholar: 1 req/s，用 2s 间隔留余量
        "arxiv": 5.0,  # arXiv 官方 API，限流严格
        "openalex": 0.1,  # OpenAlex 宽松
        "ut": 0.3,  # 测试用
    }

    @classmethod
    def backoff(cls, service: str, attempt: int) -> float:
        """指数退避秒数: interval * 2^attempt"""
        return cls.INTERVALS[service] * (2 ** attempt)

    @classmethod
    def acquire(cls, service: str) -> None:
        """原子地等待限流窗口并记录请求时间。

        在检查和写入期间持有排他文件锁，防止并行进程同时通过限流检查。
        """
        interval = cls.INTERVALS[service]
        for _ in range(5):
            with open(cls.LOCK_FILE, "a+") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.seek(0)
                content = f.read()
                try:
                    lock = json5.loads(content) if content.strip() else {}
                except ValueError:
                    lock = {}

                remaining = 0.0
                if service in lock:
                    remaining = interval - (time.time() - lock[service])

                if remaining <= 0:
                    lock[service] = time.time()
                    f.seek(0)
                    f.truncate()
                    f.write(json5.dumps(lock))
                    f.flush()
                    os.fsync(f.fileno())
                    return
            # 锁已释放，等待剩余时间后重试
            time.sleep(remaining)
        raise RuntimeError(
            f"RateLimiter: {service} failed to acquire request window after 5 attempts"
        )


def _fetch_paper_s2(arxiv_id: str) -> CachedPaper | None:
    """Fetch paper metadata from Semantic Scholar"""
    url = f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}"
    try:
        resp = _request_with_retry(
            requests.get, url, service="s2",
            params={"fields": "title,authors,abstract"},
            headers=_s2_headers(),
            timeout=15,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"S2 lookup failed: {_brief_error(e)}", file=sys.stderr)
        return None

    if not data.get("title") or not data.get("authors"):
        return None

    published = _arxiv_date(arxiv_id)
    if not published:
        return None

    return CachedPaper(
        title=data["title"],
        authors=[CachedAuthor(a["name"]) for a in data["authors"]],
        abstract=data.get("abstract") or "",
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
    )


def _fetch_paper_openalex(arxiv_id: str) -> CachedPaper | None:
    """Fetch paper metadata from OpenAlex"""
    if not OPENALEX_ENABLED:
        return None
    doi = f"10.48550/arXiv.{arxiv_id}"
    url = f"{OPENALEX_API_BASE}/works/doi:{doi}"
    try:
        resp = _request_with_retry(
            requests.get, url, service="openalex",
            params=_openalex_params(
                select="title,authorships,abstract_inverted_index",
            ),
            timeout=15,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"OpenAlex lookup failed: {_brief_error(e)}", file=sys.stderr)
        return None

    if not data.get("title"):
        return None

    authorships = data.get("authorships") or []
    authors = [CachedAuthor(a["author"]["display_name"]) for a in authorships]
    if not authors:
        return None

    abstract = _reconstruct_abstract(data.get("abstract_inverted_index")) or ""

    return CachedPaper(
        title=data["title"],
        authors=authors,
        abstract=abstract,
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
    )


def _fetch_paper_arxiv(arxiv_id: str) -> CachedPaper | None:
    """Fetch paper metadata from arXiv API (slowest, used as last resort)"""
    client = arxiv.Client(num_retries=0)
    search = arxiv.Search(id_list=[arxiv_id])
    results = None
    for attempt in range(RateLimiter.RETRIES + 1):
        RateLimiter.acquire("arxiv")
        try:
            results = list(client.results(search))
            break
        except arxiv.HTTPError:
            if attempt < RateLimiter.RETRIES:
                wait = RateLimiter.backoff("arxiv", attempt)
                print(f"arXiv 429, {wait:.0f}s后重试...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
    if not results:
        return None

    paper = results[0]
    return CachedPaper(
        title=paper.title,
        authors=[CachedAuthor(a.name) for a in paper.authors],
        abstract=paper.summary,
        categories=list(paper.categories),
        pdf_url=paper.pdf_url,
    )


def get_paper_info(arxiv_id: str, *, force_refresh: bool = False) -> CachedPaper | None:
    clean_id = extract_arxiv_id(arxiv_id)

    if not force_refresh:
        cached = get_cached_paper(clean_id)
        if cached:
            _set_source("cache")
            return cached

    paper = None
    for name, fetcher in (
        ("openalex", _fetch_paper_openalex),
        ("s2", _fetch_paper_s2),
        ("arxiv", _fetch_paper_arxiv),
    ):
        paper = fetcher(clean_id)
        if paper:
            _set_source(name)
            break

    if not paper:
        print(f"Paper not found: {clean_id}", file=sys.stderr)
        return None

    bibtex = generate_bibtex(paper, clean_id)
    cache_paper(clean_id, paper, bibtex)
    return paper


def sanitize_filename(name: str, max_length: int = 80) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"\s+", "_", name)
    if len(name) > max_length:
        name = name[:max_length]
    return name.strip("._")


def extract_arxiv_id(input_str: str) -> str:
    """从输入中提取 arXiv ID

    支持格式：
    - 2401.12345
    - arXiv:2401.12345
    - https://arxiv.org/abs/2401.12345
    - https://arxiv.org/pdf/2401.12345.pdf
    """
    patterns = [
        r"(\d{4}\.\d{4,5}(?:v\d+)?)",  # 新格式: 2401.12345 或 2401.12345v1
        r"([a-z-]+/\d{7})",  # 旧格式: cs/0401001
    ]
    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            return match.group(1)
    return input_str


def search_papers(query: str, max_results: int = 20) -> list[Result]:
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)
    return list(client.results(search))


def _truncate_authors(names: list[str], limit: int = 3) -> str:
    """将作者名列表截断为 'A, B, C...' 格式"""
    result = ", ".join(names[:limit])
    if len(names) > limit:
        result += "..."
    return result


def _normalize_s2_search(results: list[dict]) -> list[dict]:
    out = []
    for paper in results:
        ext_ids = paper["externalIds"] or {}
        arxiv_id = ext_ids.get("ArXiv", "")
        doi = ext_ids.get("DOI", "")
        if arxiv_id:
            id_str = f"arXiv:{arxiv_id}"
        elif doi:
            id_str = f"DOI:{doi}"
        else:
            id_str = ""

        authors = paper["authors"] or []
        author_str = _truncate_authors([a["name"] for a in authors])

        out.append(
            {
                "id": id_str,
                "title": paper["title"],
                "authors": author_str,
                "year": str(paper["year"] or "?"),
                "cited_by": paper["citationCount"],
                "abstract": paper["abstract"],
            }
        )
    return out


def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
    """从 OpenAlex 的 abstract_inverted_index 还原摘要原文"""
    if not inverted_index:
        return None
    words: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            words.append((pos, word))
    words.sort()
    return " ".join(w for _, w in words)


def _normalize_openalex_search(results: list[dict]) -> list[dict]:
    out = []
    for work in results:
        authorships = work["authorships"] or []
        author_str = _truncate_authors(
            [a["author"]["display_name"] for a in authorships]
        )

        ids = work["ids"] or {}
        arxiv_str = ""
        for key, val in ids.items():
            if "arxiv" in key.lower() and val:
                arxiv_str = val.replace("https://arxiv.org/abs/", "arXiv:")
                break
        if not arxiv_str:
            doi = ids.get("doi", "")
            if "arxiv." in doi.lower():
                # DOI 形如 https://doi.org/10.48550/arxiv.1706.03762
                arxiv_str = "arXiv:" + doi.rsplit("arxiv.", 1)[-1]
        id_str = arxiv_str or ids.get("doi", "") or ids.get("openalex", "")

        out.append(
            {
                "id": id_str,
                "title": work["title"],
                "authors": author_str,
                "year": str(work["publication_year"] or "?"),
                "cited_by": work["cited_by_count"],
                "abstract": _reconstruct_abstract(work.get("abstract_inverted_index")),
            }
        )
    return out


def _normalize_arxiv_search(results: list) -> list[dict]:
    out = []
    for paper in results:
        arxiv_id = paper.entry_id.split("/abs/")[-1]
        author_str = _truncate_authors([a.name for a in paper.authors])

        out.append(
            {
                "id": f"arXiv:{arxiv_id}",
                "title": paper.title,
                "authors": author_str,
                "year": paper.published.strftime("%Y-%m-%d"),
                "cited_by": None,
                "abstract": paper.summary,
            }
        )
    return out


def _print_search_results(results: list[dict]) -> None:
    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['id']}")
        print(f"    Title: {r['title']}")
        print(f"    Authors: {r['authors']}")
        cited = f"  Cited: {r['cited_by']}" if r["cited_by"] is not None else ""
        print(f"    Year: {r['year']}{cited}")
        if r["abstract"]:
            print(f"    Abstract: {r['abstract'].replace(chr(10), ' ')}")
        print()


def _s2_filters_from_args(args) -> dict:
    """从 CLI args 提取 S2 过滤参数"""
    filters = {}
    if getattr(args, "year", None):
        filters["year"] = args.year
    if getattr(args, "fields_of_study", None):
        filters["fields_of_study"] = args.fields_of_study
    if getattr(args, "pub_types", None):
        filters["publication_types"] = args.pub_types
    if getattr(args, "min_citations", None) is not None:
        filters["min_citations"] = args.min_citations
    if getattr(args, "venue", None):
        filters["venue"] = args.venue
    if getattr(args, "open_access", False):
        filters["open_access"] = True
    return filters


def cmd_search(args):
    source = args.source
    if source == "openalex" and not OPENALEX_ENABLED:
        print(
            "OpenAlex 源已被禁用 (上游 metadata 污染). "
            "请改用 --source s2 / --source arxiv, 或省略 --source 走自动选择.",
            file=sys.stderr,
        )
        sys.exit(2)
    filters = _s2_filters_from_args(args)

    results = None

    if source in ("s2", "auto"):
        if getattr(args, "bulk", False):
            print("Searching Semantic Scholar (bulk)...", file=sys.stderr)
            sort = getattr(args, "sort", None)
            token = getattr(args, "token", None)
            ret = _search_s2_bulk(args.query, args.max, token=token, sort=sort, **filters)
            if ret:
                raw, next_token = ret
                results = ("Semantic Scholar (bulk)", _normalize_s2_search(raw))
                if next_token:
                    print(f"\nNext page token: {next_token}", file=sys.stderr)
        else:
            print("Searching Semantic Scholar...", file=sys.stderr)
            raw = _search_s2(args.query, args.max, **filters)
            if raw:
                results = ("Semantic Scholar", _normalize_s2_search(raw))

    if not results and source in ("openalex", "auto") and OPENALEX_ENABLED:
        print("Searching OpenAlex...", file=sys.stderr)
        raw = _search_openalex(args.query, args.max)
        if raw:
            results = ("OpenAlex", _normalize_openalex_search(raw))

    if not results and source in ("arxiv", "auto"):
        if source == "auto":
            print(
                "⚠ S2 and OpenAlex both failed, falling back to arXiv API. "
                "If this keeps happening, check API keys and network.",
                file=sys.stderr,
            )
        print("Searching arXiv...", file=sys.stderr)
        raw = search_papers(args.query, args.max)
        if raw:
            results = ("arXiv", _normalize_arxiv_search(raw))

    if not results:
        print("No results from any source")
        return

    source_name, normalized = results
    # Audit tag: 取 source_name 首单词 (e.g. "Semantic Scholar (bulk)" -> "semantic", "arXiv" -> "arxiv")
    _set_source(source_name.split()[0].lower())
    print(f"\nFound {len(normalized)} papers ({source_name}):\n")
    _print_search_results(normalized)


def _fetch_pdf_fallback(arxiv_id: str, output_dir: Path) -> None:
    """tex 失败后的备选：下载 PDF 并提取文本"""
    output_dir.mkdir(parents=True, exist_ok=True)

    clean_id = extract_arxiv_id(arxiv_id)
    file_id = clean_id.replace("/", "_")
    txt_file = output_dir / f"{file_id}.txt"
    pdf_file = output_dir / f"{file_id}.pdf"

    if txt_file.exists():
        print(f"Already exists: {txt_file}")
        return

    pdf_url = f"https://arxiv.org/pdf/{clean_id}"
    print(f"Downloading PDF: {pdf_url}")
    response = _request_with_retry(requests.get, pdf_url, service="arxiv", headers=HTTP_HEADERS, timeout=60)
    if len(response.content) < _MIN_PDF_BYTES:
        print(f"Downloaded file only {len(response.content)} bytes, likely not a valid PDF", file=sys.stderr)
        return
    pdf_file.write_bytes(response.content)

    try:
        print("Extracting text...")
        doc = fitz.open(pdf_file)
        text = "\n".join(page.get_text().strip() for page in doc)
        doc.close()
    except Exception:
        pdf_file.unlink(missing_ok=True)
        raise

    txt_file.write_text(
        f"# arXiv:{clean_id}\n\nURL: https://arxiv.org/abs/{clean_id}\n\n## Full Text\n\n{text}",
        encoding="utf-8",
    )
    print(f"Saved PDF: {pdf_file}")
    print(f"Saved TXT: {txt_file}")


def cmd_info(args):
    clean_id = extract_arxiv_id(args.arxiv_id)
    refresh = getattr(args, "refresh", False)

    paper = get_paper_info(clean_id, force_refresh=refresh)
    if not paper:
        return

    arxiv_date = _arxiv_date(clean_id)
    date_str = arxiv_date.strftime("%Y-%m") if arxiv_date else "?"

    print(f"arXiv ID: {clean_id}")
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(a.name for a in paper.authors)}")
    print(f"Published: {date_str}")
    if paper.categories:
        print(f"Categories: {', '.join(paper.categories)}")
    print(f"PDF: {paper.pdf_url}")
    cached_tex = _find_cached_tex_dir(clean_id)
    if cached_tex:
        print(f"Tex (cached): {cached_tex}")
    print(f"\nAbstract:\n{paper.abstract}")


# 停用词列表，用于生成 citation key
STOPWORDS = {
    "a",
    "an",
    "the",
    "of",
    "for",
    "and",
    "or",
    "in",
    "on",
    "at",
    "to",
    "with",
    "by",
    "from",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "need",
    "dare",
    "ought",
    "used",
    "via",
    "using",
    "based",
    "towards",
    "toward",
}


def _arxiv_year(arxiv_id: str) -> int | None:
    """从 arXiv ID 提取提交年份（最权威的来源）

    新格式 YYMM.XXXXX → 20YY；旧格式 subject/YYMMNNN → 19YY/20YY
    """
    d = _arxiv_date(arxiv_id)
    return d.year if d else None


def _arxiv_date(arxiv_id: str) -> _datetime | None:
    """从 arXiv ID 提取提交年月 → YYYY-MM-01"""
    m = re.match(r"(\d{2})(\d{2})\.\d+", arxiv_id)
    if not m:
        m = re.match(r"[a-z-]+/(\d{2})(\d{2})\d{3}", arxiv_id)
    if not m:
        return None
    yy, mm = int(m.group(1)), int(m.group(2))
    if not 1 <= mm <= 12:
        return None
    year = 1900 + yy if yy >= 91 else 2000 + yy
    return _datetime(year, mm, 1)


def generate_citation_key(paper, arxiv_id: str) -> str:
    """生成 BibTeX citation key

    格式：{第一作者姓小写}{年份}{标题首个实词小写}
    示例：li2025codepde, raissi2017physics

    年份从 arXiv ID 提取，避免 OpenAlex 等返回期刊出版年。
    """
    last_name = re.sub(r"[^a-z]", "", paper.authors[0].name.split()[-1].lower())
    year = _arxiv_year(arxiv_id)

    title_words = re.findall(r"[a-zA-Z]+", paper.title)
    first_word = ""
    for word in title_words:
        if word.lower() not in STOPWORDS:
            first_word = word.lower()
            break

    return f"{last_name}{year}{first_word}"


def generate_bibtex(paper, arxiv_id: str) -> str:
    """生成 arXiv 标准格式的 BibTeX 条目"""
    citation_key = generate_citation_key(paper, arxiv_id)
    authors = " and ".join(a.name for a in paper.authors)
    clean_id = re.sub(r"v\d+$", "", arxiv_id)
    year = _arxiv_year(arxiv_id) or paper.published.year

    fields = [
        f"title={{{paper.title}}}",
        f"author={{{authors}}}",
        f"year={{{year}}}",
        f"eprint={{{clean_id}}}",
        "archivePrefix={arXiv}",
    ]
    if paper.categories:
        fields.append(f"primaryClass={{{paper.categories[0]}}}")
    fields.append(f"url={{https://arxiv.org/abs/{clean_id}}}")

    body = ",\n      ".join(fields)
    return f"@misc{{{citation_key},\n      {body},\n}}"


def cmd_bib(args):
    clean_id = extract_arxiv_id(args.arxiv_id)

    # get_paper_info 会在首次获取时缓存 bibtex
    paper = get_paper_info(clean_id)
    if not paper:
        sys.exit(1)

    bibtex = get_cached_bibtex(clean_id)
    if not bibtex:
        bibtex = generate_bibtex(paper, clean_id)

    if args.output:
        output_path = Path(args.output)
        mode = "a" if output_path.exists() else "w"
        with open(output_path, mode, encoding="utf-8") as f:
            if mode == "a" and output_path.stat().st_size > 0:
                f.write("\n\n")
            f.write(bibtex)
            f.write("\n")
        print(f"{'Appended' if mode == 'a' else 'Written'} to: {output_path}")
    else:
        print(bibtex)


def print_tree(
    directory: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0
) -> list[str]:
    lines = []
    if current_depth >= max_depth:
        return lines

    items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            extension = "    " if is_last else "│   "
            lines.extend(
                print_tree(item, prefix + extension, max_depth, current_depth + 1)
            )

    return lines


def _is_archived_tex_dir(name: str) -> bool:
    """名称以 __YYMMDD 结尾且为合法过去日期 → 归档目录"""
    m = re.search(r"__(\d{6})$", name)
    if not m:
        return False
    try:
        d = _datetime.strptime(m.group(1), "%y%m%d").date()
        return d <= _date.today()
    except ValueError:
        return False


def _find_cached_tex_dir(arxiv_id: str) -> Path | None:
    """返回已下载的 tex 解压目录路径; 没有则 None. 不发请求.

    优先精确 dir_id 命中, 退化到 dir_id_<title> glob (fetch_tex_source 解压后
    会把 title slug 加进目录名). 命名规则与 fetch_tex_source / cmd_tex 必须
    保持一致 — 三处共享此 helper. 跳过 __YYMMDD 归档目录.
    """
    clean_id = extract_arxiv_id(arxiv_id)
    dir_id = re.sub(r"v\d+$", "", clean_id).replace("/", "_")
    exact = OUTPUT_DIR / dir_id
    if exact.is_dir():
        return exact
    for p in OUTPUT_DIR.glob(f"{dir_id}_*"):
        if p.is_dir() and not _is_archived_tex_dir(p.name):
            return p
    return None


def fetch_tex_source(arxiv_id: str, output_dir: Path, *, force_refresh: bool = False) -> Path | None:
    """下载 arXiv LaTeX 源文件并解压

    不调用 API，直接从 e-print 下载源文件。目录名使用 arXiv ID，
    下载后尝试从 tex 文件中提取标题来补充目录名。

    Args:
        arxiv_id: arXiv ID
        output_dir: 输出目录
        force_refresh: 强制刷新（忽略 TTL）

    Returns:
        解压后的目录路径，失败返回 None
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    clean_id = extract_arxiv_id(arxiv_id)
    # 移除版本号用于目录名
    dir_id = re.sub(r"v\d+$", "", clean_id).replace("/", "_")
    target_dir = output_dir / dir_id

    def _check_and_maybe_archive(candidate: Path) -> Path | None:
        """TTL 内直接返回; 过期/force_refresh 则 rename 归档, 返回 None 触发重新下载."""
        try:
            mtime = candidate.stat().st_mtime
        except OSError:
            return candidate
        age = _datetime.now() - _datetime.fromtimestamp(mtime)
        if not force_refresh:
            if CACHE_TTL_DAYS <= 0:
                return candidate
            if age <= _timedelta(days=CACHE_TTL_DAYS):
                return candidate
        archive_suffix = _datetime.now().strftime("%y%m%d")
        archived_name = f"{candidate.name}__{archive_suffix}"
        archived_path = candidate.parent / archived_name
        reason = "--refresh" if force_refresh else f"expired ({age.days}d old)"
        print(f"Cache {reason}, archiving: {candidate.name} → {archived_name}")
        os.rename(candidate, archived_path)
        return None

    if target_dir.exists():
        result = _check_and_maybe_archive(target_dir)
        if result:
            print(f"Already exists: {result}")
            return result
    existing = [p for p in output_dir.glob(f"{dir_id}_*")
                if p.is_dir() and not _is_archived_tex_dir(p.name)]
    if existing:
        result = _check_and_maybe_archive(existing[0])
        if result:
            print(f"Already exists: {result}")
            return result

    source_url = f"https://arxiv.org/e-print/{clean_id}"
    print(f"Downloading source: {source_url}")

    try:
        response = _request_with_retry(requests.get, source_url, service="arxiv", headers=HTTP_HEADERS, timeout=60)
    except requests.RequestException as e:
        print(f"Download failed: {e}", file=sys.stderr)
        return None

    content = response.content

    target_dir.mkdir(parents=True, exist_ok=True)
    print("Extracting source...")
    try:
        _extract_source(content, target_dir)
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        shutil.rmtree(target_dir, ignore_errors=True)
        return None

    new_dir = _try_rename_with_title(target_dir, dir_id, output_dir)
    if new_dir:
        target_dir = new_dir

    print(f"Saved to: {target_dir}")
    return target_dir


def _extract_source(content: bytes, target_dir: Path) -> None:
    try:
        with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as tar:
            tar.extractall(target_dir, filter="data")
            print("Extracted as tar.gz")
            return
    except tarfile.ReadError:
        pass

    try:
        decompressed = gzip.decompress(content)
        # 解压后可能是 tar
        try:
            with tarfile.open(fileobj=io.BytesIO(decompressed), mode="r") as tar:
                tar.extractall(target_dir, filter="data")
                print("Extracted as gzip+tar")
                return
        except tarfile.ReadError:
            # 纯 gzip 压缩的单个文件
            tex_file = target_dir / "main.tex"
            tex_file.write_bytes(decompressed)
            print("Extracted as single tex file")
            return
    except gzip.BadGzipFile:
        pass

    try:
        with tarfile.open(fileobj=io.BytesIO(content), mode="r") as tar:
            tar.extractall(target_dir, filter="data")
            print("Extracted as tar")
            return
    except tarfile.ReadError:
        pass

    tex_file = target_dir / "main.tex"
    tex_file.write_bytes(content)
    print("Saved as single tex file (uncompressed)")


def _extract_braced_arg(text: str, start: int) -> str | None:
    """提取 text[start] 处 '{' 对应的完整花括号内容，支持嵌套"""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i]
    return None


def _strip_tex_comments(content: str) -> str:
    """移除 TeX 注释（% 开头的整行，以及行内未转义的 %）"""
    result = []
    for line in content.split("\n"):
        if line.lstrip().startswith("%"):
            continue
        result.append(re.sub(r"(?<!\\)%.*$", "", line))
    return "\n".join(result)


def _try_rename_with_title(
    target_dir: Path, dir_id: str, output_dir: Path
) -> Path | None:
    tex_files = list(target_dir.glob("*.tex"))
    if not tex_files:
        return None

    main_tex = next((f for f in tex_files if f.name == "main.tex"), tex_files[0])

    content = main_tex.read_text(encoding="utf-8", errors="ignore")
    content = _strip_tex_comments(content)
    match = re.search(r"\\title\s*\{", content)
    if not match:
        return None

    raw_title = _extract_braced_arg(content, match.end() - 1)
    if not raw_title:
        return None

    raw_title = re.sub(r"\\\\", " ", raw_title)
    raw_title = re.sub(r"\\[a-zA-Z]+\s*(\{[^}]*\})?", " ", raw_title)
    raw_title = re.sub(r"[{}]", "", raw_title)
    raw_title = re.sub(r"\s+", " ", raw_title).strip()
    if not raw_title:
        return None

    safe_title = sanitize_filename(raw_title, max_length=40)
    new_dir = output_dir / f"{dir_id}_{safe_title}"
    if new_dir.exists():
        return None

    target_dir.rename(new_dir)
    print(f"Renamed to: {new_dir.name}")
    return new_dir


def _s2_headers() -> dict[str, str]:
    if S2_API_KEY:
        return {**HTTP_HEADERS, "x-api-key": S2_API_KEY}
    return HTTP_HEADERS


def _s2_search_params(
    query: str,
    max_results: int,
    *,
    year: str | None = None,
    fields_of_study: str | None = None,
    publication_types: str | None = None,
    min_citations: int | None = None,
    venue: str | None = None,
    open_access: bool = False,
) -> dict:
    """构造 S2 搜索参数（search 和 bulk 共用）"""
    params: dict = {
        "query": query,
        "limit": min(max_results, 100),
        "fields": "title,year,authors,externalIds,citationCount,abstract",
    }
    if year:
        params["year"] = year
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study
    if publication_types:
        params["publicationTypes"] = publication_types
    if min_citations is not None:
        params["minCitationCount"] = str(min_citations)
    if venue:
        params["venue"] = venue
    if open_access:
        params["openAccessPdf"] = ""
    return params


def _search_s2(query: str, max_results: int = 10, **filters) -> list[dict] | None:
    """通过 Semantic Scholar 搜索论文

    Returns:
        论文列表 [{"title", "year", "authors", "externalIds", "citationCount", "abstract"}]，
        失败返回 None
    """
    params = _s2_search_params(query, max_results, **filters)
    try:
        resp = _request_with_retry(
            requests.get,
            f"{S2_API_BASE}/paper/search",
            service="s2",
            params=params,
            headers=_s2_headers(),
            timeout=30,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"Semantic Scholar search failed: {_brief_error(e)}", file=sys.stderr)
        return None

    if not data.get("data"):
        return None
    return data["data"][:max_results]


def _search_s2_bulk(
    query: str,
    max_results: int = 100,
    token: str | None = None,
    sort: str | None = None,
    **filters,
) -> tuple[list[dict], str | None] | None:
    """通过 Semantic Scholar bulk 搜索（token 分页，最多 1000 条）

    Returns:
        (论文列表, next_token)，失败返回 None
    """
    params = _s2_search_params(query, min(max_results, 1000), **filters)
    if token:
        params["token"] = token
    if sort:
        params["sort"] = sort
    try:
        resp = _request_with_retry(
            requests.get,
            f"{S2_API_BASE}/paper/search/bulk",
            service="s2",
            params=params,
            headers=_s2_headers(),
            timeout=30,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"Semantic Scholar bulk search failed: {_brief_error(e)}", file=sys.stderr)
        return None

    if not data.get("data"):
        return None
    return data["data"][:max_results], data.get("token")


def _search_openalex(query: str, max_results: int = 10) -> list[dict] | None:
    """通过 OpenAlex 搜索论文

    Returns:
        论文列表 [{"title", "publication_year", "authorships", "cited_by_count", "ids", ...}]，
        失败返回 None
    """
    if not OPENALEX_ENABLED:
        return None
    url = f"{OPENALEX_API_BASE}/works"
    try:
        resp = _request_with_retry(
            requests.get,
            url,
            service="openalex",
            params=_openalex_params(
                search=query,
                select="id,title,authorships,publication_year,cited_by_count,ids,abstract_inverted_index",
                per_page=str(min(max_results, 200)),
                sort="relevance_score:desc",
            ),
            timeout=30,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"OpenAlex search failed: {_brief_error(e)}", file=sys.stderr)
        return None

    if not data.get("results"):
        return None
    return data["results"][:max_results]


def _fetch_citations_s2(
    arxiv_id: str, max_results: int, offset: int = 0
) -> tuple[list[dict], int] | None:
    """从 Semantic Scholar 获取引用该论文的论文列表

    Returns:
        (引用论文列表, 总被引次数)，失败返回 None
    """
    info_url = f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}"
    try:
        resp = _request_with_retry(
            requests.get,
            info_url,
            service="s2",
            params={"fields": "title,citationCount"},
            headers=_s2_headers(),
            timeout=30,
        )
        paper_info = resp.json()
        print(f"Paper: {paper_info['title']}")
        print(f"Total citations: {paper_info['citationCount']}")
    except requests.RequestException as e:
        print(f"Semantic Scholar query failed: {_brief_error(e)}", file=sys.stderr)
        return None

    citations_url = f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}/citations"
    try:
        resp = _request_with_retry(
            requests.get,
            citations_url,
            service="s2",
            params={
                "fields": "title,year,externalIds,citationCount,authors",
                "offset": offset,
                "limit": min(max_results, 1000),
            },
            headers=_s2_headers(),
            timeout=30,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"Semantic Scholar citations fetch failed: {_brief_error(e)}", file=sys.stderr)
        return None

    results = [
        item["citingPaper"] for item in data["data"] if item["citingPaper"]["title"]
    ]
    return results[:max_results], paper_info["citationCount"]


def _fetch_references_s2(
    arxiv_id: str, max_results: int, offset: int = 0
) -> tuple[list[dict], int | None] | None:
    """从 Semantic Scholar 获取该论文引用的论文列表。

    Returns:
        (参考文献列表, 总参考文献数)，失败返回 None
    """
    info_url = f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}"
    total_references: int | None = None
    try:
        resp = _request_with_retry(
            requests.get,
            info_url,
            service="s2",
            params={"fields": "title,referenceCount"},
            headers=_s2_headers(),
            timeout=30,
        )
        paper_info = resp.json()
        print(f"Paper: {paper_info['title']}")
        total_references = paper_info.get("referenceCount")
        if total_references is not None:
            print(f"Total references: {total_references}")
    except requests.RequestException as e:
        print(f"Semantic Scholar query failed: {_brief_error(e)}", file=sys.stderr)
        return None

    references_url = f"{S2_API_BASE}/paper/ArXiv:{arxiv_id}/references"
    try:
        resp = _request_with_retry(
            requests.get,
            references_url,
            service="s2",
            params={
                "fields": "title,year,externalIds,citationCount,authors",
                "offset": offset,
                "limit": min(max_results, 1000),
            },
            headers=_s2_headers(),
            timeout=30,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"Semantic Scholar references fetch failed: {_brief_error(e)}", file=sys.stderr)
        return None

    results = [
        item["citedPaper"] for item in data["data"] if item["citedPaper"]["title"]
    ]
    return results[:max_results], total_references


def _openalex_params(**extra) -> dict[str, str]:
    if OPENALEX_API_KEY:
        extra["api_key"] = OPENALEX_API_KEY
    else:
        extra["mailto"] = CONTACT_EMAIL
    return extra


def _resolve_openalex_id(arxiv_id: str) -> tuple[str, str, int] | None:
    """通过 arXiv DOI 查找 OpenAlex work ID

    Returns:
        (openalex_work_id, 论文标题, 被引次数)，失败返回 None
    """
    if not OPENALEX_ENABLED:
        return None
    doi = f"10.48550/arXiv.{arxiv_id}"
    url = f"{OPENALEX_API_BASE}/works/doi:{doi}"
    try:
        resp = _request_with_retry(requests.get, url, service="openalex", params=_openalex_params(), timeout=15)
        data = resp.json()
        openalex_id = data["id"].split("/")[-1]  # "https://openalex.org/W123" -> "W123"
        return openalex_id, data["title"], data["cited_by_count"]
    except requests.RequestException:
        return None


def _fetch_citations_openalex(
    arxiv_id: str, max_results: int, offset: int = 0
) -> tuple[list[dict], int] | None:
    """从 OpenAlex 获取引用该论文的论文列表

    Returns:
        (引用论文列表, 总被引次数)，失败返回 None
    """
    if not OPENALEX_ENABLED:
        return None
    resolved = _resolve_openalex_id(arxiv_id)
    if not resolved:
        print("OpenAlex: paper not found", file=sys.stderr)
        return None

    work_id, title, total_citations = resolved
    print(f"Paper: {title}")
    print(f"Total citations: {total_citations}")

    # OpenAlex 用 page 分页，page 从 1 开始
    per_page = min(max_results, 200)
    page = (offset // per_page) + 1

    url = f"{OPENALEX_API_BASE}/works"
    try:
        resp = _request_with_retry(
            requests.get,
            url,
            service="openalex",
            params=_openalex_params(
                filter=f"cites:{work_id}",
                select="id,title,authorships,publication_year,cited_by_count",
                per_page=str(per_page),
                page=str(page),
                sort="cited_by_count:desc",
            ),
            timeout=30,
        )
        data = resp.json()
    except requests.RequestException as e:
        print(f"OpenAlex citations fetch failed: {_brief_error(e)}", file=sys.stderr)
        return None

    return data["results"][:max_results], total_citations


def _print_citations_s2(results: list[dict], start: int = 1) -> None:
    for i, paper in enumerate(results, start):
        ext_ids = paper["externalIds"] or {}
        arxiv_ext = ext_ids.get("ArXiv")
        arxiv_str = f"  arXiv:{arxiv_ext}" if arxiv_ext else ""

        authors = paper["authors"] or []
        author_str = _truncate_authors([a["name"] for a in authors])

        print(f"[{i}] {paper['title']}")
        print(f"    Authors: {author_str}")
        print(
            f"    Year: {paper['year'] or '?'}  Cited: {paper['citationCount']}{arxiv_str}"
        )
        print()


def _print_citations_openalex(results: list[dict], start: int = 1) -> None:
    for i, work in enumerate(results, start):
        authorships = work["authorships"] or []
        author_str = _truncate_authors(
            [a["author"]["display_name"] for a in authorships]
        )

        print(f"[{i}] {work['title']}")
        print(f"    Authors: {author_str}")
        print(
            f"    Year: {work['publication_year'] or '?'}  Cited: {work['cited_by_count']}"
        )
        print()


def cmd_cited(args):
    clean_id = extract_arxiv_id(args.arxiv_id)
    source = args.source
    if source == "openalex" and not OPENALEX_ENABLED:
        print(
            "OpenAlex 源已被禁用 (上游 metadata 污染). "
            "请改用 --source s2, 或省略 --source 走自动选择.",
            file=sys.stderr,
        )
        sys.exit(2)
    offset = args.offset
    results = None
    used_source = ""

    if source in ("s2", "auto"):
        print(f"Querying Semantic Scholar: ArXiv:{clean_id}")
        ret = _fetch_citations_s2(clean_id, args.max, offset)
        if ret is not None:
            results, _total = ret
            used_source = "Semantic Scholar"

    if results is None and source in ("openalex", "auto") and OPENALEX_ENABLED:
        if source == "auto":
            print("\nSemantic Scholar failed, switching to OpenAlex...")
        else:
            print(f"Querying OpenAlex: ArXiv:{clean_id}")
        ret = _fetch_citations_openalex(clean_id, args.max, offset)
        if ret is not None:
            results, _total = ret
            used_source = "OpenAlex"

    if not results:
        print(f"\nNo citations found for arXiv:{clean_id}")
        return

    # Audit tag: "Semantic Scholar" / "OpenAlex" -> first word lowercased
    _set_source(used_source.split()[0].lower())

    start_num = offset + 1
    end_num = offset + len(results)
    print(f"\nSource: {used_source}")
    print(f"Showing citations #{start_num}-{end_num}:\n")

    if used_source == "Semantic Scholar":
        _print_citations_s2(results, start_num)
    else:
        _print_citations_openalex(results, start_num)


def cmd_references(args):
    clean_id = extract_arxiv_id(args.arxiv_id)
    offset = args.offset

    print(f"Querying Semantic Scholar references: ArXiv:{clean_id}")
    ret = _fetch_references_s2(clean_id, args.max, offset)
    if ret is None:
        print(f"\nNo references found for arXiv:{clean_id}")
        return

    results, _total = ret
    if not results:
        print(f"\nNo references found for arXiv:{clean_id}")
        return

    _set_source("s2")

    start_num = offset + 1
    end_num = offset + len(results)
    print("\nSource: Semantic Scholar")
    print(f"Showing references #{start_num}-{end_num}:\n")
    _print_citations_s2(results, start_num)


def cmd_tex(args):
    refresh = getattr(args, "refresh", False)
    # Audit: 判断是否 cache hit (fetch_tex_source 前已存在目录).
    _was_cached = _find_cached_tex_dir(args.arxiv_id) is not None

    result = fetch_tex_source(args.arxiv_id, OUTPUT_DIR, force_refresh=refresh)
    if result:
        _set_source("cache" if _was_cached else "arxiv")
        print("\nDirectory structure:")
        print(result.name)
        tree_lines = print_tree(result)
        for line in tree_lines:
            print(line)
    else:
        _set_source("pdf_fallback")
        print("\ntex download failed, falling back to PDF...", file=sys.stderr)
        _fetch_pdf_fallback(args.arxiv_id, OUTPUT_DIR)


def cmd_infotex(args):
    """info + tex 组合：先打印论文元信息，再下载 LaTeX 源文件。"""
    cmd_info(args)
    print()  # 空行分隔 info 与 tex 两段输出
    cmd_tex(args)


def main():
    parser = argparse.ArgumentParser(
        description="arXiv 论文搜索与全文获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
    %(prog)s search "PINN" --max 5
    %(prog)s info 2401.12345
    %(prog)s bib 2505.08783
    %(prog)s bib 2505.08783 -o references.bib
    %(prog)s tex 2505.08783
    %(prog)s infotex 2505.08783
    %(prog)s cited 1711.10561
    %(prog)s cited 1711.10561 --max 50
    %(prog)s cited 1711.10561 --offset 20          # 第 21-40 条
    %(prog)s cited 1711.10561 --source openalex
    %(prog)s references 1711.10561
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # search 子命令
    search_parser = subparsers.add_parser("search", help="搜索论文 (S2→OpenAlex→arXiv)")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument(
        "--max", type=int, default=20, help="最大结果数 (默认 20)"
    )
    search_parser.add_argument(
        "--source",
        choices=["auto", "s2", "openalex", "arxiv"],
        default="auto",
        help="数据源: auto=自动(S2→OpenAlex→arXiv), s2, openalex, arxiv (默认 auto)",
    )
    # S2 过滤参数
    search_parser.add_argument("--year", help="年份或范围 (如 2024, 2020-2024, 2020-)")
    search_parser.add_argument("--fields-of-study", help="研究领域，逗号分隔 (如 Computer Science,Physics)")
    search_parser.add_argument("--pub-types", help="发表类型，逗号分隔 (如 JournalArticle,Conference)")
    search_parser.add_argument("--min-citations", type=int, help="最低引用数")
    search_parser.add_argument("--venue", help="会议/期刊名称")
    search_parser.add_argument("--open-access", action="store_true", help="仅显示开放获取论文")
    # S2 bulk 搜索
    search_parser.add_argument("--bulk", action="store_true", help="使用 S2 bulk 搜索（最多 1000 条）")
    search_parser.add_argument("--sort", help="排序字段 (如 citationCount:desc, publicationDate:desc)")
    search_parser.add_argument("--token", help="bulk 搜索翻页 token")
    search_parser.set_defaults(func=cmd_search)

    # info 子命令
    info_parser = subparsers.add_parser("info", help="获取论文信息（不下载全文）")
    info_parser.add_argument("arxiv_id", help="arXiv ID")
    info_parser.add_argument("--refresh", action="store_true", help="force re-fetch now (default: auto-refresh after 7 days)")
    info_parser.set_defaults(func=cmd_info)

    # bib 子命令
    bib_parser = subparsers.add_parser("bib", help="生成 BibTeX 引用")
    bib_parser.add_argument("arxiv_id", help="arXiv ID")
    bib_parser.add_argument("--output", "-o", help="输出文件路径（追加写入）")
    bib_parser.set_defaults(func=cmd_bib)

    # cited 子命令
    cited_parser = subparsers.add_parser("cited", help="被引反查：查看哪些论文引用了它")
    cited_parser.add_argument("arxiv_id", help="arXiv ID")
    cited_parser.add_argument(
        "--max", type=int, default=20, help="最大显示条数 (默认 20)"
    )
    cited_parser.add_argument(
        "--offset", type=int, default=0, help="跳过前 N 条结果，用于翻页 (默认 0)"
    )
    cited_parser.add_argument(
        "--source",
        choices=["auto", "s2", "openalex"],
        default="auto",
        help="数据源: auto=自动(S2优先), s2=Semantic Scholar, openalex=OpenAlex (默认 auto)",
    )
    cited_parser.set_defaults(func=cmd_cited)

    # references 子命令
    references_parser = subparsers.add_parser("references", help="正引查询：查看该论文引用了哪些论文")
    references_parser.add_argument("arxiv_id", help="arXiv ID")
    references_parser.add_argument(
        "--max", type=int, default=20, help="最大显示条数 (默认 20)"
    )
    references_parser.add_argument(
        "--offset", type=int, default=0, help="跳过前 N 条结果，用于翻页 (默认 0)"
    )
    references_parser.set_defaults(func=cmd_references)

    # tex 子命令
    tex_parser = subparsers.add_parser("tex", help="下载 LaTeX 源文件并解压")
    tex_parser.add_argument("arxiv_id", help="arXiv ID")
    tex_parser.add_argument("--refresh", action="store_true", help="force re-fetch now (default: auto-refresh after 7 days)")
    tex_parser.set_defaults(func=cmd_tex)

    # infotex 子命令
    infotex_parser = subparsers.add_parser("infotex", help="info + tex 组合：先打印论文信息，再下载 LaTeX")
    infotex_parser.add_argument("arxiv_id", help="arXiv ID")
    infotex_parser.add_argument("--refresh", action="store_true", help="force re-fetch now (default: auto-refresh after 7 days)")
    infotex_parser.set_defaults(func=cmd_infotex)

    args = parser.parse_args()

    # Audit: 记录调用元数据, 成功/异常都写一行 JSONL
    _started = time.time()
    _exit_code = 0
    global _LAST_SOURCE
    _LAST_SOURCE = "unknown"
    _arg = getattr(args, "arxiv_id", None) or getattr(args, "query", None) or ""
    _flags = {
        k: v for k, v in vars(args).items()
        if k not in ("command", "func", "arxiv_id", "query")
        and v is not None and v is not False
    }

    try:
        args.func(args)
    except KeyboardInterrupt:
        _exit_code = 130
    except SystemExit as e:
        # cmd_* 内部 sys.exit(N) 不算异常, 但要把退出码捕获进 audit; 否则 audit 记 0 与实际 N 不符.
        _exit_code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except arxiv.HTTPError as e:
        # arxiv.HTTPError.__str__ 带完整 URL，只取 HTTP 状态码
        print(f"Error: arXiv HTTP {e.status}", file=sys.stderr)
        _exit_code = 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        _exit_code = 1
    finally:
        _write_audit_entry({
            "ts": _datetime.now().isoformat(timespec="seconds"),
            "user": os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown",
            "cmd": args.command,
            "arg": _arg,
            "flags": _flags,
            "source_hit": _LAST_SOURCE,
            "cached_before": _LAST_SOURCE == "cache",
            "elapsed_s": round(time.time() - _started, 3),
            "exit_code": _exit_code,
        })

    if _exit_code:
        sys.exit(_exit_code)


if __name__ == "__main__":
    main()
