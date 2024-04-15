from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import os
import zipfile
import glob
import subprocess
import platform

def image_to_stl(file_path):
    download_dir = "./stls"  # Update this path
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    firefox_options = Options()
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", download_dir)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/sla")  # MIME type for STL files
    global driver
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)

    url = 'https://lithophanemaker.com/Night%20Light%20Lithophane.html'
    driver.get(url)

    input_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'fileToUpload'))
    )
    input_element.send_keys(file_path)

    pixel_resolution = driver.find_element(By.ID, "lith_res")
    pixel_resolution.clear()
    pixel_resolution.send_keys("0.1")

    slot_width = driver.find_element(By.ID, "w_slot")
    slot_width.clear()
    slot_width.send_keys("5.5")

    slot_depth = driver.find_element(By.ID, "d_slot")
    slot_depth.clear()
    slot_depth.send_keys("30")
    
    light_distance = driver.find_element(By.ID, "LLS")
    light_distance.clear()
    light_distance.send_keys("15")

    lito_radius = driver.find_element(By.ID, "radius")
    lito_radius.clear()
    lito_radius.send_keys("120")
    
    lito_width = driver.find_element(By.ID, "x_span")
    lito_width.clear()
    lito_width.send_keys("219")
    lito_height = driver.find_element(By.ID, "z_dim")
    lito_height.clear()
    lito_height.send_keys("230")

    email_address = driver.find_element(By.ID, "emailAddress")
    email_address.clear()
    email_address.send_keys("felipez8989@gmail.com")

    # dummy = driver.find_element(By.ID, "")
    # dummy.clear()
    # dummy.send_keys("")

    create_button = driver.find_element(By.NAME, 'submit')
    create_button.click()
    

def stl_to_gcode(stl_path):
    
    timeout = 300
    start_time = time.time()
    current_os = platform.system().lower()
    print('current_os: ', current_os)
    cura_command = ['open', '-a', '/Applications/Ultimaker Cura.app', stl_path] if current_os == 'darwin' else [r'C:\Program Files\Ultimaker Cura 4.x\Cura.exe', stl_path]
    subprocess.Popen(cura_command)
        
    while time.time() - start_time < timeout:    
        try:
            slice_button = pyautogui.locateCenterOnScreen(current_os + '_slice_button.png', confidence=0.9)
            if slice_button:
                time.sleep(2)
                pyautogui.moveTo(1170, 850)
                pyautogui.click()
                print("Slice button clicked.")
                break
            else:
                print("Slice button not found, retrying in 3s")
                time.sleep(3)
        except pyautogui.ImageNotFoundException:
            print("Slice button not found, retrying in 3s")
            time.sleep(3)
    
    if slice_button:  
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                save_button = pyautogui.locateCenterOnScreen(current_os + '_save_button.png', confidence=0.9)
                if save_button:
                    pyautogui.click()
                    print("Save button clicked.")
                    time.sleep(2)
                    pyautogui.press('enter')
                    time.sleep(5)
                    while time.time() - start_time < timeout:
                        try: 
                            end_confirmation = pyautogui.locateCenterOnScreen(current_os + '_open_folder.png', confidence=0.9)
                            if end_confirmation:
                                subprocess.run(['osascript', '-e', 'tell application "Ultimaker Cura" to quit'])
                                print('Closing')
                                return True
                        except pyautogui.ImageNotFoundException:
                            print("Open Folder button not found, retrying in 3s.")
                            time.sleep(3)
                else:
                    print("Save button not found, retrying in 3s")
                    time.sleep(3)
            except pyautogui.ImageNotFoundException:
                print("Save button not found, retrying in 3s.")
                time.sleep(3)

    stl_to_gcode(stl_path)

def list_files(directory):
    return set(f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)))

def unzip_stl():
    zip_dir ='/Users/admin/Downloads'
    zip_files = glob.glob(os.path.join('/Users/admin/Downloads', '*.zip'))
    if zip_files:
        with zipfile.ZipFile(zip_files[0], 'r') as zip_ref:
            zip_ref.extractall(zip_dir)
    zip_files = glob.glob(os.path.join(zip_dir, '*.zip'))
    if zip_files:
        with zipfile.ZipFile(zip_files[0], 'r') as zip_ref:
            zip_ref.extractall(zip_dir)
    stl_files = glob.glob(os.path.join(zip_dir, '*.stl'))
    return stl_files
    
def monitor_directory_changes(directory, interval=3):
    previous_files = list_files(directory)
    print(f"Initial files: {previous_files}")

    while True:
        time.sleep(interval)
        current_files = list_files(directory)
        if current_files != previous_files:
            time.sleep(10)
            driver.quit()
            break
        else:
            print("No change detected.")

file_path = '/Users/admin/Desktop/Proyectos/imageToStlSeleniumk.py/goku_and_frieza_vs_jiren_render_dokkan_battle_by_maxiuchiha22dcmnkx7Ob0hD.webp'

try:
    image_to_stl('/Users/admin/Downloads/rorro.jpeg')
    monitor_directory_changes('/Users/admin/Downloads')
    stl_files = unzip_stl()
    stl_to_gcode(stl_path=stl_files[0])


except Exception as e:
    print(f"An error occurred: {e}")