import os
import time
import tzlocal
# from datetime import datetime

# --------------------------------------------------------------------------------------------------------------
# # 현재 로컬 타임존 가져오기
# local_tz = tzlocal.get_localzone()
# # 현재 시간과 타임존 출력
# current_time = datetime.now(local_tz)
# print(f"현재 타임존: {local_tz}")
# print(f"현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

# --------------------------------------------------------------------------------------------------------------
def set_timezone(_timezone):
    # 기본 시스템 타임존
    # print('Before Timezone Change:', datetime.now())
    os.environ['TZ'] = _timezone    # 'America/New_York'
    time.tzset()                    # 변경 사항 즉시 적용 (Linux, Mac에서 필요)
    # 타임존 설정 후
    # print('After Timezone Change:', datetime.now())

# --------------------------------------------------------------------------------------------------------------
def get_timezone():
    # 클라우드 서버의 경우 utc 로 되어있음. 'Etc/UTC'
    # 'Asia/Seoul'
    return tzlocal.get_localzone()

# eof