from selenium.webdriver.remote.webdriver import WebDriver
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.902.62 Safari/537.36 Edg/92.0.902.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",

    # Add more User-Agent strings as needed
]

def get(**kwargs) -> WebDriver:
    """
    browser: safari, edge, chrome, firefox...(default: chrome)\n
    driver_version: 크롬 드라이버 버전(default:None)
    headless: (default: True)\n
    geolocation: (default: False)
    """
    browser_type = kwargs.get("browser", "chrome")
    driver_version = kwargs.get("driver_version", None)
    headless = kwargs.get("headless", True)
    geolocation = kwargs.get("geolocation", False)

    if browser_type == 'safari':
        driver = get_safari()
    elif browser_type == 'edge':
        driver = get_edge()
    elif browser_type == 'chrome':
        driver = get_chrome(driver_version=driver_version, headless=headless, geolocation=geolocation)
    elif browser_type == 'firefox':
        driver = get_firefox(headless=headless)
    elif browser_type == 'chromium':
        driver = get_chromium(headless=headless)
    else:
        raise Exception(f"browser type error : {browser_type}")
    return driver


def get_safari() -> WebDriver:
    from selenium import webdriver

    # safari는 headless 모드를 지원하지 않음
    print("For using safari driver. You should safari setting first, 설정/개발자/원격자동화허용 on")
    driver = webdriver.Safari()
    print(f'Get safari driver successfully...')
    return driver


def get_edge() -> WebDriver:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service as EdgeService
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    print(f'Get edge driver successfully...')
    return driver


def get_firefox(headless=True) -> WebDriver:
    # refered from https://www.zenrows.com/blog/selenium-user-agent#what-is-selenium-user-agent
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

    # Set up Firefox profile
    profile = FirefoxProfile()

    # Choose a random User-Agent from the list
    random_user_agent = random.choice(user_agents)
    profile.set_preference("general.useragent.override", random_user_agent)

    # Set up Firefox options
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("-headless")
    firefox_options.profile = profile

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install())
                               , options=firefox_options)

    print(f'Get firefox driver successfully...')
    return driver

def get_chromium(headless=True) -> WebDriver:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Chrome 옵션 설정
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Choose a random User-Agent from the list
    random_user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"--user-agent={random_user_agent}")

    # Chromium 실행 파일 경로 지정 (일반적으로 필요 없음)
    # chrome_options.binary_location = "/usr/bin/chromium"

    # Chromedriver 서비스 설정 (경로 직접 지정)
    service = Service("/usr/bin/chromedriver")

    # WebDriver 생성
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(f'Get chromium driver successfully... headless : {headless}')
    return driver


def get_chrome(driver_version: str = None, temp_dir: str = '', headless=True, geolocation=False) -> WebDriver:
    """ 크롬 드라이버를 반환
    Args:
        driver_version: 드라이버를 못찾는 에러가 가끔있으며 이때는 드라이버 버전을 넣어주면 해결됨
        temp_dir : 크롬에서 다운받은 파일을 저장하는 임시디렉토리 경로(주로 krx에서 사용)
        headless : 크롬 옵션 headless 여부
        geolocation : geolocation 사용여부

    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options


    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")

    # Choose a random User-Agent from the list
    random_user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"--user-agent={random_user_agent}")

    chrome_options.add_argument("--no-sandbox")  # 샌드박스 비활성화 (Linux에서 필요할 수 있음)
    chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화 (Linux에서 필요할 수 있음)

    prefs = {}

    if geolocation:
        # https://copyprogramming.com/howto/how-to-enable-geo-location-by-default-using-selenium-duplicate
        prefs.update(
            {
                'profile.default_content_setting_values': {'notifications': 1, 'geolocation': 1},
                'profile.managed_default_content_settings': {'geolocation': 1},
            }
        )

    if temp_dir != '':
        # print(f'Set temp dir : {temp_dir}')
        # referred from https://stackoverflow.com/questions/71716460/how-to-change-download-directory-location-path-in-selenium-using-chrome
        prefs.update({'download.default_directory': temp_dir,
                      "download.prompt_for_download": False,
                      "download.directory_upgrade": True})

    if prefs:
        chrome_options.add_experimental_option('prefs', prefs)

    # Initialize the Chrome driver
    service = ChromeService(ChromeDriverManager(driver_version=driver_version).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(f'Get chrome driver successfully... headless : {headless}, geolocation : {geolocation}')
    return driver
