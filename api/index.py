"""Vercel Serverless — 全网热点聚合 API (Native Python handler)"""
import json, httpx, asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import scrapers
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers'))

CACHE = {}
CACHE_TTL = 120

async def fetch_scraper(name, mod_name):
    """Fetch data from a single scraper module"""
    try:
        mod = __import__(mod_name)
        scraper_cls = getattr(mod, f'{mod_name.title()}Scraper', None)
        if not scraper_cls:
            # Try alternative name patterns
            for attr_name in dir(mod):
                if 'Scraper' in attr_name and attr_name.endswith('Scraper'):
                    scraper_cls = getattr(mod, attr_name)
                    break
        if scraper_cls:
            scraper = scraper_cls()
            items = await scraper.fetch() if hasattr(scraper, 'fetch') and asyncio.iscoroutinefunction(scraper.fetch) else scraper.fetch()
            return name, items
    except Exception as e:
        print(f'[scraper] {name} error: {e}')
    return name, []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        result = {}
        
        if path == '' or path == '/':
            result = {
                "name": "全网热点聚合",
                "version": "1.0.0",
                "platforms": {
                    "douyin": {"name": "抖音", "icon": "🎵"},
                    "xiaohongshu": {"name": "小红书", "icon": "📕"},
                    "shipinhao": {"name": "视频号", "icon": "📹"},
                    "wechat_gzh": {"name": "微信公众号", "icon": "💬"}
                },
                "endpoints": {
                    "/hot": "获取所有平台热点",
                    "/platforms": "获取平台列表"
                }
            }
        
        elif path == '/platforms' or path == '/api/platforms':
            result = {
                "douyin": {"name": "抖音", "icon": "🎵", "color": "#000000"},
                "xiaohongshu": {"name": "小红书", "icon": "📕", "color": "#FF2442"},
                "shipinhao": {"name": "视频号", "icon": "📹", "color": "#07C160"},
                "wechat_gzh": {"name": "微信公众号", "icon": "💬", "color": "#353535"}
            }
        
        elif path == '/hot' or path == '/api/hot':
            # Return hot data synchronously (asyncio not well supported in Vercel Python)
            params = parse_qs(parsed.query)
            # Return mock/default data for now
            result = self._get_mock_hot_data()
        
        else:
            result = {"error": "not_found", "path": path}
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
    
    def _get_mock_hot_data(self):
        return {
            "total": 12,
            "platform_count": {"douyin": 3, "xiaohongshu": 3, "shipinhao": 3, "wechat_gzh": 3},
            "timestamp": __import__('time').time(),
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
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
