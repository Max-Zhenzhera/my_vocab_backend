from app.builder import get_app
from app.core.config import get_app_settings
from app.utils.logging_.config import configure_base_logging
from app.utils.runners.main import run


configure_base_logging()

settings = get_app_settings()
app = get_app(settings)

APP_PATH = 'app.__main__:app'

if __name__ == '__main__':
    run(APP_PATH, settings)
