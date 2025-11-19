"""
Login functionality test cases
Demonstrates how to write tests using the mobile testing framework
"""

import pytest
import allure
from tests.pages.login_page import LoginPage
# from tests.pages.home_page import HomePage
from framework.test_logger import get_test_logger


@allure.epic("Authentication")
@allure.feature("Login")
class TestLogin:
    """Test cases for login functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.logger = get_test_logger(self.__class__.__name__)

    @allure.story("Valid Login")
    @pytest.mark.smoke
    @pytest.mark.critical
    def test_valid_login(self, mobile_driver, test_utils):
        """
        Test successful login with valid credentials

        Steps:
        1. Navigate to login page
        2. Enter valid username
        3. Enter valid password
        4. Click login button
        5. Verify successful login (home page appears)
        """
        self.logger.start_test("Valid Login Test")

        with allure.step("Initialize page objects"):
            login_page = LoginPage()
            # home_page = HomePage()

        with allure.step("Generate test data"):
            # username = test_utils.generate_test_data("email")
            # password = test_utils.generate_test_data("string", length=12)
            username = "standard_user"
            password = "secret_sauce"

            allure.dynamic.parameter("Username", username)
            allure.dynamic.parameter("Password", "***masked***")

        with allure.step("Perform login"):
            assert login_page.navigate_to_login(), "Failed to navigate to login page"
            assert login_page.enter_username(username), "Failed to enter username"
            assert login_page.enter_password(password), "Failed to enter password"
            assert login_page.click_login_button(), "Failed to click login button"

        with allure.step("Verify successful login"):
            # Note: In a real app, you would check for successful navigation to home page
            # For demo purposes, we'll just verify no error message is shown
            assert not login_page.is_error_message_displayed(), "Login should not show error message"

        self.logger.end_test("Valid Login Test", "PASSED")


    @allure.story("Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("username,password,expected_result", [
        ("", "", "Username is required"),
        ("user@test.com", "", "Password is required"),
        ("standard_user", "password123", "Username and password do not match any user in this service."),
    ])
    def test_wrong_credentials(self, mobile_driver, username, password, expected_result):
        """
        Parameterized test for input validation

        Args:
            username: Username to test
            password: Password to test
            expected_result: Expected validation result
        """
        self.logger.start_test(f"Input Validation Test - {expected_result}")

        with allure.step("Initialize page objects"):
            login_page = LoginPage()

        with allure.step(f"Test input validation for {expected_result}"):
            assert login_page.navigate_to_login(), "Failed to navigate to login page"

            if username:
                assert login_page.enter_username(username), "Failed to enter username"

            if password:
                assert login_page.enter_password(password), "Failed to enter password"

            assert login_page.click_login_button(), "Failed to click login button"

        with allure.step("Verify validation behavior"):
            error_displayed = login_page.is_error_message_displayed()
            self.logger.verification("Error message displayed for invalid login", error_displayed)
            assert login_page.get_error_message() == expected_result, "Error message is not as expected"

        self.logger.end_test(f"Input Validation Test - {expected_result}", "PASSED")


@allure.epic("Authentication")
@allure.feature("Login Performance")
class TestLoginPerformance:
    """Performance tests for login functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.logger = get_test_logger(self.__class__.__name__)

    @allure.story("Login Performance")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    def test_login_performance(self, mobile_driver, test_utils, performance_monitor):
        """
        Test login performance

        Verifies that login process completes within acceptable time limits
        """
        self.logger.start_test("Login Performance Test")

        with allure.step("Initialize page objects"):
            login_page = LoginPage()

        with allure.step("Generate test data"):
            # username = test_utils.generate_test_data("email")
            # password = test_utils.generate_test_data("string", length=12)
            username = "standard_user"
            password = "secret_sauce"

        with allure.step("Measure login performance"):
            def perform_login():
                login_page.navigate_to_login()
                login_page.enter_username(username)
                login_page.enter_password(password)
                login_page.click_login_button()
                return True

            result, execution_time = test_utils.measure_performance(perform_login)

            # Assert login completes within 10 seconds
            assert execution_time < 10.0, f"Login took too long: {execution_time:.2f} seconds"

            allure.attach(
                f"Login execution time: {execution_time:.2f} seconds",
                name="Performance Metrics",
                attachment_type=allure.attachment_type.TEXT
            )

        self.logger.end_test("Login Performance Test", "PASSED")
