import os
import sys
from loguru import logger
from .constants import *

# --------------------------------------------------------------------------------------------------------------
# (*) 로그 레벨 우선순위 (loguru 기본 레벨)
#   - TRACE     – 5  (가장 낮음, 가장 상세한 로그)
#   - DEBUG     – 10
#   - INFO      – 20
#   - SUCCESS   – 25 (특정 작업이 성공했을 때, 커스텀)
#   - WARNING   – 30
#   - ERROR     – 40
#   - CRITICAL  – 50 (가장 심각한 오류)
# --------------------------------------------------------------------------------------------------------------
# (*) logger.add() : backtrace, diagnose 옵션
#   - logger.exception() 에만 영향을 미침 (주의 logger.error(), critical() 에는 영향 안미침)
#   - backtrace, diagnose 모두 True 가 기본값 : 즉, 모든 스택이 나열되면서 변수까지 보여줌
#
#   - backtrace 옵션 : 스택 나열 (False 로 지정하면 마지막 스택만 나옴)
#   - diagnose 옵션  : 변수 나열 (False 로 지정하면 변수 안나옴)
#
#   - 권장 방법 : backtrace(True), diagnose(False)
#   - Apify 로그는 backtrace(False), diagnose(False) 로 되어있음
# --------------------------------------------------------------------------------------------------------------
def init_log(_file=None, hdr='edk'):
    logger.remove()
    if _file:
        app_dir = f'{os.path.dirname(os.path.abspath(_file))}'
        log_dir = os.path.join(app_dir, SX_LOGS)
        log_file = f'{log_dir}/{hdr}_{{time:YYYY-MM-DD}}.log'
        logger.add(
            sink=log_file,
            format='{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{level: <8}</level> | {message}',
            level='TRACE',
            backtrace=True,     # logger.exception() 에만 해당
            diagnose=False,     # logger.exception() 에만 해당
            rotation='00:00',
            retention='7 days'
        )
    # 화면은 backtrace(False), diagnose(False), 로그파일은 backtrace(True), diagnose(False)
    logger.add(
        sink=sys.stdout,
        format='{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{level: <8}</level> | {message}',
        level='TRACE',
        colorize=True,
        backtrace=False,
        diagnose=False
    )
    logger.level('DEBUG', color='<dim>')
    logger.level('INFO', color='<cyan>')

# --------------------------------------------------------------------------------------------------------------
# import시 공개할 심볼(함수, 클래스, 변수등)을 제한
# 오직 from module import * 에만 영향을 미침
# --------------------------------------------------------------------------------------------------------------
# __all__ = ['logger', 'init_log']