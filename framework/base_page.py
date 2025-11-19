"""
Base Page Object Model for Mobile Testing Framework
Provides common functionality for all page objects
"""

import time
import logging
from typing import List, Optional, Tuple
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException
)
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH

from conftest import driver_manager
from framework.driver_manager import DriverManager


class BasePage:
    """
    Base class for all page objects
    Provides common mobile testing functionality
    """

    def __init__(self):
        self.driver_manager = DriverManager()
        self.driver = self.driver_manager.get_driver()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.wait = WebDriverWait(self.driver, 30) if self.driver else None
        self.actions = ActionBuilder(self.driver) if self.driver else None
        self.finger = PointerInput(POINTER_TOUCH, name="finger") if self.driver else None

    def find_element(self, locator: Tuple[str, str], timeout: int = 30) -> Optional[WebElement]:
        """
        Find a single element with explicit wait

        Args:
            locator: Tuple of (By, locator_value)
            timeout: Wait timeout in seconds

        Returns:
            WebElement if found, None otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"Element found: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Element not found within {timeout} seconds: {locator}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {locator}: {e}")
            return None

    def find_elements(self, locator: Tuple[str, str], timeout: int = 30) -> List[WebElement]:
        """
        Find multiple elements with explicit wait

        Args:
            locator: Tuple of (By, locator_value)
            timeout: Wait timeout in seconds

        Returns:
            List of WebElements
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located(locator))
            self.logger.debug(f"Found {len(elements)} elements: {locator}")
            return elements
        except TimeoutException:
            self.logger.warning(f"No elements found within {timeout} seconds: {locator}")
            return []
        except Exception as e:
            self.logger.error(f"Error finding elements {locator}: {e}")
            return []

    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: int = 30) -> bool:
        """
        Wait for element to be visible

        Args:
            locator: Tuple of (By, locator_value)
            timeout: Wait timeout in seconds

        Returns:
            True if element becomes visible, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            self.logger.error(f"Element not visible within {timeout} seconds: {locator}")
            return False

    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: int = 30) -> Optional[WebElement]:
        """
        Wait for element to be clickable

        Args:
            locator: Tuple of (By, locator_value)
            timeout: Wait timeout in seconds

        Returns:
            WebElement if clickable, None otherwise
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            return element
        except TimeoutException:
            self.logger.error(f"Element not clickable within {timeout} seconds: {locator}")
            return None

    def wait_for_elements_count(self, locator: Tuple[str, str], expected_count: int, timeout: int = 30) -> bool:
        """
        Wait for specific number of elements

        Args:
            locator: Element locator
            expected_count: Expected number of elements
            timeout: Wait timeout

        Returns:
            True if count matches, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            elements = self.driver.find_elements(*locator)
            if len(elements) == expected_count:
                return True
            time.sleep(0.5)
        return False

    def click(self, locator: Tuple[str, str], timeout: int = 30) -> bool:
        """
        Click on an element with retry mechanism

        Args:
            locator: Tuple of (By, locator_value)
            timeout: Wait timeout in seconds

        Returns:
            True if clicked successfully, False otherwise
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                element = self.wait_for_element_clickable(locator, timeout)
                if element:
                    element.click()
                    self.logger.info(f"Clicked on element: {locator}")
                    return True
            except (ElementNotInteractableException, StaleElementReferenceException) as e:
                if attempt < max_attempts - 1:
                    self.logger.warning(f"Click attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(1)
                    continue
                else:
                    self.logger.error(f"Failed to click after {max_attempts} attempts: {locator}")
            except Exception as e:
                self.logger.error(f"Error clicking element {locator}: {e}")
                break
        return False

    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True, timeout: int = 30) -> bool:
        """
        Send keys to an element

        Args:
            locator: Tuple of (By, locator_value)
            text: Text to send
            clear_first: Whether to clear the field first
            timeout: Wait timeout in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.logger.info(f"Sent keys '{text}' to element: {locator}")
                return True
        except Exception as e:
            self.logger.error(f"Error sending keys to element {locator}: {e}")
        return False

    def get_text(self, locator: Tuple[str, str], timeout: int = 30) -> Optional[str]:
        """
        Get text from an element

        Args:
            locator: Tuple of (By, locator_value)
            timeout: Wait timeout in seconds

        Returns:
            Element text if found, None otherwise
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                text = element.text
                self.logger.debug(f"Got text '{text}' from element: {locator}")
                return text
        except Exception as e:
            self.logger.error(f"Error getting text from element {locator}: {e}")
        return None

    def get_element_center(self, element: WebElement) -> Tuple[int, int]:
        """
        Get center coordinates of an element

        Args:
            element: WebElement

        Returns:
            Tuple of (x, y) coordinates
        """
        location = element.location
        size = element.size
        center_x = location['x'] + size['width'] // 2
        center_y = location['y'] + size['height'] // 2
        return center_x, center_y

    def is_element_in_viewport(self, element: WebElement) -> bool:
        """
        Check if element is visible in viewport

        Args:
            element: WebElement to check

        Returns:
            True if element is in viewport, False otherwise
        """
        try:
            location = element.location
            size = element.size
            window_size = self.driver.get_window_size()

            # Check if element is within screen bounds
            if (location['x'] >= 0 and
                    location['y'] >= 0 and
                    location['x'] + size['width'] <= window_size['width'] and
                    location['y'] + size['height'] <= window_size['height']):
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking if element is in viewport: {e}")
            return False

    def get_attribute(self, locator: Tuple[str, str], attribute: str, timeout: int = 30) -> Optional[str]:
        """
        Get attribute value from an element

        Args:
            locator: Tuple of (By, locator_value)
            attribute: Attribute name
            timeout: Wait timeout in seconds

        Returns:
            Attribute value if found, None otherwise
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                value = element.get_attribute(attribute)
                self.logger.debug(f"Got attribute '{attribute}' = '{value}' from element: {locator}")
                return value
        except Exception as e:
            self.logger.error(f"Error getting attribute {attribute} from element {locator}: {e}")
        return None

    def is_element_present(self, locator: Tuple[str, str]) -> bool:
        """
        Check if element is present in the DOM

        Args:
            locator: Tuple of (By, locator_value)

        Returns:
            True if present, False otherwise
        """
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def is_element_visible(self, locator: Tuple[str, str]) -> bool:
        """
        Check if element is visible

        Args:
            locator: Tuple of (By, locator_value)

        Returns:
            True if visible, False otherwise
        """
        try:
            element = self.driver.find_element(*locator)
            return element.is_displayed()
        except NoSuchElementException:
            return False

    def scroll_to_element(self, locator: Tuple[str, str], direction: str = "down") -> bool:
        """
        Scroll to make an element visible

        Args:
            locator: Tuple of (By, locator_value)
            direction: Scroll direction ("up", "down", "left", "right")

        Returns:
            True if element found after scrolling, False otherwise
        """
        max_scrolls = 10
        scroll_count = 0

        while scroll_count < max_scrolls:
            if self.is_element_visible(locator):
                return True

            # Perform scroll based on direction
            if direction.lower() == "down":
                self.scroll_down()
            elif direction.lower() == "up":
                self.scroll_up()
            elif direction.lower() == "left":
                self.scroll_left()
            elif direction.lower() == "right":
                self.scroll_right()

            scroll_count += 1
            time.sleep(0.5)

        self.logger.warning(f"Element not found after {max_scrolls} scroll attempts: {locator}")
        return False

    def scroll_down(self):
        """Scroll down on the screen"""
        size = self.driver.get_window_size()
        start_x = size['width'] / 2
        start_y = size['height'] * 0.8
        end_y = size['height'] * 0.2

        self.actions.pointer_action.move_to_location(start_x, start_y)
        self.actions.pointer_action.pointer_down()
        self.actions.pointer_action.move_to_location(start_x, end_y)
        self.actions.pointer_action.pointer_up()
        self.actions.perform()

    def scroll_up(self):
        # """Scroll up on the screen"""
        size = self.driver.get_window_size()
        start_x = size['width'] / 2
        start_y = size['height'] * 0.2
        end_y = size['height'] * 0.8

        self.actions.pointer_action.move_to_location(start_x, start_y)
        self.actions.pointer_action.pointer_down()
        self.actions.pointer_action.move_to_location(start_x, end_y)
        self.actions.pointer_action.pointer_up()
        self.actions.perform()

    def scroll_left(self):
        """Scroll left on the screen"""
        self.driver.execute_script('mobile: scrollGesture', {
            'left': 500, 'top': 500, 'width': 500, 'height': 0,
            'direction': 'left',
            'percent': 1.0
        })

    def scroll_right(self, distance: int = None):
        """Scroll right on the screen"""
        self.driver.execute_script('mobile: scrollGesture', {
            'left': 500, 'top': 500, 'width': 500, 'height': 0,
            'direction': 'right',
            'percent': 1.0
        })

    def tap(self, x: int, y: int):
        """
        Tap at specific coordinates

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.driver.tap([(x, y)])
        self.logger.info(f"Tapped at coordinates ({x}, {y})")

    def double_tap(self, element: WebElement = None, x: int = None, y: int = None):
        """
        Perform double tap

        Args:
            element: Element to double tap (optional)
            x: X coordinate (if element not provided)
            y: Y coordinate (if element not provided)
        """
        if element:
            center_x, center_y = self.get_element_center(element)
        elif x is not None and y is not None:
            center_x, center_y = x, y
        else:
            raise ValueError("Either element or coordinates must be provided")

        # Perform double tap
        self.driver.execute_script('mobile: doubleClickGesture', {'x': center_x, 'y': center_y})

        self.logger.info(f"Double tapped at coordinates ({center_x}, {center_y})")


    def long_press(self, locator: Tuple[str, str], duration: int = 1000) -> bool:
        """
        Long press on an element

        Args:
            locator: Tuple of (By, locator_value)
            duration: Press duration in milliseconds

        Returns:
            True if successful, False otherwise
        """
        try:
            element = self.find_element(locator)
            if element:
                element_coords = element.location
                self.driver.execute_script('mobile: longClickGesture', {'x': element_coords['x'], 'y': element_coords['y'], 'duration': duration})
                return True
        except Exception as e:
            self.logger.error(f"Error long pressing element {locator}: {e}")
        return False

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000):
        """
        Swipe from one point to another

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Swipe duration in milliseconds
        """
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        self.logger.info(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")

    def hide_keyboard(self):
        """Hide the on-screen keyboard"""
        try:
            self.driver.hide_keyboard()
            self.logger.info("Keyboard hidden")
        except Exception as e:
            self.logger.debug(f"Could not hide keyboard: {e}")

    def get_page_source(self) -> str:
        """Get current page source"""
        return self.driver.page_source

    def wait_for_page_load(self, timeout: int = 30):
        """
        Wait for page to load completely
        This is a basic implementation - override in specific pages as needed
        """
        time.sleep(2)  # Basic wait - can be enhanced with specific conditions

    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """
        Take screenshot of current screen

        Args:
            filename: Optional filename for screenshot

        Returns:
            Path to saved screenshot
        """

        return self.driver_manager.take_screenshot(filename, self.driver)

    def get_current_activity(self) -> Optional[str]:
        """Get current activity (Android only)"""
        try:
            return self.driver.current_activity
        except Exception as e:
            self.logger.debug(f"Could not get current activity: {e}")
            return None

    def get_current_package(self) -> Optional[str]:
        """Get current package (Android only)"""
        try:
            return self.driver.current_package
        except Exception as e:
            self.logger.debug(f"Could not get current package: {e}")
            return None
