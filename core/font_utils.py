#!/usr/bin/env python3
"""
Shared font discovery helpers for multilingual title and cover rendering.
"""
import logging
import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)


CJK_LANGUAGES = {"zh", "ja", "ko"}
REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_FONT_ROOTS = [
    REPO_ROOT / ".local-fonts" / "fonts-noto-cjk",
    REPO_ROOT / ".local-fonts",
    REPO_ROOT / "assets" / "fonts",
    REPO_ROOT / "fonts",
]


def _normalize_language(language: str) -> str:
    return (language or "default").lower().split("-")[0]


def is_cjk_language(language: str) -> bool:
    return _normalize_language(language) in CJK_LANGUAGES


def _append_unique(items: List[str], *candidates: str) -> None:
    for candidate in candidates:
        if candidate and candidate not in items:
            items.append(candidate)


def _prepend_local_paths(paths: List[str], *relative_paths: str) -> None:
    for root in LOCAL_FONT_ROOTS:
        for relative_path in relative_paths:
            _append_unique(paths, str(root / relative_path))


def _preferred_font_paths(language: str, prefer_bold: bool) -> List[str]:
    paths: List[str] = []
    normalized = _normalize_language(language)

    if normalized == "vi":
        _prepend_local_paths(
            paths,
            "usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        )
        if prefer_bold:
            _append_unique(
                paths,
                "/Library/Fonts/Arial Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            )
        _append_unique(
            paths,
            "/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        )
        return paths

    if is_cjk_language(normalized):
        _prepend_local_paths(
            paths,
            "usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
            "usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        )
        if prefer_bold:
            _append_unique(
                paths,
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "C:/Windows/Fonts/msyhbd.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansSC-Bold.otf",
                "/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Bold.otf",
            )

        _append_unique(
            paths,
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansSC-Regular.otf",
            "/usr/share/fonts/opentype/noto/NotoSansSC-Bold.otf",
            "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
            "/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Regular.otf",
            "/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Bold.otf",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
        )
        return paths

    if prefer_bold:
        _append_unique(paths, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        _append_unique(paths, "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/DejaVuSans-Bold.ttf")
    _append_unique(paths, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    _append_unique(paths, "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/DejaVuSans.ttf")
    return paths


def _fontconfig_patterns(language: str, prefer_bold: bool) -> List[str]:
    normalized = _normalize_language(language)
    patterns: List[str] = []

    if normalized == "vi":
        families = ["Arial Unicode MS", "Arial", "DejaVu Sans"]
    elif is_cjk_language(normalized):
        families = [
            "PingFang SC",
            "STHeiti",
            "Hiragino Sans GB",
            "Microsoft YaHei",
            "SimHei",
            "Noto Sans CJK SC",
            "Noto Sans SC",
            "Noto Serif CJK SC",
            "Source Han Sans SC",
            "WenQuanYi Zen Hei",
            "WenQuanYi Micro Hei",
            "Arial Unicode MS",
        ]
    else:
        families = ["DejaVu Sans"]

    if prefer_bold:
        for family in families:
            _append_unique(patterns, f"{family}:style=Bold", family)
    else:
        for family in families:
            _append_unique(patterns, family, f"{family}:style=Bold")

    return patterns


@lru_cache(maxsize=32)
def _fc_match(pattern: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["fc-match", "-f", "%{family}\n%{file}\n", pattern],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except (FileNotFoundError, OSError):
        return None

    if result.returncode != 0:
        return None

    lines = (result.stdout or "").strip().splitlines()
    if len(lines) < 2:
        return None

    matched_family = lines[0].strip()
    candidate = lines[1].strip()
    requested_family = pattern.split(":", 1)[0].strip()

    requested_tokens = {
        token for token in re.split(r"[\s,_-]+", requested_family.lower()) if token
    }
    matched_tokens = {
        token for token in re.split(r"[\s,_-]+", matched_family.lower()) if token
    }

    if requested_tokens and not requested_tokens.issubset(matched_tokens):
        return None

    return candidate if candidate and os.path.exists(candidate) else None


def _existing_paths(candidates: Iterable[str]) -> Iterable[str]:
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            yield candidate


def find_best_font(
    language: str = "zh",
    prefer_bold: bool = False,
    allow_generic_fallback: bool = True,
) -> Optional[str]:
    """Find the best locally available font for the given language."""
    for candidate in _existing_paths(_preferred_font_paths(language, prefer_bold)):
        return candidate

    for pattern in _fontconfig_patterns(language, prefer_bold):
        candidate = _fc_match(pattern)
        if candidate:
            return candidate

    if allow_generic_fallback:
        generic_language = "default"
        for candidate in _existing_paths(_preferred_font_paths(generic_language, prefer_bold)):
            return candidate
        for pattern in _fontconfig_patterns(generic_language, prefer_bold):
            candidate = _fc_match(pattern)
            if candidate:
                return candidate

    return None


def build_missing_font_message(language: str) -> str:
    if is_cjk_language(language):
        return (
            "No suitable CJK font found for title/cover rendering. "
            "Install Noto Sans CJK SC, WenQuanYi Zen Hei (fonts-wqy-zenhei), "
            "Source Han Sans SC, Microsoft YaHei, or SimHei, then rerun."
        )

    if _normalize_language(language) == "vi":
        return (
            "No suitable Vietnamese-capable font found for title/cover rendering. "
            "Install Arial Unicode MS or DejaVu Sans, then rerun."
        )

    return "No suitable font found for title/cover rendering."
