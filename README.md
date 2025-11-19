## Commands:
```bash
 pytest tests/test_login.py::TestLogin::test_valid_login --platform android --alluredir=allure-results --log-cli-level=INFO 
```

```bash
 pytest tests/test_login.py::TestLogin::test_valid_login --platform android --alluredir=allure-results --log-cli-level=INFO --app-path=/saucelabs.apk
```

```bash
 pytest tests/test_home.py::TestHomePage::test_content_scrolling --platform android --alluredir=allure-results --log-cli-level=INFO 
```

### Generate and serve the report
```bash
allure serve allure-results
```

### Or generate static report
```bash
allure generate allure-results --output allure-report --clean
```

```bash
python -m pytest tests/test_login.py::TestLogin::test_valid_login --platform android -v --log-cli-level=DEBUG --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
```

docker run --privileged -d -p 4723:4723 -e EMULATOR_DEVICE="Samsung Galaxy S10" -e APPIUM=true --device /dev/kvm --name android-container -v "C:/Users/mdmon/Docs/AutomationCamp/Projects/automationcamp-appium-python-framework/app/saucelabs.apk:/saucelabs.apk" budtmo/docker-android:emulator_11.0 

# with UI vnc
docker run --privileged -d -p 6080:6080 -p 4723:4723 -e EMULATOR_DEVICE="Samsung Galaxy S10" -e WEB_VNC=true -e APPIUM=true --device /dev/kvm --name android-container -v "C:/Users/mdmon/Docs/AutomationCamp/Projects/automationcamp-appium-python-framework/app/saucelabs.apk:/saucelabs.apk" budtmo/docker-android:emulator_11.0

docker run --privileged -d -p 6080:6080 -p 4723:4723 -e EMULATOR_DEVICE="Samsung Galaxy S10" -e WEB_VNC=true -e APPIUM=true --device /dev/kvm --name android-container -v "${PWD}/app/saucelabs.apk:/saucelabs.apk" budtmo/docker-android:emulator_11.0


# docker compomse
docker compose up -d

# check emulator device status 
docker exec -it android-container cat device_status

docker exec android-container adb shell getprop sys.boot_completed
docker exec android-container adb wait-for-device

# open bash inside container
docker exec -it android-container bash

# current activity
adb shell dumpsys window | grep -E "mCurrentFocus|mFocusedApp"

# check appium logs (inside the container)
tail -f ~/logs/appium.stdout.log