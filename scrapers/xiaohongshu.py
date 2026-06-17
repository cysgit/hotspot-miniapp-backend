"""小红书热点爬虫"""
from __future__ import annotations

import json
import re
import time

import httpx
from bs4 import BeautifulSoup

from .base import BaseScraper, HotItem

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# 小红书加密较严，主要使用第三方聚合API
FALLBACK_APIS = [
    "https://tenapi.cn/v2/xiaohongshuhot",
    "https://api.vvhan.com/api/hotlist/xiaohongshuHot",
]


class XiaohongshuScraper(BaseScraper):
    """Scrape Xiaohongshu (RED) trending topics."""

    @property
    def platform_key(self) -> str:
        return "xiaohongshu"

    async def fetch(self) -> list[HotItem]:
        items = []
        errors = []

        # 策略: 尝试第三方聚合API
        try:
            items = await self._try_fallback_apis()
            if items:
                return items
        except Exception as e:
            errors.append(f"第三方API失败: {e}")

        print(f"[xiaohongshu] 所有抓取方式均失败: {'; '.join(errors)}，使用模拟数据")
        return self._demo_mode()

    async def _try_fallback_apis(self) -> list[HotItem]:
        """尝试第三方聚合API"""
        for api_url in FALLBACK_APIS:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        api_url,
                        headers={"User-Agent": USER_AGENT},
                    )
                    if resp.status_code != 200:
                        continue
                    data = resp.json()

                items = []
                if "tenapi" in api_url:
                    for idx, item in enumerate(data.get("data", [])):
                        items.append(
                            HotItem(
                                title=item.get("name", ""),
                                url=item.get("url", ""),
                                platform="xiaohongshu",
                                hot_score=item.get("hot", f"#{idx+1}"),
                                rank=idx + 1,
                                summary="",
                                fetched_at=time.time(),
                            )
                        )
                elif "vvhan" in api_url:
                    for idx, item in enumerate(data.get("data", [])):
                        items.append(
                            HotItem(
                                title=item.get("title", ""),
                                url=item.get("url", ""),
                                platform="xiaohongshu",
                                hot_score=item.get("hot", f"#{idx+1}"),
                                rank=idx + 1,
                                fetched_at=time.time(),
                            )
                        )

                if items:
                    return items
            except Exception:
                continue

        return []

    def _demo_mode(self) -> list[HotItem]:
        """模拟小红书热搜数据"""
        demos = [
            "周末去哪玩？这5个地方绝了",
            "早八妆容十分钟搞定！",
            "独居女孩的100个安全感好物",
            "真正厉害的女生都学会了这点",
            "月薪5000如何存下10万？",
            "这套穿搭被问了800遍链接",
            "千万不要这样用护肤品！",
            "2024年最值得读的10本书",
            "租房改造花了300块，邻居都来抄作业",
            "这种旅行方式正在年轻人中流行",
            "我发现了一个超好用的学习方法",
            "小红书爆款笔记标题公式来了",
            "减脂期这几种水果千万别吃",
            "副业指南：靠这个每月多赚5000",
            "极简生活一年后，我后悔了...",
        ]
        now = time.time()
        return [
            HotItem(
                title=t,
                url=f"https://www.xiaohongshu.com/search_result?keyword={t}",
                platform="xiaohongshu",
                hot_score=f"{(15-i)*1000+500}赞",
                rank=i + 1,
                fetched_at=now,
            )
            for i, t in enumerate(demos)
        ]
