"""
pytest configuration and fixtures for mobile testing framework
Provides setup, teardown, and common testing utilities
"""

import os
import sys
import pytest
import logging
import allure
from datetime import datetime
from typing import Optional, Dict, Any

# Add framework to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'framework'))

from framework.driver_manager import DriverManager
from framework.test_logger import setup_logging
from framework.test_utils import TestUtils


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        choices=["android", "ios"],
        help="Platform to run tests on: android or ios"
    )
    parser.addoption(
        "--app-path",
        action="store",
        default=None,
        help="Path to the mobile app file (.apk for Android, .app/.ipa for iOS)"
    )
    parser.addoption(
        "--device-name",
        action="store",
        default=None,
        help="Device name to run tests on"
    )
    parser.addoption(
        "--platform-version",
        action="store",
        default=None,
        help="Platform version to run tests on"
    )
    parser.addoption(
        "--appium-host",
        action="store",
        default="localhost",
        help="Appium server host"
    )
    parser.addoption(
        "--appium-port",
        action="store",
        default="4723",
        help="Appium server port"
    )
    parser.addoption(
        "--no-reset",
        action="store_true",
        default=False,
        help="Don't reset app state between sessions"
    )
    parser.addoption(
        "--full-reset",
        action="store_true",
        default=False,
        help="Perform full reset (uninstall and reinstall app)"
    )


def pytest_configure(config):
    """Configure pytest environment"""
    # Setup logging
    setup_logging()

    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("allure-results", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Register custom markers
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "android: mark test for Android platform")
    config.addinivalue_line("markers", "ios: mark test for iOS platform")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "critical: mark test as critical functionality")
    config.addinivalue_line("markers", "api: mark test for API testing")
    config.addinivalue_line("markers", "ui: mark test for UI testing")


def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    # Store config for later use
    session.config._allure_env_created = False


