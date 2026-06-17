"""Vercel Serverless (WSGI) — 全网热点聚合 API"""
import json, time
from http.server import BaseHTTPRequestHandler

CACHE = {}
CACHE_TTL = 120

def _make_hot_data():
    """Return hot topic data organized by vertical categories"""
    return {
        "total": 15,
        "category_count": {"muying": 3, "meishi": 3, "shiling": 3, "ai": 3, "tongyong": 3},
        "timestamp": time.time(),
        "data": {
            "muying": {"category": {"key":"muying","name":"母婴","icon":"👶","color":"#FF69B4"},
                "items": [
                    {"title":"夏季宝宝防晒攻略：这些误区要避开","url":"#","hot_score":"32.5万","rank":1,"category":"muying","summary":"儿科专家详解婴幼儿防晒产品选择和注意事项"},
                    {"title":"新生儿抚触教程（0-3个月）","url":"#","hot_score":"28.3万","rank":2,"category":"muying","summary":"资深月嫂手把手教学，促进宝宝生长发育"},
                    {"title":"2026最新儿童营养食谱推荐","url":"#","hot_score":"21.7万","rank":3,"category":"muying","summary":"三甲医院营养科主任推荐，涵盖各年龄段"}
                ]},
            "meishi": {"category": {"key":"meishi","name":"美食","icon":"🍜","color":"#FF8C00"},
                "items": [
                    {"title":"夏天必学的5道凉拌菜做法","url":"#","hot_score":"45.2万","rank":1,"category":"meishi","summary":"清爽开胃，10分钟就能搞定"},
                    {"title":"网红空气炸锅美食合集","url":"#","hot_score":"38.6万","rank":2,"category":"meishi","summary":"零失败食谱，厨房小白也能做"},
                    {"title":"减脂期也能吃的低卡甜品","url":"#","hot_score":"29.4万","rank":3,"category":"meishi","summary":"无糖无油，每一款都不到100卡"}
                ]},
            "shiling": {"category": {"key":"shiling","name":"时令","icon":"🌻","color":"#32CD32"},
                "items": [
                    {"title":"夏至养生：这3件事千万别做","url":"#","hot_score":"52.1万","rank":1,"category":"shiling","summary":"中医专家提醒，顺应节气才能健康度夏"},
                    {"title":"入夏后高发！儿童手足口病预防指南","url":"#","hot_score":"47.3万","rank":2,"category":"shiling","summary":"疾控中心发布最新防控建议，家长必看"},
                    {"title":"6月水果上市时间表，别买错了","url":"#","hot_score":"36.8万","rank":3,"category":"shiling","summary":"当季水果最新鲜，一张表告诉你什么时候吃什么"}
                ]},
            "ai": {"category": {"key":"ai","name":"AI科技","icon":"🤖","color":"#4169E1"},
                "items": [
                    {"title":"GPT-5.4发布：推理能力大幅跃升","url":"#","hot_score":"286万","rank":1,"category":"ai","summary":"OpenAI最新模型在多项基准测试中刷新纪录"},
                    {"title":"AI改写软件工程：2026年趋势报告","url":"#","hot_score":"192万","rank":2,"category":"ai","summary":"AI Agent渗透率已达47%，开发者效率提升3倍"},
                    {"title":"国内大模型价格战再升级","url":"#","hot_score":"167万","rank":3,"category":"ai","summary":"豆包、文心、通义千问纷纷大幅降价，最高降幅90%"}
                ]},
            "tongyong": {"category": {"key":"tongyong","name":"通用热点","icon":"🔥","color":"#FF4500"},
                "items": [
                    {"title":"2026年高考分数线公布","url":"#","hot_score":"528万","rank":1,"category":"tongyong","summary":"全国各地分数线陆续出炉，录取批次有重大调整"},
                    {"title":"端午假期出行指南","url":"#","hot_score":"415万","rank":2,"category":"tongyong","summary":"高速免费政策、热门景区预约、天气全攻略"},
                    {"title":"618购物节终极省钱攻略","url":"#","hot_score":"389万","rank":3,"category":"tongyong","summary":"全网比价，教你避开提价再打折的坑"}
                ]}
        }
    }

def app(environ, start_response):
    """WSGI application for @vercel/python builder"""
    path = environ.get('PATH_INFO', '/').rstrip('/')

    if path == '' or path == '/':
        data = {
            "name": "全网热点聚合",
            "version": "1.0.0",
            "categories": {
                "muying": {"name": "母婴", "icon": "👶"},
                "meishi": {"name": "美食", "icon": "🍜"},
                "shiling": {"name": "时令", "icon": "🌻"},
                "ai": {"name": "AI科技", "icon": "🤖"},
                "tongyong": {"name": "通用热点", "icon": "🔥"}
            },
            "endpoints": {"/hot": "获取按垂类聚合的热点", "/categories": "获取垂类列表"}
        }
    elif path in ('/categories', '/categories/'):
        data = {
            "muying": {"name": "母婴", "icon": "👶", "color": "#FF69B4"},
            "meishi": {"name": "美食", "icon": "🍜", "color": "#FF8C00"},
            "shiling": {"name": "时令", "icon": "🌻", "color": "#32CD32"},
            "ai": {"name": "AI科技", "icon": "🤖", "color": "#4169E1"},
            "tongyong": {"name": "通用热点", "icon": "🔥", "color": "#FF4500"}
        }
    elif path in ('/hot', '/api/hot'):
        data = _make_hot_data()
    else:
        data = {"error": "not_found", "path": path}
    
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', '*'),
        ('Content-Length', str(len(body)))
    ]
    start_response(status, headers)
    return [body]
