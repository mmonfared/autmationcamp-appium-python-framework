"""
Home page functionality test cases
Demonstrates navigation and home page interactions
"""

import pytest
import allure
from tests.pages.home_page import HomePage
from tests.pages.login_page import LoginPage
from framework.test_logger import get_test_logger


@allure.epic("Navigation")
@allure.feature("Home Page")
class TestHomePage:
    """Test cases for home page functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.logger = get_test_logger(self.__class__.__name__)

    def perform_login_setup(self, mobile_driver):
        """Helper method to perform login setup"""
        with allure.step("Setup: Perform login before home page tests"):
            login_page = LoginPage()
            login_success = login_page.login("standard_user", "secret_sauce")
            assert login_success, "Failed to login before home page test"
            self.logger.info("Login successful - ready for home page tests")

    @allure.story("Home Page Load")
    @pytest.mark.smoke
    @pytest.mark.android
    def test_home_page_loads(self, mobile_driver):
        """
        Test that home page loads after login

        Steps:
        1. Perform login (setup)
        2. Wait for home page to load
        3. Verify home page elements are present
        """
        self.logger.start_test("Home Page Load Test")

        # Perform login setup
        self.perform_login_setup(mobile_driver)

        with allure.step("Initialize page objects"):
            home_page = HomePage()

        with allure.step("Wait for home page to load"):
            loaded = home_page.wait_for_home_page_load(timeout=10)
            assert loaded, "Home page failed to load after successful login"

        with allure.step("Verify home page elements"):
            elements_present = home_page.verify_home_page_elements()
            assert elements_present, "Not all home page elements are present"

        self.logger.end_test("Home Page Load Test", "PASSED")

    @allure.story("Menu Navigation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_menu_functionality(self, mobile_driver):
        """
        Test menu functionality

        Steps:
        1. Perform login (setup)
        2. Open navigation menu
        3. Verify menu opens successfully
        """
        self.logger.start_test("Menu Functionality Test")

        # Perform login setup
        self.perform_login_setup(mobile_driver)

        with allure.step("Initialize page objects"):
            home_page = HomePage()

        with allure.step("Wait for home page to load"):
            loaded = home_page.wait_for_home_page_load(timeout=10)
            assert loaded, "Home page failed to load after successful login"

        with allure.step("Open navigation menu"):
            menu_opened = home_page.open_menu()
            assert menu_opened, "Failed to open navigation menu"

        self.logger.end_test("Menu Functionality Test", "PASSED")

    @allure.story("Footer Presence")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_content_scrolling(self, mobile_driver):
        """
        Test scrolling to footer content

        Steps:
        1. Perform login (setup)
        2. Wait for home page to load
        3. Scroll to footer
        4. Verify footer elements are visible
        """
        self.logger.start_test("Content Scrolling Test")

        # Perform login setup
        self.perform_login_setup(mobile_driver)

        with allure.step("Initialize page objects"):
            home_page = HomePage()

        with allure.step("Wait for home page to load"):
            loaded = home_page.wait_for_home_page_load(timeout=10)
            assert loaded, "Home page failed to load after successful login"

        with allure.step("Scroll to the bottom of the page"):
            scrolled = home_page.scroll_to_footer()
            assert scrolled, "Failed to scroll to footer"

        with allure.step("Check footer elements"):
            footer_visible = home_page.check_footer_elements()
            assert footer_visible, "Footer elements are not visible"

        self.logger.end_test("Content Scrolling Test", "PASSED")


@allure.epic("Authentication")
@allure.feature("Logout")
class TestLogout:
    """Test cases for logout functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.logger = get_test_logger(self.__class__.__name__)

    def perform_login_setup(self, mobile_driver):
        """Helper method to perform login setup"""
        with allure.step("Setup: Perform login before logout test"):
            login_page = LoginPage()
            login_success = login_page.login("standard_user", "secret_sauce")
            assert login_success, "Failed to login before logout test"
            self.logger.info("Login successful - ready for logout test")

    @allure.story("User Logout")
    @pytest.mark.smoke
    @pytest.mark.critical
    def test_user_logout(self, mobile_driver):
        """
        Test user logout functionality

        Steps:
        1. Perform login (setup)
        2. Navigate to home page
        3. Open menu
        4. Click logout button
        5. Verify user is logged out (returns to login page)
        """
        self.logger.start_test("User Logout Test")

        # Perform login setup
        self.perform_login_setup(mobile_driver)

        with allure.step("Initialize page objects"):
            home_page = HomePage()
            login_page = LoginPage()

        with allure.step("Wait for home page to load"):
            loaded = home_page.wait_for_home_page_load(timeout=10)
            assert loaded, "Home page failed to load after successful login"

        with allure.step("Open menu"):
            menu_opened = home_page.open_menu()
            assert menu_opened, "Failed to open menu"

        with allure.step("Perform logout"):
            logout_success = home_page.logout()
            assert logout_success, "Failed to logout user"

        with allure.step("Verify return to login page"):
            # After logout, should return to login page
            import time
            time.sleep(2)  # Wait for navigation

            # Verify we're back on login page by checking for login elements
            login_elements_present = login_page.verify_page_elements()
            assert login_elements_present, "Did not return to login page after logout"

            # Take screenshot to verify logout result
            screenshot_path = home_page.take_screenshot("after_logout.png")
            with open(screenshot_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name="Screenshot After Logout",
                    attachment_type=allure.attachment_type.PNG
                )

        self.logger.end_test("User Logout Test", "PASSED")
