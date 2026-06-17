"""热点聚合 API 服务器 - FastAPI"""
from __future__ import annotations

import asyncio
import time
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from scrapers import (
    DouyinScraper,
    HotItem,
    XiaohongshuScraper,
    ShipinhaoScraper,
    WechatGzhScraper,
    PLATFORMS,
)

app = FastAPI(
    title="全网热点聚合 API",
    description="聚合抖音、小红书、视频号、微信公众号热点数据",
    version="1.0.0",
)

# 允许跨域（小程序和调试用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 爬虫实例（单例）
DOUYIN = DouyinScraper()
XIAOHONGSHU = XiaohongshuScraper()
SHIPINHAO = ShipinhaoScraper()
WECHAT_GZH = WechatGzhScraper()

ALL_SCRAPERS = {
    "douyin": DOUYIN,
    "xiaohongshu": XIAOHONGSHU,
    "shipinhao": SHIPINHAO,
    "wechat_gzh": WECHAT_GZH,
}

# 简单内存缓存
_cache: dict[str, tuple[float, list[dict]]] = {}
CACHE_TTL = 120  # 缓存2分钟


def _item_to_dict(item: HotItem) -> dict:
    return {
        "title": item.title,
        "url": item.url,
        "platform": item.platform,
        "hot_score": item.hot_score,
        "rank": item.rank,
        "summary": item.summary,
        "author": item.author,
        "cover_url": item.cover_url,
        "fetched_at": item.fetched_at,
    }


async def _fetch_with_cache(key: str, scraper) -> list[dict]:
    """带缓存的抓取"""
    now = time.time()
    if key in _cache:
        ts, data = _cache[key]
        if now - ts < CACHE_TTL:
            return data

    items = await scraper.fetch()
    result = [_item_to_dict(item) for item in items]
    _cache[key] = (now, result)
    return result


@app.get("/")
def root():
    return {
        "name": "全网热点聚合",
        "version": "1.0.0",
        "platforms": {k: {"name": v.name, "icon": v.icon} for k, v in PLATFORMS.items()},
        "endpoints": {
            "/hot": "获取所有平台热点",
            "/hot/{platform}": "获取指定平台热点",
            "/platforms": "获取平台列表",
            "/refresh": "强制刷新缓存",
        },
    }


@app.get("/platforms")
def get_platforms():
    """获取支持的平台列表"""
    return {
        k: {"name": v.name, "icon": v.icon, "color": v.color}
        for k, v in PLATFORMS.items()
    }


@app.get("/hot")
async def get_all_hot(
    limit: int = Query(20, ge=1, le=100, description="每个平台返回条数"),
):
    """获取所有平台的热点数据"""
    tasks = []
    for key, scraper in ALL_SCRAPERS.items():
        tasks.append(_fetch_with_cache(key, scraper))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    platform_count = {}
    for key, result in zip(ALL_SCRAPERS.keys(), results):
        if isinstance(result, Exception):
            print(f"[hot] {key} 抓取异常: {result}")
            continue
        platform_count[key] = len(result)
        all_items.extend(result[:limit])

    # 按平台分组返回（前端更方便渲染）
    grouped = {}
    for key in ALL_SCRAPERS:
        grouped[key] = {"platform": PLATFORMS[key], "items": []}
    for item in all_items:
        p = item["platform"]
        if p in grouped:
            grouped[p]["items"].append(item)

    return {
        "total": len(all_items),
        "platform_count": platform_count,
        "timestamp": time.time(),
        "data": grouped,
    }


@app.get("/hot/{platform}")
async def get_platform_hot(
    platform: str,
    limit: int = Query(30, ge=1, le=100),
):
    """获取指定平台的热点数据"""
    platform = platform.lower().replace(" ", "_")
    if platform not in ALL_SCRAPERS:
        valid = list(ALL_SCRAPERS.keys())
        return {"error": f"不支持的平台: {platform}", "valid_platforms": valid}

    scraper = ALL_SCRAPERS[platform]
    items = await _fetch_with_cache(platform, scraper)

    return {
        "platform": PLATFORMS[platform],
        "total": len(items[:limit]),
        "timestamp": time.time(),
        "data": items[:limit],
    }


@app.post("/refresh")
async def refresh_cache():
    """强制刷新所有缓存"""
    _cache.clear()
    return {"status": "ok", "message": "缓存已清空，下次请求将重新抓取"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
