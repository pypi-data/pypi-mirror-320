
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.remote.remote_connection import RemoteConnection

from selenium.webdriver.chrome.options import Options as ChromeOptions


DOWNLOAD_PATH = "/Downloads"


def get_chrome_opera_options(
        options, device, proxy_server=None, is_headless=False
):
    """
    --whitelisted-ips   Comma-separated whitelist of remote IPv4
                        addresses which are allowed to connect to ChromeDriver,
                        "" - allowed all

    --use-gl            Select which implementation of GL the GPU process
                        should use.

    --no-sandbox        Disables the sandbox for all process types that
                        are normally sandboxed. Meant to be used as
                        a browser-level switch for testing purposes only.
    """
    if proxy_server:
        options.add_argument(f"--proxy-server={proxy_server}")
    if is_headless:
        options.add_argument('--headless=new')
    options.add_argument("--whitelisted-ips=''")
    options.add_argument("--use-gl=swiftshader")  # for rendering Chrome 79+
    options.add_argument("--no-sandbox")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--no-first-run")
    options.add_argument("--verbose")
    options.add_argument("--enable-logging --v=3")
    options.add_argument("--test-type")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-notifications")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--proxy-bypass-list=*ws*;*chat*")
    prefs = {
        "download.default_directory": DOWNLOAD_PATH,
        "download.directory_upgrade": True,
        'prompt_for_download': False,
        "profile.default_content_setting_values.cookies": 1,
        "profile.block_third_party_cookies": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", [
        "enable-automation",  # disable the automation bar
    ])
    # fix use window.onbeforeunload
    options.enable_bidi = True
    options.unhandled_prompt_behavior = 'ignore'

    if device.__class__.__name__ == "CustomDevice":
        mobile_emulation = {
            "deviceMetrics": {
                "width": device.width,
                "height": device.height,
                "pixelRatio": device.pixel_ratio
            },
            "userAgent": device.user_agent
        }
        options.add_experimental_option(
            "mobileEmulation", mobile_emulation
        )
        # for seeing the emulation window inside browser
        options.add_argument("--window-size=1920,1080")
    else:
        if device.user_agent:
            options.add_argument(f"--user-agent={device.user_agent}")
        options.add_argument(f"--window-size={device.width},{device.height}")
    return options


def get_chrome_options(device, proxy_server=None, is_headless=False):
    options = ChromeOptions()
    return get_chrome_opera_options(options, device, proxy_server, is_headless)


def get_opera_options(device, proxy_server=None):
    options = ChromeOptions()
    opera_options = get_chrome_opera_options(options, device, proxy_server)
    opera_options.binary_location = '/usr/bin/opera'
    return opera_options


def get_firefox_profile(device):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("startup.homepage_welcome_url", "about:blank")
    profile.set_preference(
        "startup.homepage_welcome_url.additional", "about:blank"
    )
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", DOWNLOAD_PATH)
    profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "application/zip"
    )
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("extensions.firebug.allPagesActivation", "on")
    profile.set_preference("extensions.firebug.console.enableSites", "on")
    profile.set_preference(
        "extensions.firebug.defaultPanelName", "console"
    )
    profile.set_preference(
        "extensions.firebug.console.defaultPersist", "true"
    )
    profile.set_preference(
        "extensions.firebug.consoleFilterTypes", "error"
    )
    profile.set_preference("extensions.firebug.showFirstRunPage", False)
    profile.set_preference("extensions.firebug.cookies.enableSites", True)
    if device.user_agent:
        profile.set_preference("general.useragent.override", device.user_agent)
    profile.update_preferences()
    return profile


def get_firefox_options(device):
    """Function available if selenium version > 2.53.0"""
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("-no-remote")
    firefox_options.add_argument(f"-width {device.width}")
    firefox_options.add_argument(f"-height {device.height}")
    return firefox_options


PERFORMANCE_CAPABILITIES = (
    'goog:loggingPrefs',
    {
        "performance": "ALL",
        "server": "ALL",
        "client": "ALL",
        "driver": "ALL",
        "browser": "ALL"
    }
)


CERTS_CAPABILITIES = {
    'acceptSslCerts': True,
    'acceptInsecureCerts': True
}


class RemoteBrowser(webdriver.Remote):

    def __init__(self, *args, client, device, hub, proxy_server,
                 is_headless, **kwargs):
        """
        Initialise a new Remote WebDriver instance
        with connection to Selenium Grid
        """
        capabilities = getattr(DesiredCapabilities, client.upper()).copy()

        if client == "chrome":
            options = get_chrome_options(device, proxy_server, is_headless)
            if is_headless:
                options.accept_insecure_certs = True
        elif client == "firefox":
            options = get_firefox_options(device)
            kwargs['browser_profile'] = get_firefox_profile(device)
        elif client == "opera":
            options = get_opera_options(device)
            capabilities["browserName"] = "opera"
        if client != "safari":
            if proxy_server:
                proxy_capabilities = Proxy(
                    {
                        "httpProxy": proxy_server,
                        'sslProxy': proxy_server,
                        'noProxy': None,
                        "proxyType": ProxyType.MANUAL
                    }
                )
            else:
                proxy_capabilities = Proxy(
                    {
                        "proxyType": ProxyType.DIRECT
                    }
                )
            capabilities.update(proxy_capabilities.to_capabilities())

        options.set_capability(*PERFORMANCE_CAPABILITIES)
        options.set_capability('cloud:options', capabilities)
        kwargs['options'] = options
        remote_connection = RemoteConnection(hub, keep_alive=False)
        remote_connection.set_timeout(300)
        kwargs['command_executor'] = remote_connection
        super().__init__(*args, **kwargs)


class ChromeBrowser(webdriver.Chrome):

    def __init__(self, *args, device, proxy_server, is_headless, **kwargs):
        """
        Initialise a new Chrome WebDriver instance.
        """
        capabilities = DesiredCapabilities.CHROME.copy()

        if proxy_server:
            proxy_capabilities = Proxy(
                {
                    "httpProxy": proxy_server,
                    'sslProxy': proxy_server,
                    'noProxy': None,
                    "proxyType": ProxyType.MANUAL
                }
            )
            capabilities.update(proxy_capabilities.to_capabilities())

        options = get_chrome_options(
            device, proxy_server, is_headless
        )
        if is_headless:
            options.accept_insecure_certs = True
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability(*PERFORMANCE_CAPABILITIES)
        options.set_capability('cloud:options', capabilities)
        kwargs['options'] = options

        super().__init__(*args, **kwargs)


class OperaBrowser(webdriver.Chrome):

    def __init__(self, *args, device, **kwargs):
        """
        Initialise a new Opera WebDriver instance.
        """

        capabilities = DesiredCapabilities.CHROME.copy()
        options = get_opera_options(device)

        kwargs['desired_capabilities'] = capabilities
        kwargs['options'] = options

        super().__init__(*args, **kwargs)


class FirefoxBrowser(webdriver.Firefox):

    def __init__(self, *args, device, **kwargs):
        """
        Initialise a new Firefox WebDriver instance.
        """

        capabilities = DesiredCapabilities.FIREFOX.copy()

        profile = get_firefox_profile(device)
        options = get_firefox_options(device)
        options.set_capability(*PERFORMANCE_CAPABILITIES)
        kwargs['desired_capabilities'] = capabilities
        kwargs['firefox_profile'] = profile
        kwargs['options'] = options

        super().__init__(*args, **kwargs)
