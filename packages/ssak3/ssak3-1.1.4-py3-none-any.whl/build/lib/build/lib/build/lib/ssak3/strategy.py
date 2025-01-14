import random

# -----------------------------------------------------------------------------------------------------------------
async def strategy_webdriver(_context):
    # 브라우저 지문 조작 (navigator.webdriver 제거)
    # 구글은 navigator.webdriver 값이 true이면 봇으로 간주
    await _context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

# -----------------------------------------------------------------------------------------------------------------
async def strategy_chrome(_context):
    # window.chrome 속성 추가 (Chrome DevTools 환경 우회)
    # 실제 브라우저에는 window.chrome 객체가 존재하지만, 자동화된 환경에서는 없으므로 이를 추가함
    # - window.chrome : 크롬 개발자 도구(DevTools)에서 사용되는 API와 관련됩니다.
    # - window.navigator.chrome : 브라우저 및 사용자 환경 정보
    await _context.add_init_script("""
        window.chrome = {
            app: {},
            runtime: {},
            loadTimes: function() {},
            csi: function() {}
        };
        window.navigator.chrome = {
            app: {},
            runtime: {},
            loadTimes: function() {},
            csi: function() {}
        };
    """)

# -----------------------------------------------------------------------------------------------------------------
async def strategy_plugin(_context):
    # 플러그인 개수 설정 (빈 배열이면 자동화로 간주)
    await _context.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
    """)

# -----------------------------------------------------------------------------------------------------------------
async def strategy_lang(_context):
    # 언어 설정 (실제 브라우저와 일치)
    await _context.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['ko-KR', 'en-US']
        });
    """)

# -----------------------------------------------------------------------------------------------------------------
async def strategy_tz(_context):
    # 시간대 설정 (Intl API 조작)
    await _context.add_init_script("""
        const timeZone = 'Asia/Seoul';
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
            value: function() {
                return {
                    timeZone: timeZone
                };
            }
        });
    """)

# -----------------------------------------------------------------------------------------------------------------
# WebGL 렌더러 및 벤더 스푸핑 
async def strategy_webgl(_context):
    renderers = [ "NVIDIA GeForce GTX 1650", "AMD Radeon RX 580", "Intel Iris Xe Graphics"]
    vendors = [ "NVIDIA Corporation", "Advanced Micro Devices, Inc.", "Intel Corporation"]
    selected_renderer = random.choice(renderers)
    selected_vendor = random.choice(vendors)
    # f-string에서 중괄호 두 번 사용해 JavaScript 코드 삽입
    await _context.add_init_script(f"""
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return "{selected_renderer}";  // 렌더러 스푸핑
            }}
            if (parameter === 37446) {{
                return "{selected_vendor}";  // 벤더 스푸핑
            }}
            return getParameter(parameter);
        }};
    """)

# -----------------------------------------------------------------------------------------------------------------
async def strategy_canvas(_context):
    # Canvas Fingerprinting 조작
    # 구글은 HTMLCanvasElement를 사용해 브라우저에서 렌더링된 이미지를 기반으로 지문을 생성해 감지
    # 일부 픽셀 값을 수정해 캔버스 지문이 일치하지 않도록 설정
    # if (type === '2d') {  이게 오리지널...type 은 추가함
    await _context.add_init_script("""
        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attributes) {
            if (type === '2d' || type === 'webgl') {
                const context = getContext.call(this, type, attributes);
                const originalGetImageData = context.getImageData;
                context.getImageData = function(x, y, width, height) {
                    const imageData = originalGetImageData.call(this, x, y, width, height);
                    imageData.data[0] = imageData.data[0] ^ 0xff;  // 첫 번째 픽셀 수정
                    return imageData;
                };
            }
            return getContext.call(this, type, attributes);
        };
    """)

# -----------------------------------------------------------------------------------------------------------------
async def strategy_outer(_context, _outer_size):
    # 실제 브라우저처럼 window.outerHeight와 window.outerWidth를 설정해 헤드리스 환경을 감춤
    height = _outer_size['height']
    width = _outer_size['width']
    await _context.add_init_script(f"""
        window.outerHeight = {height};
        window.outerWidth = {width};
    """)

# -----------------------------------------------------------------------------------------------------------------
async def strategy_block(_context, _outer_size):
    await strategy_webdriver(_context)
    await strategy_chrome(_context)
    await strategy_plugin(_context)
    await strategy_lang(_context)
    await strategy_webgl(_context)
    await strategy_canvas(_context)
    await strategy_tz(_context)
    await strategy_outer(_context, _outer_size)

# eof