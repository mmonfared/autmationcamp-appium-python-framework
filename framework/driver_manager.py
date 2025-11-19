"""
Driver Manager for Appium Mobile Testing Framework
Handles driver initialization, configuration, and cleanup
"""

import os
import logging
import yaml
from typing import Optional, Dict, Any
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException


class DriverManager:
    """
    Manages Appium WebDriver instances for mobile testing
    """
    _instance = None
    _driver = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DriverManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        self.driver = None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        # Try both .yaml and .yml extensions
        config_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yml'))
        ]

        for config_path in config_paths:
            try:
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    self.logger.info(f"Configuration loaded from: {config_path}")
                    return config
            except FileNotFoundError:
                continue
            except yaml.YAMLError as e:
                self.logger.error(f"Error parsing configuration file {config_path}: {e}")
                return {}

        # If no config file found
        self.logger.warning("No configuration file found. Using default settings.")
        return {}

    def create_android_driver(self, app_path: Optional[str] = None, **kwargs) -> webdriver.Remote:
        """
        Create Android driver with UiAutomator2

        Args:
            app_path: Path to the Android app (.apk file)
            **kwargs: Additional capabilities

        Returns:
            Appium WebDriver instance
        """
        android_config = self.config.get('android', {})
        appium_config = self.config.get('appium', {})

        options = UiAutomator2Options()
        options.platform_name = android_config.get('platform_name', 'Android')
        options.device_name = android_config.get('device_name', 'Android Emulator')
        options.platform_version = android_config.get('platform_version', '11.0')
        options.automation_name = android_config.get('automation_name', 'UiAutomator2')
        options.new_command_timeout = android_config.get('new_command_timeout', 300)
        options.no_reset = android_config.get('no_reset', False)
        options.full_reset = android_config.get('full_reset', False)
        options.auto_grant_permissions = android_config.get('auto_grant_permissions', True)
        options.auto_accept_alerts = android_config.get('auto_accept_alerts', True)
        options.app_wait_activity = android_config.get('app_wait_activity', '*')
        options.disable_window_animation = android_config.get('disable_window_animation', True)
        options.ignore_hidden_api_policy_error = android_config.get('ignore_hidden_api_policy_error', True)
        options.uiautomator2_server_install_timeout = 60000
        options.uiautomator2_server_launch_timeout = 60000

        # Added to speed up initialization (when running on real devices/emulators with existing setup)
        # options.skip_server_installation = True
        # options.skip_device_initialization = True


        # Handle app path or app package/activity
        app_package = android_config.get('app_package')
        app_activity = android_config.get('app_activity')
        if app_path:
            options.app = app_path
        elif app_package and app_activity:
            options.app_package = app_package
            options.app_activity = app_activity
        else:
            self.logger.error("Either app path or app package/activity must be provided for Android driver")
            raise ValueError("No app path or package/activity specified for Android driver")


        # Add custom capabilities
        for key, value in kwargs.items():
            setattr(options, key, value)

        server_url = f"http://{appium_config.get('host', 'localhost')}:{appium_config.get('port', 4723)}"

        try:
            self.driver = webdriver.Remote(server_url, options=options)
            DriverManager._driver = self.driver
            self._configure_driver_timeouts()
            self.logger.info("Android driver created successfully")
            return self.driver
        except WebDriverException as e:
            self.logger.error(f"Failed to create Android driver: {e}")
            raise

    def create_ios_driver(self, app_path: Optional[str] = None, **kwargs) -> webdriver.Remote:
        """
        Create iOS driver with XCUITest

        Args:
            app_path: Path to the iOS app (.app or .ipa file)
            **kwargs: Additional capabilities

        Returns:
            Appium WebDriver instance
        """
        ios_config = self.config.get('ios', {})
        appium_config = self.config.get('appium', {})

        options = XCUITestOptions()
        options.platform_name = ios_config.get('platform_name', 'iOS')
        options.device_name = ios_config.get('device_name', 'iPhone Simulator')
        options.platform_version = ios_config.get('platform_version', '15.0')
        options.automation_name = ios_config.get('automation_name', 'XCUITest')
        options.new_command_timeout = ios_config.get('new_command_timeout', 300)
        options.no_reset = ios_config.get('no_reset', False)
        options.full_reset = ios_config.get('full_reset', False)
        options.auto_accept_alerts = ios_config.get('auto_accept_alerts', True)
        options.show_ios_log = ios_config.get('show_ios_log', True)

        if app_path:
            options.app = app_path
        else:
            bundle_id = ios_config.get('bundle_id')
            if bundle_id:
                options.bundle_id = bundle_id

        # Add custom capabilities
        for key, value in kwargs.items():
            setattr(options, key, value)

        server_url = f"http://{appium_config.get('host', 'localhost')}:{appium_config.get('port', 4723)}"

        try:
            self.driver = webdriver.Remote(server_url, options=options)
            DriverManager._driver = self.driver
            self._configure_driver_timeouts()
            self.logger.info("iOS driver created successfully")
            return self.driver
        except WebDriverException as e:
            self.logger.error(f"Failed to create iOS driver: {e}")
            raise

    def _configure_driver_timeouts(self):
        """Configure driver timeouts from configuration"""
        if not self.driver:
            return

        appium_config = self.config.get('appium', {})

        # Set implicit wait
        implicit_wait = appium_config.get('implicit_wait', 10)
        self.driver.implicitly_wait(implicit_wait)

        # Note: Page load timeout and script timeout are not supported by Android UiAutomator2 driver
        # These timeouts are only needed for web browser contexts, not native mobile apps

        self.logger.info(f"Driver timeouts configured - Implicit: {implicit_wait}s")

    def configure_webview_timeouts(self):
        """Configure timeouts specifically for webview context"""
        if not self.driver:
            return

        try:
            current_context = self.driver.current_context
            if "WEBVIEW" in current_context or "CHROMIUM" in current_context:
                page_load_timeout = self.config.get('appium', {}).get('page_load_timeout', 30)
                self.driver.set_page_load_timeout(page_load_timeout)
                self.logger.info(f"Webview page load timeout set: {page_load_timeout}s")
        except Exception as e:
            self.logger.debug(f"Could not set webview timeouts: {e}")

    def get_driver(self) -> Optional[webdriver.Remote]:
        """Get the current driver instance"""
        return DriverManager._driver

    def quit_driver(self):
        """Quit the current driver instance"""
        if DriverManager._driver:
            try:
                DriverManager._driver.quit()
                self.logger.info("Driver quit successfully")
            except Exception as e:
                self.logger.error(f"Error quitting driver: {e}")
            finally:
                self.driver = None
                DriverManager._driver = None

    def restart_driver(self, platform: str, app_path: Optional[str] = None, **kwargs):
        """
        Restart the driver

        Args:
            platform: 'android' or 'ios'
            app_path: Path to the app file
            **kwargs: Additional capabilities
        """
        self.quit_driver()

        if platform.lower() == 'android':
            return self.create_android_driver(app_path, **kwargs)
        elif platform.lower() == 'ios':
            return self.create_ios_driver(app_path, **kwargs)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def wait_for_element(self, locator: tuple, timeout: int = 30) -> bool:
        """
        Wait for element to be present and visible

        Args:
            locator: Tuple of (By, locator_value)
            timeout: Wait timeout in seconds

        Returns:
            True if element found, False otherwise
        """
        if not self.driver:
            return False

        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            self.logger.warning(f"Element not found within {timeout} seconds: {locator}")
            return False

    def is_element_present(self, locator: tuple) -> bool:
        """
        Check if element is present in the DOM

        Args:
            locator: Tuple of (By, locator_value)

        Returns:
            True if element is present, False otherwise
        """
        if not self.driver:
            return False

        try:
            self.driver.find_element(*locator)
            return True
        except:
            return False

    def take_screenshot(self, filename: Optional[str] = None, driver: Optional[webdriver] = None) -> str:
        """
        Take screenshot of current screen

        Args:
            filename: Optional filename for screenshot
            driver: Optional driver instance to use

        Returns:
            Path to saved screenshot

        """
        # if not self.driver:
        #     raise RuntimeError("No active driver instance")
        if not driver:
            driver = self.driver

        if not filename:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        screenshot_dir = self.config.get('test', {}).get('screenshot_path', 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)

        screenshot_path = os.path.abspath(os.path.join(screenshot_dir, filename))
        # self.driver.save_screenshot(screenshot_path)
        driver.save_screenshot(screenshot_path)
        self.logger.info(f"Screenshot saved: {screenshot_path}")

        return screenshot_path
