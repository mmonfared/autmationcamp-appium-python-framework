# AutomationCamp Appium Python Framework

A mobile test automation framework built with **Python**, **pytest**, and **Appium**. It uses the Page Object Model (POM) pattern to automate the [Swag Labs mobile app](https://github.com/saucelabs/sample-app-mobile) on Android (and iOS-ready configuration).

## Features

- Page Object Model with a reusable `BasePage` for common mobile interactions (tap, scroll, swipe, etc.)
- Singleton `DriverManager` for Android (UiAutomator2) and iOS (XCUITest) driver lifecycle
- pytest fixtures for driver setup/teardown, screenshots on failure, and Allure attachments
- YAML-based configuration (`config/config.yml`)
- Allure and HTML reporting
- Docker-based Android emulator with Appium for local and CI runs
- GitHub Actions workflow for automated test execution and report publishing

## Project Structure

```
automationcamp-appium-python-framework/
├── config/
│   └── config.yml              # Appium, platform, logging, and Allure settings
├── framework/
│   ├── base_page.py            # Base page object with shared mobile actions
│   ├── driver_manager.py       # Appium driver creation and management
│   ├── test_logger.py          # Structured logging utilities
│   └── test_utils.py           # Test helpers (data generation, performance, etc.)
├── tests/
│   ├── pages/
│   │   ├── login_page.py       # Login page object
│   │   └── home_page.py        # Home page object
│   ├── test_login.py           # Login and validation tests
│   └── test_home.py            # Home page, menu, scroll, and logout tests
├── app/
│   └── saucelabs.apk           # Swag Labs APK (not included — download separately)
├── conftest.py                 # pytest fixtures and hooks
├── docker-compose.yml          # Docker-Android emulator + Appium stack
├── pytest.ini                  # pytest defaults, markers, and logging
├── requirements.txt
└── .github/workflows/main.yml  # CI pipeline
```

## Prerequisites

- **Python 3.8+**
- **Docker** with `/dev/kvm` support (Linux) or Docker Desktop (Windows/macOS with virtualization)
- **Allure CLI** (for viewing reports locally)
- **Swag Labs APK** — place it at `app/saucelabs.apk`  
  Download from: https://github.com/saucelabs/sample-app-mobile/releases

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd automationcamp-appium-python-framework

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Android Emulator

### Option 1: Docker Compose (recommended)

```bash
docker compose up -d
```

This starts a `budtmo/docker-android` container with Appium on port **4723** and mounts `./app/saucelabs.apk` into the container at `/saucelabs.apk`.

### Option 2: Docker run (manual)

**Headless (Appium only):**

```bash
docker run --privileged -d -p 4723:4723 \
  -e EMULATOR_DEVICE="Samsung Galaxy S10" \
  -e APPIUM=true \
  --device /dev/kvm \
  --name android-container \
  -v "${PWD}/app/saucelabs.apk:/saucelabs.apk" \
  budtmo/docker-android:emulator_11.0
```

**With VNC UI (view emulator in browser at http://localhost:6080):**

```bash
docker run --privileged -d -p 6080:6080 -p 4723:4723 \
  -e EMULATOR_DEVICE="Samsung Galaxy S10" \
  -e WEB_VNC=true \
  -e APPIUM=true \
  --device /dev/kvm \
  --name android-container \
  -v "${PWD}/app/saucelabs.apk:/saucelabs.apk" \
  budtmo/docker-android:emulator_11.0
```

> **Windows path example:** replace `${PWD}/app/saucelabs.apk` with your full path, e.g.  
> `"C:/Projects/automationcamp-appium-python-framework/app/saucelabs.apk:/saucelabs.apk"`

### Emulator troubleshooting

```bash
# Check emulator device status
docker exec -it android-container cat device_status

# Wait for device and confirm boot completed
docker exec android-container adb wait-for-device
docker exec android-container adb shell getprop sys.boot_completed

# Open a shell inside the container
docker exec -it android-container bash

# Check current activity (run inside container)
adb shell dumpsys window | grep -E "mCurrentFocus|mFocusedApp"

# Tail Appium logs (inside the container)
tail -f ~/logs/appium.stdout.log

# Stop the stack
docker compose down
```

## Running Tests

Make sure the emulator is running and Appium is reachable at `http://localhost:4723` before executing tests.

### Run a single test

```bash
pytest tests/test_login.py::TestLogin::test_valid_login --platform android --alluredir=allure-results --log-cli-level=INFO
```

### Run with explicit app path (required when using Docker)

When the APK is mounted inside the container at `/saucelabs.apk`:

```bash
pytest tests/test_login.py::TestLogin::test_valid_login --platform android --alluredir=allure-results --log-cli-level=INFO --app-path=/saucelabs.apk
```

### Run home page scroll test

```bash
pytest tests/test_home.py::TestHomePage::test_content_scrolling --platform android --alluredir=allure-results --log-cli-level=INFO
```

### Run with verbose debug logging

```bash
python -m pytest tests/test_login.py::TestLogin::test_valid_login --platform android -v --log-cli-level=DEBUG --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
```

### Run the full suite

```bash
pytest --platform android --app-path=/saucelabs.apk --alluredir=allure-results --log-cli-level=INFO
```

### CLI options

| Option | Default | Description |
|---|---|---|
| `--platform` | `android` | Target platform: `android` or `ios` |
| `--app-path` | — | Path to `.apk` (Android) or `.app`/`.ipa` (iOS) |
| `--device-name` | from config | Override device name |
| `--platform-version` | from config | Override OS version |
| `--appium-host` | `localhost` | Appium server host |
| `--appium-port` | `4723` | Appium server port |
| `--no-reset` | `false` | Preserve app state between sessions |
| `--full-reset` | `false` | Uninstall and reinstall the app |

### Test markers

Filter tests using pytest markers defined in `pytest.ini`:

```bash
pytest -m smoke --platform android --app-path=/saucelabs.apk
pytest -m "not slow" --platform android --app-path=/saucelabs.apk
```

Available markers: `smoke`, `regression`, `android`, `ios`, `slow`, `critical`, `api`, `ui`

## Reports

Test runs produce output in several locations:

| Output | Path |
|---|---|
| Allure results | `allure-results/` |
| Allure report | `allure-report/` |
| HTML report | `reports/pytest_report.html` |
| Logs | `logs/pytest.log`, `logs/test_execution.log` |
| Failure screenshots | `screenshots/` |

### Generate and serve the Allure report

```bash
allure serve allure-results
```

### Generate a static Allure report

```bash
allure generate allure-results --output allure-report --clean
```

## Configuration

Edit `config/config.yml` to adjust:

- **Appium server** — host, port, timeouts
- **Android/iOS capabilities** — device name, platform version, app package/activity
- **Test settings** — screenshot on failure, retry count, parallel execution
- **Logging** — level, format, file path
- **Allure** — results and report directories

Default Android app under test:

| Setting | Value |
|---|---|
| App package | `com.swaglabsmobileapp` |
| App activity | `.MainActivity` |
| Platform version | `11.0` |

## CI/CD

The GitHub Actions workflow (`.github/workflows/main.yml`) runs on pushes to `master`:

1. Starts the Docker-Android stack via `docker compose up -d`
2. Waits for Appium and the emulator to be ready
3. Installs Python dependencies and Allure CLI
4. Runs the full pytest suite with `--app-path=/saucelabs.apk`
5. Generates and uploads Allure reports (artifact + GitHub Pages)
6. Collects debug logs on failure

## Writing New Tests

1. Create a page object in `tests/pages/` extending `BasePage`
2. Define locators and page-specific methods
3. Write test classes in `tests/` using the `mobile_driver` and `test_utils` fixtures
4. Decorate with `@allure` annotations and pytest markers as needed

Example:

```python
import allure
import pytest
from tests.pages.login_page import LoginPage

@allure.feature("Login")
class TestLogin:
    @pytest.mark.smoke
    def test_valid_login(self, mobile_driver):
        login_page = LoginPage()
        assert login_page.login("standard_user", "secret_sauce")
```
## Tutorial (in Persian):

https://www.youtube.com/playlist?list=PLAYzZ7q3hc54

## Author:

Moe Monfared

https://github.com/mmonfared

https://linkedin.com/in/monfared/
