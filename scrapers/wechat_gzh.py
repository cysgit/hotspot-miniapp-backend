"""微信公众号热点爬虫

⚠️ 说明：
微信公众号的文章阅读数据没有开放 API。
获取10万+爆文的方法：
  1. 微信搜一搜 API（需申请微信开放平台）
  2. 公众号 RSS 订阅（如 WeRSS、Feeddd 等第三方服务）
  3. 新榜/清博等第三方数据平台（付费）
  4. 搜狗微信搜索（已下线）
  
此爬虫会尝试可用的公开途径，并提供模拟数据保底。
"""
from __future__ import annotations

import json
import time

import httpx
from bs4 import BeautifulSoup

from .base import BaseScraper, HotItem

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

FALLBACK_APIS = [
    "https://tenapi.cn/v2/weixinhot",  # 微信热点
    "https://api.vvhan.com/api/hotlist/wechatHot",
    "https://api.zhangshu.fun/v1/hot-list/wechat",  # 第三方聚合
]


class WechatGzhScraper(BaseScraper):
    """Scrape WeChat Official Account trending articles."""

    @property
    def platform_key(self) -> str:
        return "wechat_gzh"

    async def fetch(self) -> list[HotItem]:
        items = []
        errors = []

        # 策略: 尝试第三方聚合API
        try:
            items = await self._try_apis()
            if items:
                return items
        except Exception as e:
            errors.append(f"API抓取失败: {e}")

        print(f"[wechat_gzh] 所有方式失败: {'; '.join(errors)}，使用模拟数据")
        return self._demo_mode()

    async def _try_apis(self) -> list[HotItem]:
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
                                platform="wechat_gzh",
                                hot_score=item.get("hot", f"#{idx+1}"),
                                rank=idx + 1,
                                author=item.get("author", ""),
                                summary=item.get("desc", ""),
                                fetched_at=time.time(),
                            )
                        )
                elif "vvhan" in api_url:
                    for idx, item in enumerate(data.get("data", [])):
                        items.append(
                            HotItem(
                                title=item.get("title", ""),
                                url=item.get("url", ""),
                                platform="wechat_gzh",
                                hot_score=item.get("hot", f"#{idx+1}"),
                                rank=idx + 1,
                                author=item.get("author", ""),
                                summary=item.get("desc", ""),
                                fetched_at=time.time(),
                            )
                        )
                elif "zhangshu" in api_url:
                    for idx, item in enumerate(data.get("data", [])):
                        items.append(
                            HotItem(
                                title=item.get("title", ""),
                                url=item.get("url", ""),
                                platform="wechat_gzh",
                                hot_score=item.get("views", f"#{idx+1}"),
                                rank=idx + 1,
                                author=item.get("author", ""),
                                fetched_at=time.time(),
                            )
                        )

                if items:
                    return items
            except Exception:
                continue

        return []

    def _demo_mode(self) -> list[HotItem]:
        """模拟微信公众号10万+爆文数据"""
        demos = [
            ("深夜重磅！央行宣布降息", "财经观察", "10万+"),
            ("这5种食物千万别放冰箱，越放越坏", "健康生活", "10万+"),
            ("一个家庭最大的悲哀，不是没钱", "洞见", "10万+"),
            ("00后整顿职场，这次轮到老板慌了", "人力星球", "8.5万"),
            ("人生建议：不要和烂人烂事纠缠", "心灵鸡汤", "7.2万"),
            ("终于有人把AI说清楚了", "科技前沿", "6.8万"),
            ("孩子发烧了，这个做法害了无数家庭", "儿科医生", "9.1万"),
            ("中国最危险的职业，月薪不到3000", "人物", "8.0万"),
            ("35岁以后才明白的道理", "人生哲理", "7.5万"),
            ("我花了三年，终于从月薪5000到5万", "职场进阶", "6.5万"),
            ("这个城市出台楼市新政，房价要涨？", "楼市观察", "5.8万"),
            ("退休金调整方案出炉，看看你涨了多少", "社会保障", "9.5万"),
            ("熬夜对身体的伤害不可逆！", "医学科普", "6.0万"),
            ("这本书我读了五遍，推荐给所有人", "书单来了", "5.5万"),
            ("全国最宜居城市排名出炉", "城市生活", "7.0万"),
        ]
        now = time.time()
        return [
            HotItem(
                title=t,
                url=f"https://mp.weixin.qq.com/s/0",
                platform="wechat_gzh",
                hot_score=hot,
                rank=i + 1,
                author=a,
                fetched_at=now,
            )
            for i, (t, a, hot) in enumerate(demos)
        ]
