"""
Home Page Object for sample mobile application
Demonstrates navigation and common app functionality
"""

import allure
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from framework.base_page import BasePage
from framework.test_logger import get_test_logger


class HomePage(BasePage):
    """
    Home page object for mobile application
    """

    def __init__(self):
        super().__init__()
        self.logger = get_test_logger(self.__class__.__name__)

        # Page locators
        self.cart_button = (By.ID, "cart_button")
        self.menu_button = (By.ID, "menu_button")
        self.add_to_cart_button = (By.ID, "add_to_cart_button")
        self.logout_button = (By.ID, "test_button")
        self.privacy_text= (By.XPATH, '//*[text()="Terms of Service | Privacy Policy"]')

        # Android specific locators
        self.android_locators = {
            "cart_button": (AppiumBy.ACCESSIBILITY_ID, "test-Cart"),
            "menu_button": (AppiumBy.ACCESSIBILITY_ID, "test-Menu"),
            "add_to_cart_button": (AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART"),
            "logout_button": (AppiumBy.ACCESSIBILITY_ID, "test-LOGOUT"),
            "privacy_text": (AppiumBy.XPATH, '//*[@text="Terms of Service | Privacy Policy"]')
        }

        # iOS specific locators
        self.ios_locators = {
            "cart_button": (AppiumBy.ACCESSIBILITY_ID, "test-Cart"),
            "menu_button": (AppiumBy.ACCESSIBILITY_ID, "test-Menu"),
            "add_to_cart_button": (AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART"),
            "logout_button": (AppiumBy.ACCESSIBILITY_ID, "test-LOGOUT"),
            "privacy_text": (AppiumBy.XPATH, '//*[@text="Terms of Service | Privacy Policy"]')
        }

    def get_platform_locator(self, element_name: str):
        """Get platform-specific locator"""
        device_info = self.driver.capabilities.get('platformName', '').lower()

        if device_info == 'android' and element_name in self.android_locators:
            return self.android_locators[element_name]
        elif device_info == 'ios' and element_name in self.ios_locators:
            return self.ios_locators[element_name]
        else:
            return getattr(self, element_name)

    @allure.step("Wait for home page to load")
    def wait_for_home_page_load(self, timeout: int = 30) -> bool:
        """
        Wait for home page to load completely

        Args:
            timeout: Wait timeout in seconds

        Returns:
            True if page loaded, False otherwise
        """
        self.logger.step("Waiting for home page to load")

        cart_locator = self.get_platform_locator("cart_button")
        if self.wait_for_element_visible(cart_locator, timeout):
            self.logger.info("Home page loaded successfully")
            return True
        else:
            self.logger.error("Home page failed to load within timeout")
            return False

    @allure.step("Open menu")
    def open_menu(self) -> bool:
        """
        Open the navigation menu

        Returns:
            True if successful, False otherwise
        """
        self.logger.action("Opening navigation menu")

        menu_locator = self.get_platform_locator("menu_button")
        success = self.click(menu_locator)

        if success:
            self.logger.info("Menu opened successfully")
        else:
            self.logger.error("Failed to open menu")

        return success


    @allure.step("Logout from application")
    def logout(self) -> bool:
        """
        Perform logout from the application

        Returns:
            True if successful, False otherwise
        """
        self.logger.action("Logging out from application")

        logout_locator = self.get_platform_locator("logout_button")
        success = self.click(logout_locator)

        if success:
            self.logger.info("Logout successful")
        else:
            self.logger.error("Failed to logout")

        return success

    @allure.step("Verify home page elements")
    def verify_home_page_elements(self) -> bool:
        """
        Verify all expected elements are present on home page

        Returns:
            True if all elements are present, False otherwise
        """
        self.logger.verification("Verifying home page elements", True)

        required_elements = [
            ("menu_button", self.get_platform_locator("menu_button")),
            ("cart_button", self.get_platform_locator("cart_button")),
            ("add_to_cart_button", self.get_platform_locator("add_to_cart_button"))
        ]

        all_present = True
        for element_name, locator in required_elements:
            is_present = self.is_element_present(locator)
            self.logger.verification(f"{element_name} element present", is_present)
            if not is_present:
                all_present = False

        self.logger.verification("All home page elements present", all_present)
        return all_present

    @allure.step("Scroll to footer")
    def scroll_to_footer(self) -> bool:
        """
        Scroll to footer of the page

        Returns:
            True if successful, False otherwise
        """
        self.logger.action("Scrolling to footer")
        privacy_locator = self.get_platform_locator("privacy_text")
        return self.scroll_to_element(privacy_locator)

        # return self.scroll_to_element(self.privacy_text)

    @allure.step("Check the footer")
    def check_footer_elements(self) -> bool:
        """
        Check if footer elements are visible

        Returns:
            True if successful, False otherwise
        """
        self.logger.action("Verifying footer elements")
        privacy_locator = self.get_platform_locator("privacy_text")
        return self.is_element_visible(privacy_locator)


