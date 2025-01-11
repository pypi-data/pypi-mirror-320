from onego import logger

try: import cloudscraper
except ModuleNotFoundError as e:
    logger.danger('To use onego.sessions "cloudscraper" module is required', e)

import onego.sessions.chrome as chrome
from onego.sessions.chrome import SessionChrome

from onego.sessions.get_chrome_version import get_chrome_version, get_chrome_version_soft