@pytest.fixture(scope="session", autouse=True)
def create_allure_environment(request):
    """Create Allure environment file after allure directory is ready"""
    config = request.config

    # Only create once per session
    if hasattr(config, '_allure_env_created') and config._allure_env_created:
        return

    try:
        # Ensure directory exists
        os.makedirs("allure-results", exist_ok=True)

        allure_env_path = os.path.abspath(os.path.join("allure-results", "environment.properties"))

        with open(allure_env_path, "w") as f:
            f.write(f"Platform={config.getoption('--platform')}\n")
            f.write(f"App.Path={config.getoption('--app-path') or 'Not specified'}\n")
            f.write(f"Device.Name={config.getoption('--device-name') or 'Default'}\n")
            f.write(f"Platform.Version={config.getoption('--platform-version') or 'Default'}\n")
            f.write(f"Appium.Host={config.getoption('--appium-host')}\n")
            f.write(f"Appium.Port={config.getoption('--appium-port')}\n")
            f.write(f"Execution.Time={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        config._allure_env_created = True
    except Exception as e:
        # Log error but don't fail tests
        logging.getLogger(__name__).warning(f"Failed to create Allure environment file: {e}")


@pytest.fixture(scope="session")
def test_config(request) -> Dict[str, Any]:
    """Provide test configuration from command line options"""
    return {
        "platform": request.config.getoption("--platform"),
        "app_path": request.config.getoption("--app-path"),
        "device_name": request.config.getoption("--device-name"),
        "platform_version": request.config.getoption("--platform-version"),
        "appium_host": request.config.getoption("--appium-host"),
        "appium_port": request.config.getoption("--appium-port"),
        "no_reset": request.config.getoption("--no-reset"),
        "full_reset": request.config.getoption("--full-reset"),
    }


@pytest.fixture(scope="session")
def driver_manager():
    """Provide driver manager instance"""
    return DriverManager()


@pytest.fixture(scope="function")
def mobile_driver(request, test_config, driver_manager):
    """
    Provide mobile driver instance with automatic setup and teardown
    """
    logger = logging.getLogger("mobile_driver")

    # Prepare driver capabilities
    capabilities = {}
    if test_config["device_name"]:
        capabilities["device_name"] = test_config["device_name"]
    if test_config["platform_version"]:
        capabilities["platform_version"] = test_config["platform_version"]
    if test_config["no_reset"]:
        capabilities["no_reset"] = True
    if test_config["full_reset"]:
        capabilities["full_reset"] = True

    # Create driver based on platform
    try:
        if test_config["platform"].lower() == "android":
            driver = driver_manager.create_android_driver(
                app_path=test_config["app_path"],
                **capabilities
            )
        elif test_config["platform"].lower() == "ios":
            driver = driver_manager.create_ios_driver(
                app_path=test_config["app_path"],
                **capabilities
            )
        else:
            pytest.fail(f"Unsupported platform: {test_config['platform']}")

        logger.info(f"Mobile driver created successfully for {test_config['platform']}")

        # Add driver info to Allure report
        allure.dynamic.parameter("Platform", test_config["platform"])
        allure.dynamic.parameter("Device", test_config.get("device_name", "Default"))
        allure.dynamic.parameter("Platform Version", test_config.get("platform_version", "Default"))

        yield driver

    except Exception as e:
        logger.error(f"Failed to create mobile driver: {e}")
        pytest.fail(f"Driver initialization failed: {e}")

    finally:
        # Cleanup
        try:
            driver_manager.quit_driver()
            logger.info("Mobile driver quit successfully")
        except Exception as e:
            logger.error(f"Error during driver cleanup: {e}")


@pytest.fixture(scope="function")
def test_utils(mobile_driver):
    """Provide test utilities"""
    return TestUtils(mobile_driver)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results and take screenshots on failure"""
    outcome = yield
    report = outcome.get_result()

    # Only process on test call (not setup/teardown)
    if report.when == "call":
        logger = logging.getLogger("pytest_hook")

        # Get the driver from fixtures if available
        driver_manager = None
        if hasattr(item, "funcargs") and "mobile_driver" in item.funcargs:
            try:
                driver_manager = DriverManager()
                driver = driver_manager.get_driver()
            except:
                driver = None

        # Take screenshot on failure
        if report.failed and driver:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                test_name = item.nodeid.replace("::", "_").replace("/", "_")
                screenshot_name = f"FAILED_{test_name}_{timestamp}.png"
                screenshot_path = driver_manager.take_screenshot(screenshot_name, driver)

                # Attach screenshot to Allure report
                with open(screenshot_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name="Screenshot on Failure",
                        attachment_type=allure.attachment_type.PNG
                    )

                logger.info(f"Screenshot taken for failed test: {screenshot_path}")

            except Exception as e:
                logger.error(f"Failed to take screenshot: {e}")

        # Add test result to Allure
        if report.passed:
            allure.dynamic.severity(allure.severity_level.NORMAL)
        elif report.failed:
            allure.dynamic.severity(allure.severity_level.CRITICAL)
            # Attach page source on failure
            if driver:
                try:
                    page_source = driver.page_source
                    allure.attach(
                        page_source,
                        name="Page Source on Failure",
                        attachment_type=allure.attachment_type.XML
                    )
                except Exception as e:
                    logger.error(f"Failed to attach page source: {e}")


@pytest.fixture(scope="function")
def skip_on_platform(request, test_config):
    """Skip test if running on specific platform"""

    def _skip_on_platform(platform):
        if test_config["platform"].lower() == platform.lower():
            pytest.skip(f"Test skipped on {platform} platform")

    return _skip_on_platform


@pytest.fixture(scope="function")
def only_on_platform(request, test_config):
    """Run test only on specific platform"""

    def _only_on_platform(platform):
        if test_config["platform"].lower() != platform.lower():
            pytest.skip(f"Test only runs on {platform} platform")

    return _only_on_platform


# Parametrize fixtures for data-driven testing
@pytest.fixture(scope="function")
def test_data():
    """Provide test data - can be overridden in specific test files"""
    return {}


# Performance monitoring fixtures
@pytest.fixture(scope="function")
def performance_monitor():
    """Monitor test performance"""
    start_time = datetime.now()

    yield

    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    # Attach performance info to Allure
    allure.attach(
        f"Test execution time: {execution_time:.2f} seconds",
        name="Performance",
        attachment_type=allure.attachment_type.TEXT
    )

#
# # Custom markers
# def pytest_configure(config):
#     """Register custom markers"""
#     config.addinivalue_line("markers", "smoke: mark test as smoke test")
#     config.addinivalue_line("markers", "regression: mark test as regression test")
#     config.addinivalue_line("markers", "android: mark test for Android platform")
#     config.addinivalue_line("markers", "ios: mark test for iOS platform")
#     config.addinivalue_line("markers", "slow: mark test as slow running")
#     config.addinivalue_line("markers", "critical: mark test as critical functionality")
#     config.addinivalue_line("markers", "api: mark test for API testing")
#     config.addinivalue_line("markers", "ui: mark test for UI testing")


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_session():
    """Session-level cleanup"""
    yield

    # Final cleanup
    try:
        driver_manager = DriverManager()
        driver_manager.quit_driver()
    except:
        pass
