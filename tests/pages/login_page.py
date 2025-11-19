"""
Login Page Object for sample mobile application
Demonstrates how to create page objects using the framework
"""

import allure
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from framework.base_page import BasePage
from framework.test_logger import get_test_logger


class LoginPage(BasePage):
    """
    Login page object for mobile application
    """

    def __init__(self):
        super().__init__()
        self.logger = get_test_logger(self.__class__.__name__)

        # Page locators
        self.username_field = (By.ID, "username")
        self.password_field = (By.ID, "password")
        self.login_button = (By.ID, "login")
        self.error_message = (By.ID, "error_message")
        self.forgot_password_link = (By.ID, "forgot_password")
        self.signup_button = (By.ID, "signup")

        # Alternative locators for different platforms
        self.android_locators = {
            "username": (AppiumBy.ACCESSIBILITY_ID, "test-Username"),
            "password": (AppiumBy.ACCESSIBILITY_ID, "test-Password"),
            "login_button": (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN"),
            "error_message": (AppiumBy.XPATH, "//*[@content-desc='test-Error message']/android.widget.TextView")

        }

        self.ios_locators = {
            "username": (AppiumBy.ACCESSIBILITY_ID, "username_field"),
            "password": (AppiumBy.ACCESSIBILITY_ID, "password_field"),
            "login_button": (AppiumBy.ACCESSIBILITY_ID, "login_button"),
            "error_message": (AppiumBy.ACCESSIBILITY_ID, "error_message")
        }

    def get_platform_locator(self, element_name: str):
        """
        Get platform-specific locator

        Args:
            element_name: Name of the element

        Returns:
            Platform-specific locator tuple
        """
        device_info = self.driver.capabilities.get('platformName', '').lower()

        if device_info == 'android' and element_name in self.android_locators:
            return self.android_locators[element_name]
        elif device_info == 'ios' and element_name in self.ios_locators:
            return self.ios_locators[element_name]
        else:
            # Fallback to default locators
            return getattr(self, f"{element_name}_field" if element_name in ["username", "password"] else element_name)

    @allure.step("Navigate to login page")
    def navigate_to_login(self):
        """Navigate to the login page"""
        self.logger.step("Navigating to login page")

        # Wait for page to load
        self.wait_for_page_load()

        # Verify login page elements are present
        username_locator = self.get_platform_locator("username")
        if self.wait_for_element_visible(username_locator, timeout=10):
            self.logger.info("Login page loaded successfully")
            return True
        else:
            self.logger.error("Login page did not load properly")
            return False

    @allure.step("Enter username: {username}")
    def enter_username(self, username: str) -> bool:
        """
        Enter username in the username field

        Args:
            username: Username to enter

        Returns:
            True if successful, False otherwise
        """
        self.logger.action(f"Entering username: {username}")

        username_locator = self.get_platform_locator("username")
        success = self.send_keys(username_locator, username, clear_first=True)

        if success:
            self.logger.info("Username entered successfully")
        else:
            self.logger.error("Failed to enter username")

        return success

    @allure.step("Enter password")
    def enter_password(self, password: str) -> bool:
        """
        Enter password in the password field

        Args:
            password: Password to enter

        Returns:
            True if successful, False otherwise
        """
        self.logger.action("Entering password")

        password_locator = self.get_platform_locator("password")
        success = self.send_keys(password_locator, password, clear_first=True)

        if success:
            self.logger.info("Password entered successfully")
        else:
            self.logger.error("Failed to enter password")

        return success

    @allure.step("Click login button")
    def click_login_button(self) -> bool:
        """
        Click the login button

        Returns:
            True if successful, False otherwise
        """
        self.logger.action("Clicking login button")

        login_button_locator = self.get_platform_locator("login_button")
        success = self.click(login_button_locator)

        if success:
            self.logger.info("Login button clicked successfully")
        else:
            self.logger.error("Failed to click login button")

        return success

    @allure.step("Perform login with credentials: {username}")
    def login(self, username: str, password: str) -> bool:
        """
        Perform complete login flow

        Args:
            username: Username to use
            password: Password to use

        Returns:
            True if login successful, False otherwise
        """
        self.logger.step(f"Performing login with username: {username}")

        # Navigate to login page
        if not self.navigate_to_login():
            return False

        # Enter credentials
        if not self.enter_username(username):
            return False

        if not self.enter_password(password):
            return False

        # Click login
        if not self.click_login_button():
            return False

        # Wait for login to complete (either success or error)
        import time
        time.sleep(2)

        # Check for error message
        if self.is_error_message_displayed():
            error_text = self.get_error_message()
            self.logger.error(f"Login failed with error: {error_text}")
            return False

        self.logger.info("Login completed successfully")
        return True

    @allure.step("Check for error message")
    def is_error_message_displayed(self) -> bool:
        """
        Check if error message is displayed

        Returns:
            True if error message is visible, False otherwise
        """
        error_locator = self.get_platform_locator("error_message")
        is_displayed = self.is_element_visible(error_locator)

        self.logger.verification(f"Error message displayed: {is_displayed}", True)
        return is_displayed

    @allure.step("Get error message text")
    def get_error_message(self) -> str:
        """
        Get the error message text

        Returns:
            Error message text or empty string
        """
        error_locator = self.get_platform_locator("error_message")
        error_text = self.get_text(error_locator)

        self.logger.info(f"Error message text: {error_text}")
        return error_text or ""

    @allure.step("Clear login form")
    def clear_form(self):
        """Clear all form fields"""
        self.logger.action("Clearing login form")

        username_locator = self.get_platform_locator("username")
        password_locator = self.get_platform_locator("password")

        # Clear username field
        username_element = self.find_element(username_locator)
        if username_element:
            username_element.clear()

        # Clear password field
        password_element = self.find_element(password_locator)
        if password_element:
            password_element.clear()

        self.logger.info("Login form cleared")

    @allure.step("Verify login page elements")
    def verify_page_elements(self) -> bool:
        """
        Verify all expected elements are present on the login page

        Returns:
            True if all elements are present, False otherwise
        """
        self.logger.verification("Verifying login page elements", True)

        required_elements = [
            ("username", self.get_platform_locator("username")),
            ("password", self.get_platform_locator("password")),
            ("login_button", self.get_platform_locator("login_button"))
        ]

        all_present = True
        for element_name, locator in required_elements:
            is_present = self.is_element_present(locator)
            self.logger.verification(f"{element_name} element present", is_present)
            if not is_present:
                all_present = False

        self.logger.verification("All login page elements present", all_present)
        return all_present
