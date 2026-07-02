"""Common helper functions: IO, timing, logging."""

from __future__ import annotations

import gzip
import json
import logging
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


def get_logger(name: str, log_file: Path | None = None) -> logging.Logger:
    """Return a configured logger that writes to stdout and optionally a file."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger


@contextmanager
def timer(label: str, logger: logging.Logger | None = None) -> Iterator[None]:
    """Context manager to time a block of code."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    msg = f"[TIMER] {label}: {elapsed:.2f}s"
    if logger:
        logger.info(msg)
    else:
        print(msg)


def read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    """Read a gzip-compressed JSONL file into a list of dicts."""
    records = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_jsonl_gz(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)


def safe_get(d: dict, key: str, default: Any = None) -> Any:
    """Get a value from a dict, returning default for None or missing key."""
    val = d.get(key, default)
    return default if val is None else val


def as_list(value: Any) -> list:
    """Normalize a value that might be a list, a single item, or None into a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        # handle comma-separated strings gracefully
        return [v.strip() for v in value.split(",") if v.strip()]
    return [value]


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split()).strip().lower()