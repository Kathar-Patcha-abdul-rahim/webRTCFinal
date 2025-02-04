from time import sleep

from appium import webdriver as appium_webdriver
from appium.options.common import AppiumOptions
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ✅ WebRTC App URL (Update with actual deployed URL if different)
pc_webrtc_url = "http://localhost:3000"  # WebRTC app for PC
mobile_webrtc_url = "http://10.0.2.2:3000"  # WebRTC app for Android emulator
#
# # ==============================
# # 🚀 Mobile Chrome - Appium Setup
# # ==============================
# Define capabilities
mobile_capabilities = {
    "platformName": "Android",
    "deviceName": "emulator-5554",  # Change based on your emulator/device
    "browserName": "Chrome",
    "chromeDriverExecutable": "appium-tests/Android/chromedriver.exe",
    "automationName": "UiAutomator2",  # Recommended for Android
    "platformVersion": "15.0",  # Specify your Android version
    "noReset": True,  # Optional, depending on your use case
    "chromeOptions": {
        "args": [
            "--use-fake-ui-for-media-stream",  # Auto-grant media access
            "--use-fake-device-for-media-stream"  # Use fake devices for media
        ]}
}

print(mobile_capabilities)
# Initialize Appium WebDriver for Mobile Chrome
appium_options = AppiumOptions()
appium_options.load_capabilities(mobile_capabilities)
mobile_driver = appium_webdriver.Remote("http://localhost:4723/wd/hub", options=appium_options)
mobile_driver.get(mobile_webrtc_url)

# 🎯 Enter Partner ID and Start Call (Mobile)
WebDriverWait(mobile_driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/h2')))
mobile_partner_id = mobile_driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/h2').text

# Simulate a touch action to activate the mobile driver
def activate_mobile_driver(driver):
    # Example: Tap on coordinates (100, 200) on the screen
    touch = PointerInput(kind="touch", name="finger")

    # Initialize ActionBuilder with the touch input source
    actions = ActionBuilder(driver, mouse=touch)

    # Define the action sequence
    actions.pointer_action.move_to_location(100, 200)  # Move to coordinates (100, 200)
    actions.pointer_action.pointer_down()  # Simulate touch press
    actions.pointer_action.pointer_up()  # Simulate touch release

    # Perform the action sequence
    actions.perform()

# ==============================
# 🖥️ Desktop Chrome - Selenium Setup
# ==============================
chrome_driver_path = "windows/chromedriver.exe"  # Update with the correct path to ChromeDriver
# Allow real media devices (no fake stream setup)
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Auto-grant media access
chrome_options.add_argument("--disable-web-security")  # Disable security to prevent blocking of media devices

chrome_service = ChromeService(executable_path=chrome_driver_path)
desktop_driver = selenium_webdriver.Chrome(service=chrome_service, options=chrome_options)
desktop_driver.get(pc_webrtc_url)

# 🎯 Enter Partner ID and Start Call (PC)
WebDriverWait(desktop_driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/input')))
desktop_partner_id = desktop_driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/input')
print("Mobile Partner ID: ", mobile_partner_id.split(':')[1].strip())
desktop_partner_id.send_keys(mobile_partner_id.split(':')[1].strip())
activate_mobile_driver(mobile_driver)
desktop_driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/button').click()

# Handle camera permission popup
try:
    WebDriverWait(desktop_driver, 10).until(EC.alert_is_present())
    alert = Alert(desktop_driver)
    alert.accept()  # Accept the permission popup
    print("Camera permission granted.")
except:
    print("No camera permission popup.")

# ==============================
# 📹 Verify WebRTC Video Stream
# ==============================
WebDriverWait(mobile_driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "video")))
WebDriverWait(desktop_driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "video")))

sleep(5)
video_element_mobile = mobile_driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/video[2]')
video_element_desktop = desktop_driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/video[1]')

# ==============================
# 📹 Verify WebRTC Video Stream
# ==============================
def is_video_playing(driver, video_element):
    script = """
        return arguments[0].paused === false && arguments[0].readyState >= 2;
    """
    return driver.execute_script(script, video_element)


# Check video playing status
mobile_video_playing = is_video_playing(mobile_driver, video_element_mobile)
desktop_video_playing = is_video_playing(desktop_driver, video_element_desktop)


if mobile_video_playing and desktop_video_playing:
    print("✅ WebRTC Video Streams Connected Successfully!")
else:
    print("❌ WebRTC Stream Verification Failed!")

# Cleanup
mobile_driver.quit()
desktop_driver.quit()
