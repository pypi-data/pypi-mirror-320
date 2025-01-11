from dotenv import load_dotenv
from utils_hj3415.tools import get_env_path
from utils_hj3415.logger import mylogger

env_path = get_env_path()
if env_path is None:
    mylogger.warning(f"환경변수 파일(.env)를 찾을수 없습니다. 기본 설정값으로 프로그램을 실행합니다.")
load_dotenv(env_path)
