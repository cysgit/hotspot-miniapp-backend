"""Shared data models and base scraper class."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HotItem:
    """A single trending/hot item from any platform."""

    title: str
    url: str
    platform: str  # douyin, xiaohongshu, shipinhao, wechat_gzh
    hot_score: str  # e.g. "120万", "热搜第3", "10万+"
    rank: int = 0
    summary: str = ""
    author: str = ""
    cover_url: str = ""
    fetched_at: float = 0.0

    def __post_init__(self):
        if not self.fetched_at:
            self.fetched_at = time.time()


@dataclass
class PlatformSource:
    """Describes a data source platform."""

    key: str
    name: str
    icon: str  # emoji or unicode icon
    color: str  # hex color for UI


PLATFORMS = {
    "douyin": PlatformSource("douyin", "抖音", "🎵", "#000000"),
    "xiaohongshu": PlatformSource("xiaohongshu", "小红书", "📕", "#FF2442"),
    "shipinhao": PlatformSource("shipinhao", "视频号", "📹", "#07C160"),
    "wechat_gzh": PlatformSource("wechat_gzh", "微信公众号", "💬", "#353535"),
}


class BaseScraper(ABC):
    """Abstract base for all platform scrapers."""

    def __init__(self):
        self._demo_data: list[HotItem] = []

    @property
    @abstractmethod
    def platform_key(self) -> str:
        """Return platform key matching PLATFORMS dict."""
        ...

    @abstractmethod
    async def fetch(self) -> list[HotItem]:
        """Try to fetch real trending data. Returns list of HotItem."""
        ...

    def _demo_mode(self) -> list[HotItem]:
        """Fallback demo data when scraping fails."""
        return self._demo_data

    def set_demo_data(self, items: list[HotItem]):
        """Override the default demo data."""
        self._demo_data = items
