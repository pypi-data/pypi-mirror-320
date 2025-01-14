import random

# -----------------------------------------------------------------------------------------------------------------
# (*) 미국 타임존
#   - Eastern Time (ET) 
#     timezone = 'America/New_York'
#   - Central Time (CT) 
#     timezone = 'America/Chicago'
#   - Mountain Time (MT) 
#     timezone = 'America/Denver'
#   - Pacific Time (PT) 
#     timezone = 'America/Los_Angeles'

# -----------------------------------------------------------------------------------------------------------------
# viewport : 브라우저 렌더링 영역의 크기를 설정. 사용자 환경 위장 (해상도 조작)
# window.outerWidth/Height (브라우저 전체) : 브라우저 실제 창 크기 조작 (headless 봇 탐지 회피)
def get_random_viewport():
    viewports = [
        {'width': 1920, 'height': 1080},    # Full HD
        {'width': 1600, 'height': 900},
        {'width': 1366, 'height': 768},
        {'width': 1440, 'height': 900},
        {'width': 1280, 'height': 800},
        {'width': 1536, 'height': 864},     # Laptop
        {'width': 1280, 'height': 720},     # 720p : 데스크톱 기준 해상도(1280x720 이상)를 설정하는 것이 안전
        #
        #
        # {'width': 1024, 'height': 1366}   # iPad Pro
        # {'width': 810, 'height': 1080},   # iPad Mini
        # {'width': 414, 'height': 896},    # iPhone XR
        # {'width': 390, 'height': 844},    # iPhone 14 Pro Max
        # {'width': 375, 'height': 667},    # iPhone SE
    ]
    outsize = random.choice(viewports)
    insize = {'width': outsize['width'], 'height': outsize['height'] - 120}
    return outsize, insize

# -----------------------------------------------------------------------------------------------------------------
# def get_random_viewport():
#     desktop_viewports = [
#         {'width': 1920, 'height': 1080},
#         {'width': 1600, 'height': 900},
#         {'width': 1280, 'height': 800}
#     ]
#     mobile_viewports = [
#         {'width': 390, 'height': 844},
#         {'width': 414, 'height': 896}
#     ]
#     # 데스크톱 70%, 모바일 30%
#     return random.choices(desktop_viewports + mobile_viewports, weights=[7, 7, 7, 3, 3])[0]

# -----------------------------------------------------------------------------------------------------------------
# 이게 다양해지면, 200 ok 가 나와도, html classid 가 바뀌어 파싱이 오류 (모바일 해상도는 삭제함)
user_agents = [
    # Windows - Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    # Windows - Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
    # Windows - Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.61",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.2151.58",
    # macOS - Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # macOS - Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    # macOS - Firefox
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) Gecko/20100101 Firefox/117.0",
    # Linux - Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # Linux - Firefox
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    #
    #
    # (*) iPhone - Safari
    # "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    # "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
    # (*) iPad - Safari
    # "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    # (*) Android - Chrome
    # "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    # "Mozilla/5.0 (Linux; Android 11; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
    # (*) Android - Firefox
    # "Mozilla/5.0 (Android 11; Mobile; rv:117.0) Gecko/117.0 Firefox/117.0",
    # (*) Android - Edge
    # "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36 EdgA/119.0.0.0",
    # (*) Other
    # "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

# -----------------------------------------------------------------------------------------------------------------
# 리퍼러가 요청마다 바뀌면 오히려 탐지될 수 있습니다.
# referers = [
#     "https://www.google.com",
#     "https://www.bing.com",
#     "https://www.yahoo.com",
#     "https://duckduckgo.com"
# ]
# referers = [
#     "https://news.google.com",
#     "https://www.nytimes.com",
#     "https://www.reddit.com",
#     "https://www.wikipedia.org"
# ]
#
# "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.7,en;q=0.6",
#
# headers = {
#     "User-Agent": random.choice(user_agents),
#     "Referer": random.choice(referers),  # 리퍼러 랜덤 설정
#     "Accept-Language": "en-US,en;q=0.9",
#     "Connection": "keep-alive"
# }

# -----------------------------------------------------------------------------------------------------------------
# proxies = {
#     'http': 'http://username:password@proxy_server:port',
#     'https': 'https://username:password@proxy_server:port'
# }
