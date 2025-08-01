# pyapi/__main__.py
import uvicorn
import platform

from pyapi.settings import settings

def main() -> None:
    """Entrypoint of the application."""
    # Windows 系統或開發模式使用 uvicorn
    if platform.system().lower() == "windows" or settings.reload:
        uvicorn.run(
            "pyapi.web.application:get_app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.value.lower(),
            factory=True,
        )
    else:
        # 只有在 Unix/Linux 系統且非開發模式才使用 gunicorn
        try:
            from pyapi.gunicorn_runner import GunicornApplication
            GunicornApplication(
                "pyapi.web.application:get_app",
                host=settings.host,
                port=settings.port,
                workers=settings.workers_count,
                factory=True,
                accesslog="-",
                loglevel=settings.log_level.value.lower(),
                access_log_format='%r "-" %s "-" %Tf',
            ).run()
        except ImportError:
            # 如果 gunicorn 不可用，回退到 uvicorn
            uvicorn.run(
                "pyapi.web.application:get_app",
                host=settings.host,
                port=settings.port,
                workers=1,  # uvicorn 單工作模式
                log_level=settings.log_level.value.lower(),
                factory=True,
            )

if __name__ == "__main__":
    main()