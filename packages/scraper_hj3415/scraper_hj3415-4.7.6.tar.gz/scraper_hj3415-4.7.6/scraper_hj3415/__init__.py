from scraper_hj3415.nfscraper import run as nfs
from scraper_hj3415.miscraper import run as mis
from scraper_hj3415.krx300 import krx300 as krx

from dotenv import load_dotenv
from utils_hj3415.tools import get_env_path
from utils_hj3415.logger import mylogger

env_path = get_env_path()
if env_path is None:
    mylogger.warning(f"환경변수 파일(.env)를 찾을수 없습니다. 기본 설정값으로 프로그램을 실행합니다.")
load_dotenv(env_path)

import os
headless = os.getenv('HEADLESS', 'true').lower() in ["true", "1", "yes"]
driver_version = os.getenv('DRIVER_VERSION', '')
browser = os.getenv('BROWSER', 'chrome')