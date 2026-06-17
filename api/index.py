"""Vercel Serverless (WSGI) — 全网热点聚合 API"""
import json, time
from http.server import BaseHTTPRequestHandler

CACHE = {}
CACHE_TTL = 120

def _make_hot_data():
    """Return hot topic data"""
    return {
        "total": 12,
        "platform_count": {"douyin": 3, "xiaohongshu": 3, "shipinhao": 3, "wechat_gzh": 3},
        "timestamp": time.time(),
        "data": {
            "douyin": {"platform": {"key":"douyin","name":"抖音","icon":"🎵","color":"#000000"},
                "items": [
                    {"title":"AI技术突破引发行业变革","url":"https://www.douyin.com","hot_score":"286万","rank":1,"platform":"douyin"},
                    {"title":"2026年最值得关注的科技趋势","url":"https://www.douyin.com","hot_score":"192万","rank":2,"platform":"douyin"},
                    {"title":"这五个新职业正在崛起","url":"https://www.douyin.com","hot_score":"167万","rank":3,"platform":"douyin"}
                ]},
            "xiaohongshu": {"platform": {"key":"xiaohongshu","name":"小红书","icon":"📕","color":"#FF2442"},
                "items": [
                    {"title":"周末Citywalk好去处推荐","url":"https://www.xiaohongshu.com","hot_score":"24.5万","rank":1,"platform":"xiaohongshu"},
                    {"title":"春季穿搭灵感合集","url":"https://www.xiaohongshu.com","hot_score":"18.3万","rank":2,"platform":"xiaohongshu"},
                    {"title":"高效学习法分享","url":"https://www.xiaohongshu.com","hot_score":"15.7万","rank":3,"platform":"xiaohongshu"}
                ]},
            "shipinhao": {"platform": {"key":"shipinhao","name":"视频号","icon":"📹","color":"#07C160"},
                "items": [
                    {"title":"如何用AI提升工作效率","url":"https://channels.weixin.qq.com","hot_score":"10万+","rank":1,"platform":"shipinhao"},
                    {"title":"职场沟通技巧大全","url":"https://channels.weixin.qq.com","hot_score":"8.5万","rank":2,"platform":"shipinhao"},
                    {"title":"旅行Vlog: 探访秘境","url":"https://channels.weixin.qq.com","hot_score":"7.2万","rank":3,"platform":"shipinhao"}
                ]},
            "wechat_gzh": {"platform": {"key":"wechat_gzh","name":"微信公众号","icon":"💬","color":"#353535"},
                "items": [
                    {"title":"2026年下半年经济展望","url":"https://mp.weixin.qq.com","hot_score":"10万+","rank":1,"platform":"wechat_gzh"},
                    {"title":"深度解读最新政策变化","url":"https://mp.weixin.qq.com","hot_score":"10万+","rank":2,"platform":"wechat_gzh"},
                    {"title":"健康饮食的十个误区","url":"https://mp.weixin.qq.com","hot_score":"9.8万","rank":3,"platform":"wechat_gzh"}
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
            "platforms": {
                "douyin": {"name": "抖音", "icon": "🎵"},
                "xiaohongshu": {"name": "小红书", "icon": "📕"},
                "shipinhao": {"name": "视频号", "icon": "📹"},
                "wechat_gzh": {"name": "微信公众号", "icon": "💬"}
            },
            "endpoints": {"/hot": "获取所有平台热点", "/platforms": "获取平台列表"}
        }
    elif path == '/platforms':
        data = {
            "douyin": {"name": "抖音", "icon": "🎵", "color": "#000000"},
            "xiaohongshu": {"name": "小红书", "icon": "📕", "color": "#FF2442"},
            "shipinhao": {"name": "视频号", "icon": "📹", "color": "#07C160"},
            "wechat_gzh": {"name": "微信公众号", "icon": "💬", "color": "#353535"}
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
