"""抖音热点爬虫 - 从抖音热搜页面抓取"""
from __future__ import annotations

import re
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .base import BaseScraper, HotItem

DOUYIN_HOT_URL = "https://www.douyin.com/hot"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# 备用API端点（非官方，可能会变化）
FALLBACK_APIS = [
    "https://tenapi.cn/v2/douyinhot",
    "https://api.vvhan.com/api/hotlist/douYinHot",
]


class DouyinScraper(BaseScraper):
    """Scrape Douyin trending topics."""

    @property
    def platform_key(self) -> str:
        return "douyin"

    async def fetch(self) -> list[HotItem]:
        items = []
        errors = []

        # 策略1: 尝试直接抓取抖音热搜页面
        try:
            items = await self._scrape_hot_page()
            if items:
                return items
        except Exception as e:
            errors.append(f"页面抓取失败: {e}")

        # 策略2: 尝试第三方API
        try:
            items = await self._try_fallback_apis()
            if items:
                return items
        except Exception as e:
            errors.append(f"第三方API失败: {e}")

        print(f"[douyin] 所有抓取方式均失败: {'; '.join(errors)}，使用模拟数据")
        return self._demo_mode()

    async def _scrape_hot_page(self) -> list[HotItem]:
        """直接抓取抖音热搜页面"""
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(
                DOUYIN_HOT_URL,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
            )
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # 抖音页面是用JS渲染的，但可能会在初始HTML中有SSR数据
        # 尝试查找<script>中的JSON数据
        items = []

        # 方法1: 查找window.__INITIAL_STATE__或类似变量
        for script in soup.find_all("script"):
            text = script.string or ""
            if "hotSearchData" in text or "hotWords" in text:
                # 尝试提取JSON数据
                json_match = re.search(r"window\.__INITIAL_STATE__\s*=\s*({.*?});", text, re.DOTALL)
                if json_match:
                    import json

                    data = json.loads(json_match.group(1))
                    hot_words = (
                        data.get("hotSearchData", {})
                        .get("hotSearchList", [])
                    )
                    for idx, item in enumerate(hot_words):
                        items.append(
                            HotItem(
                                title=item.get("word", ""),
                                url=f"https://www.douyin.com/search/{item.get('word', '')}",
                                platform="douyin",
                                hot_score=str(item.get("hotValue", f"热搜#{idx+1}")),
                                rank=idx + 1,
                                summary=item.get("label", ""),
                                fetched_at=time.time(),
                            )
                        )
                    if items:
                        break

        return items

    async def _try_fallback_apis(self) -> list[HotItem]:
        """尝试第三方聚合API"""
        for api_url in FALLBACK_APIS:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(api_url, headers={"User-Agent": USER_AGENT})
                    if resp.status_code != 200:
                        continue
                    data = resp.json()

                items = []
                # 不同的API有不同的返回格式，尝试兼容
                if api_url == "https://tenapi.cn/v2/douyinhot":
                    for idx, item in enumerate(data.get("data", [])):
                        items.append(
                            HotItem(
                                title=item.get("name", ""),
                                url=item.get("url", ""),
                                platform="douyin",
                                hot_score=item.get("hot", f"#{idx+1}"),
                                rank=idx + 1,
                                fetched_at=time.time(),
                            )
                        )
                elif api_url.startswith("https://api.vvhan.com"):
                    for idx, item in enumerate(data.get("data", [])):
                        items.append(
                            HotItem(
                                title=item.get("title", ""),
                                url=item.get("url", ""),
                                platform="douyin",
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
        """模拟抖音热搜数据（抓取失败时使用）"""
        demos = [
            "全网爆款！这个美食做法火了",
            "明星夫妻官宣离婚，网友炸锅了",
            "高考成绩今日公布，分数线出炉",
            "这款国产AI工具彻底火了",
            "突发！重大政策调整",
            "热门旅游城市出现人从众",
            "新人主播一晚赚百万？真相是",
            "这个夏天最流行的穿搭来啦",
            "神十八航天员顺利出舱",
            "无人机表演惊艳全场",
            "这种水果价格暴涨300%",
            "天价演唱会门票引发争议",
            "这个城市房价跌回五年前",
            "00后整顿职场又出新招",
            "特斯拉新款发布会倒计时",
        ]
        now = time.time()
        return [
            HotItem(
                title=t,
                url=f"https://www.douyin.com/search/{t}",
                platform="douyin",
                hot_score=f"{(15-i)*10+5}万",
                rank=i + 1,
                fetched_at=now,
            )
            for i, t in enumerate(demos)
        ]
