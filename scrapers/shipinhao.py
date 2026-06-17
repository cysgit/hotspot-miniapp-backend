"""视频号热点爬虫

⚠️ 重要说明：
视频号 (WeChat Channels) 是微信生态内的功能，没有公开的 Web API 或网页版。
目前无法直接从外部抓取视频号的热点数据。
可行的替代方案：
  1. 使用微信官方广告 API（需企业资质）
  2. 使用微信视频号创作者后台（需有视频号账号）
  3. 接入第三方数据服务商（如新榜、飞瓜等）
  4. 使用微信开放平台的视频号相关接口（需申请）

此爬虫主要依靠第三方聚合API和模拟数据。
"""
from __future__ import annotations

import time

import httpx

from .base import BaseScraper, HotItem

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# 尝试一些第三方聚合API
FALLBACK_APIS = [
    "https://api.vvhan.com/api/hotlist/weiboHot",  # 有些聚合API有视频号数据
    "https://tenapi.cn/v2/weibohot",
]


class ShipinhaoScraper(BaseScraper):
    """Scrape WeChat Channels (视频号) trending."""

    @property
    def platform_key(self) -> str:
        return "shipinhao"

    async def fetch(self) -> list[HotItem]:
        errors = []

        # 尝试第三方API（部分聚合API可能包含视频号数据）
        try:
            items = await self._try_apis()
            if items:
                return items
        except Exception as e:
            errors.append(f"API抓取失败: {e}")

        print(f"[shipinhao] 抓取失败: {'; '.join(errors)}，使用模拟数据")
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
                # 微博热点中部分内容也会在视频号传播
                if "vvhan" in api_url or "tenapi" in api_url:
                    entries = data.get("data", [])
                    # 只取前20条作为参考
                    for idx, item in enumerate(entries[:20]):
                        title = item.get("title", "") or item.get("name", "")
                        if not title:
                            continue
                        items.append(
                            HotItem(
                                title=title,
                                url=f"https://weixin.qq.com/cgi-bin/readtemplate?t=find_video_tmpl&search={title}",
                                platform="shipinhao",
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
        """模拟视频号热点数据"""
        demos = [
            "今天这个视频火遍了朋友圈",
            "很多人不知道的微信隐藏功能",
            "这个农村小伙靠养殖年入百万",
            "三步教你学会这个特效",
            "千万不要在晚上看这个视频",
            "全网都在模仿这个舞蹈",
            "老照片修复技术让网友泪目",
            "这段采访值得每个家长看看",
            "旅行博主带你云游西藏",
            "猫咪成精了！它的举动让人震惊",
            "这个创业故事看哭了多少人",
            "一秒教你辨别真假货",
            "民间高手做的这个太惊艳了",
            "看完这个你还敢熬夜吗",
            "这个知识点百分之90的人都不知道",
        ]
        now = time.time()
        return [
            HotItem(
                title=t,
                url="https://channels.weixin.qq.com/",
                platform="shipinhao",
                hot_score=f"{(15-i)*1000}+" if i < 10 else f"{(15-i)*500}+",
                rank=i + 1,
                fetched_at=now,
            )
            for i, t in enumerate(demos)
        ]
