const express = require('express');
const app = express();
const PORT = process.env.PORT || 8080;

// CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', '*');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Mock hot data
const hotData = {
  total: 12,
  platform_count: { douyin: 3, xiaohongshu: 3, shipinhao: 3, wechat_gzh: 3 },
  data: {
    douyin: {
      platform: { key: "douyin", name: "抖音", icon: "🎵", color: "#000000" },
      items: [
        { title: "AI技术突破引发行业变革", url: "https://www.douyin.com", hot_score: "286万", rank: 1, platform: "douyin" },
        { title: "2026年最值得关注的科技趋势", url: "https://www.douyin.com", hot_score: "192万", rank: 2, platform: "douyin" },
        { title: "这五个新职业正在崛起", url: "https://www.douyin.com", hot_score: "167万", rank: 3, platform: "douyin" }
      ]
    },
    xiaohongshu: {
      platform: { key: "xiaohongshu", name: "小红书", icon: "📕", color: "#FF2442" },
      items: [
        { title: "周末Citywalk好去处推荐", url: "https://www.xiaohongshu.com", hot_score: "24.5万", rank: 1, platform: "xiaohongshu" },
        { title: "春季穿搭灵感合集", url: "https://www.xiaohongshu.com", hot_score: "18.3万", rank: 2, platform: "xiaohongshu" },
        { title: "高效学习法分享", url: "https://www.xiaohongshu.com", hot_score: "15.7万", rank: 3, platform: "xiaohongshu" }
      ]
    },
    shipinhao: {
      platform: { key: "shipinhao", name: "视频号", icon: "📹", color: "#07C160" },
      items: [
        { title: "如何用AI提升工作效率", url: "https://channels.weixin.qq.com", hot_score: "10万+", rank: 1, platform: "shipinhao" },
        { title: "职场沟通技巧大全", url: "https://channels.weixin.qq.com", hot_score: "8.5万", rank: 2, platform: "shipinhao" },
        { title: "旅行Vlog: 探访秘境", url: "https://channels.weixin.qq.com", hot_score: "7.2万", rank: 3, platform: "shipinhao" }
      ]
    },
    wechat_gzh: {
      platform: { key: "wechat_gzh", name: "微信公众号", icon: "💬", color: "#353535" },
      items: [
        { title: "2026年下半年经济展望", url: "https://mp.weixin.qq.com", hot_score: "10万+", rank: 1, platform: "wechat_gzh" },
        { title: "深度解读最新政策变化", url: "https://mp.weixin.qq.com", hot_score: "10万+", rank: 2, platform: "wechat_gzh" },
        { title: "健康饮食的十个误区", url: "https://mp.weixin.qq.com", hot_score: "9.8万", rank: 3, platform: "wechat_gzh" }
      ]
    }
  }
};

// Routes
app.get('/', (req, res) => {
  res.json({
    name: "全网热点聚合",
    version: "1.0.0",
    platforms: {
      douyin: { name: "抖音", icon: "🎵" },
      xiaohongshu: { name: "小红书", icon: "📕" },
      shipinhao: { name: "视频号", icon: "📹" },
      wechat_gzh: { name: "微信公众号", icon: "💬" }
    },
    endpoints: { "/hot": "获取所有平台热点", "/platforms": "获取平台列表" }
  });
});

app.get('/platforms', (req, res) => {
  res.json({
    douyin: { name: "抖音", icon: "🎵", color: "#000000" },
    xiaohongshu: { name: "小红书", icon: "📕", color: "#FF2442" },
    shipinhao: { name: "视频号", icon: "📹", color: "#07C160" },
    wechat_gzh: { name: "微信公众号", icon: "💬", color: "#353535" }
  });
});

app.get('/hot', (req, res) => {
  hotData.timestamp = Date.now() / 1000;
  res.json(hotData);
});

app.listen(PORT, () => {
  console.log(`Hotspot API running on port ${PORT}`);
});
