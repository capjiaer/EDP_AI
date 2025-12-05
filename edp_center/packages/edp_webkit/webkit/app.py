from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .routers import metrics_router
import os

def create_app():
    app = FastAPI(title="EDP WebKit", description="EDP Center Web Services")
    
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 挂载静态文件目录
    static_dir = os.path.join(current_dir, "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # 挂载 templates 目录作为静态资源 (为了简化，暂不使用服务端渲染模板，直接 serve HTML)
    templates_dir = os.path.join(current_dir, "templates")
    if os.path.exists(templates_dir):
        app.mount("/dashboard", StaticFiles(directory=templates_dir, html=True), name="dashboard")

    # 注册路由
    app.include_router(metrics_router.router)
    
    # 根路径重定向到 Dashboard
    @app.get("/")
    async def root():
        return RedirectResponse(url="/dashboard/index.html")
    
    return app
