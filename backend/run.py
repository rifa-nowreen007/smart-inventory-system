#!/usr/bin/env python3
"""
SmartInventory-007 — Backend Server
Run: python run.py
"""
import uvicorn

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║   📦  SmartInventory-007  API  v1.0.0            ║
║                                                  ║
║   API    →  http://localhost:8000                ║
║   Docs   →  http://localhost:8000/docs           ║
║   ReDoc  →  http://localhost:8000/redoc          ║
╚══════════════════════════════════════════════════╝
    """)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
