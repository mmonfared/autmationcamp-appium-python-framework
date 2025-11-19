"""
Test utilities for mobile testing framework
Provides helper functions and utilities for common testing tasks
"""

import os
import time
import json
import random
import string
from datetime import datetime
from typing import Any, Dict, Tuple
import logging
from selenium.webdriver.remote.webelement import WebElement


class TestUtils:
    """
    Utility class providing helper methods for mobile testing
    """

    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    # Data Generation Utilities
    def generate_random_string(self, length: int = 10, include_digits: bool = True) -> str:
        """
        Generate random string

        Args:
            length: String length
            include_digits: Whether to include digits

        Returns:
            Random string
        """
        chars = string.ascii_letters
        if include_digits:
            chars += string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def generate_random_email(self, domain: str = "example.com") -> str:
        """
        Generate random email address

        Args:
            domain: Email domain

        Returns:
            Random email address
        """
        username = self.generate_random_string(8, include_digits=True).lower()
        return f"{username}@{domain}"

    def generate_random_phone(self, country_code: str = "+1") -> str:
        """
        Generate random phone number

        Args:
            country_code: Country code prefix

        Returns:
            Random phone number
        """
        area_code = ''.join(random.choice('23456789') for _ in range(3))
        number = ''.join(random.choice(string.digits) for _ in range(7))
        return f"{country_code} ({area_code}) {number[:3]}-{number[3:]}"

    def generate_test_data(self, data_type: str, **kwargs) -> Any:
        """
        Generate test data based on type

        Args:
            data_type: Type of data to generate
            **kwargs: Additional parameters

        Returns:
            Generated test data
        """
        generators = {
            'string': lambda: self.generate_random_string(kwargs.get('length', 10)),
            'email': lambda: self.generate_random_email(kwargs.get('domain', 'example.com')),
            'phone': lambda: self.generate_random_phone(kwargs.get('country_code', '+1')),
            'number': lambda: random.randint(kwargs.get('min', 1), kwargs.get('max', 100)),
            'boolean': lambda: random.choice([True, False]),
            'date': lambda: datetime.now().strftime(kwargs.get('format', '%Y-%m-%d')),
            'time': lambda: datetime.now().strftime(kwargs.get('format', '%H:%M:%S')),
        }

        if data_type in generators:
            return generators[data_type]()
        else:
            raise ValueError(f"Unsupported data type: {data_type}")


    # Screenshot and Visual Utilities
    def take_element_screenshot(self, element: WebElement, filename: str = None) -> str:
        """
        Take screenshot of specific element

        Args:
            element: Element to screenshot
            filename: Optional filename

        Returns:
            Path to saved screenshot
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"element_screenshot_{timestamp}.png"

        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, filename)

        element.screenshot(screenshot_path)
        self.logger.info(f"Element screenshot saved: {screenshot_path}")

        return screenshot_path

    def compare_screenshots(self, image1_path: str, image2_path: str, threshold: float = 0.95) -> bool:
        """
        Compare two screenshots for similarity

        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            threshold: Similarity threshold (0-1)

        Returns:
            True if images are similar, False otherwise
        """
        try:
            from PIL import Image
            import numpy as np

            # Load images
            img1 = Image.open(image1_path).convert('RGB')
            img2 = Image.open(image2_path).convert('RGB')

            # Resize to same dimensions if needed
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)

            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)

            # Calculate similarity
            diff = np.abs(arr1 - arr2)
            similarity = 1 - (np.sum(diff) / (img1.size[0] * img1.size[1] * 255 * 3))

            self.logger.info(f"Screenshot similarity: {similarity:.4f}")
            return similarity >= threshold

        except ImportError:
            self.logger.warning("PIL/Pillow not available for screenshot comparison")
            return False
        except Exception as e:
            self.logger.error(f"Error comparing screenshots: {e}")
            return False

    # Device and App Utilities
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information

        Returns:
            Dictionary with device information
        """
        info = {}
        try:
            info['platform'] = self.driver.capabilities.get('platformName')
            info['platform_version'] = self.driver.capabilities.get('platformVersion')
            info['device_name'] = self.driver.capabilities.get('deviceName')
            info['automation_name'] = self.driver.capabilities.get('automationName')
            info['orientation'] = self.driver.orientation
            info['window_size'] = self.driver.get_window_size()

            # Android specific
            if info['platform'].lower() == 'android':
                info['current_activity'] = getattr(self.driver, 'current_activity', None)
                info['current_package'] = getattr(self.driver, 'current_package', None)

        except Exception as e:
            self.logger.error(f"Error getting device info: {e}")

        return info

    def switch_to_webview(self, webview_name: str = None):
        """
        Switch to web view context

        Args:
            webview_name: Specific webview name (optional)
        """
        try:
            contexts = self.driver.contexts
            self.logger.info(f"Available contexts: {contexts}")

            if webview_name:
                if webview_name in contexts:
                    self.driver.switch_to.context(webview_name)
                    self.logger.info(f"Switched to webview: {webview_name}")
                else:
                    self.logger.error(f"Webview {webview_name} not found")
            else:
                # Switch to first available webview
                webviews = [ctx for ctx in contexts if 'WEBVIEW' in ctx]
                if webviews:
                    self.driver.switch_to.context(webviews[0])
                    self.logger.info(f"Switched to webview: {webviews[0]}")
                else:
                    self.logger.error("No webview contexts available")

        except Exception as e:
            self.logger.error(f"Error switching to webview: {e}")

    def switch_to_native(self):
        """Switch back to native app context"""
        try:
            self.driver.switch_to.context('NATIVE_APP')
            self.logger.info("Switched to native app context")
        except Exception as e:
            self.logger.error(f"Error switching to native context: {e}")

    # Performance Utilities
    def measure_performance(self, func, *args, **kwargs) -> Tuple[Any, float]:
        """
        Measure function execution time

        Args:
            func: Function to measure
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Tuple of (result, execution_time)
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        self.logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result, execution_time

    # Data Management Utilities
    def load_test_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load test data from JSON file

        Args:
            file_path: Path to JSON file

        Returns:
            Dictionary with test data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Test data loaded from {file_path}")
            return data
        except Exception as e:
            self.logger.error(f"Error loading test data from {file_path}: {e}")
            return {}

    def save_test_data(self, data: Dict[str, Any], file_path: str):
        """
        Save test data to JSON file

        Args:
            data: Data to save
            file_path: Path to save file
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Test data saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving test data to {file_path}: {e}")

    # Wait Utilities
    def wait_for_condition(self, condition_func, timeout: int = 30, interval: float = 0.5) -> bool:
        """
        Wait for custom condition to be met

        Args:
            condition_func: Function that returns boolean
            timeout: Wait timeout in seconds
            interval: Check interval in seconds

        Returns:
            True if condition met, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception as e:
                self.logger.debug(f"Condition check failed: {e}")
            time.sleep(interval)

        self.logger.warning(f"Condition not met within {timeout} seconds")
        return False
