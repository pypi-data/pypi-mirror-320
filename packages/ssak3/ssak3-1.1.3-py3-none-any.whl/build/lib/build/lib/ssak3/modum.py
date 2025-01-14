import random
import time
from .constants import *
from .block import *

# -----------------------------------------------------------------------------------------------------------------
async def load_cookie(_task_name, _actor):
    kvstore = await _actor.open_key_value_store(name=SX_COOKIE_STORE)
    index = random.randint(0, len(user_agents) - 1)
    cookie_key = f'cookies_{index}'
    # {'cookies': {...}, 'timestamp': 1693698539.1234}
    stored_data = await kvstore.get_value(cookie_key)
    cookies_data = None
    if stored_data:
        stored_timestamp = stored_data.get('timestamp', 0)
        # 1시간(3600초) 이내라면 쿠키 재사용
        if time.time() - stored_timestamp < 3600:
            cookies_data = stored_data.get('cookies')
        else:
            # logger.debug(f'[t] task-{int(_task_name):04d} the cookie has expired as more than 1 hour has passed.')
            await kvstore.set_value(cookie_key, None)   # 기존 쿠키 삭제(또는 set_value(cookie_key, {}) 등)
    return index, cookies_data, kvstore

# -----------------------------------------------------------------------------------------------------------------
async def save_cookie(_context, _index, _kvstore):
    data_to_store = {'cookies': await _context.storage_state(), 'timestamp': time.time()}
    await _kvstore.set_value(f'cookies_{_index}', data_to_store)

# -----------------------------------------------------------------------------------------------------------------
async def set_internal_proxy(_actor, _env_ctx):
    # Apify 플랫폼에서 Actor가 실행될 때, Apify 시스템이 APIFY_PROXY_HOSTNAME, APIFY_PROXY_PORT, APIFY_PROXY_PASSWORD 환경 변수
    # 를 자동으로 주입.
    proxy_configuration = await _actor.create_proxy_configuration(actor_proxy_input=_env_ctx['proxy'])
    return proxy_configuration

# -----------------------------------------------------------------------------------------------------------------
async def set_outernal_proxy(_actor, _env_ctx):
    # mac 로컬에서 실행시에는 password 를 지정해 줘야 함. 즉 이경우에는 외부 프록시 사용하는 경우임.
    proxy_configuration = await _actor.create_proxy_configuration(
        groups=_env_ctx['proxy']['apifyProxyGroups'],
        country_code=_env_ctx['proxy']['apifyProxyCountry'],
        password=_env_ctx['proxy_password']
    )
    return proxy_configuration

# -----------------------------------------------------------------------------------------------------------------
async def set_proxy(_task_name, _config):
    # (*) 환경 변수를 사용하여 내부 프록시를 사용해야 함
    # 외부 프록시 : http://groups-RESIDENTIAL:apify_proxy_u...d@proxy.apify.com:8000
    #
    # 내부 프록시 사용 중
    # http://groups-RESIDENTIAL,country-US:*********@10.0.93.195:8011
    proxy_url = await _config.new_url()

    # {'server': '10.0.93.195:8011', 'username': 'groups-RESIDENTIAL,country-US', 'password': '*********'}
    proxy_ctx = {
        'server': proxy_url.split('@')[-1],                                 # proxy.apify.com:8000
        'username': proxy_url.split('@')[0].split('//')[-1].split(':')[0],  # groups-RESIDENTIAL,country-US, or 'auto'
        'password': proxy_url.split('@')[0].split(':')[-1]                  # apify_proxy_xxxxxxxxxx
    }
    password = proxy_ctx['password']
    masked_password = f"{password[:-30]}{'*' * 30}"  # 마지막 5자리만 남기고 마스킹
    logging_ctx = proxy_ctx.copy()
    logging_ctx['password'] = masked_password
    # logger.debug(f'[t] task-{int(_task_name):04d} using a proxy : {logging_ctx['server']} ({logging_ctx['username']})')
    return proxy_ctx

# -----------------------------------------------------------------------------------------------------------------
# 'America/Los_Angeles', 'Asia/Seoul'
# -----------------------------------------------------------------------------------------------------------------
def browser_context(_task_name, _idx, _browser, _env_ctx, _user_agent, _viewport, _headers, _cookies=None):
    context_params = {
        'user_agent': _user_agent,
        'viewport': _viewport,
        'extra_http_headers': _headers,                 # HTTP 헤더 User-Agent 동기화
        'timezone_id': _env_ctx['country_tz']
    }
    # - launch() 에서 세팅함
    # if _proxy:
    #     context_params['proxy'] = _proxy
    if _cookies:
        context_params['storage_state'] = _cookies
        # logger.debug(f'[t] task-{int(_task_name):04d} reusing stored cookies : (user-agent: {_idx})')
    else:
        # logger.debug(f'[t] task-{int(_task_name):04d} using new cookies : (user-agent: {_idx})')
        pass
    return _browser.new_context(**context_params)

# eof