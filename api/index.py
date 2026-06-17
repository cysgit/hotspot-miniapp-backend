"""Vercel Serverless — FastAPI + Mangum adapter for Hotspot API"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app
from mangum import Mangum

# Mangum wraps FastAPI ASGI app for Vercel's WSGI-compatible Lambda runtime
handler = Mangum(app, lifespan="off")
