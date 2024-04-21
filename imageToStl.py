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
import subprocess
import platform

def force_quit_cura():
    script = '''
    tell application "System Events"
        key code 53 using {command down, option down}
    end tell
    '''
    subprocess.run(["osascript", "-e", script])
    time.sleep(1)
    xcura,ycura = pyautogui.locateCenterOnScreen('darwin_curafq.png')
    pyautogui.moveTo(xcura,ycura)
    pyautogui.click()
    xfq1, yfq1 = pyautogui.locateCenterOnScreen('darwin_fq1.png')
    pyautogui.moveTo(xfq1,yfq1)
    pyautogui.click()
    time.sleep(1)
    xfq2, yfq2 = pyautogui.locateCenterOnScreen('darwin_fq2.png')
    pyautogui.moveTo(xfq2,yfq2)
    pyautogui.click()
    time.sleep(1)
    pyautogui.press('esc')

def remove_extension(filename):
    last_dot_index = filename.rfind('.')
    if last_dot_index != -1:
        base_filename = filename[:last_dot_index]
    else:
        base_filename = filename
    return base_filename

def get_paths(image_filename):
    current_os = platform.system().lower()
    download_path = '/Users/admin/Downloads/' if current_os=='darwin' else 'C:\\Users\\Felipe\\Downloads\\'
    image_directory = '/Users/admin/Desktop/images/' if current_os=='darwin' else 'C:\\Users\\Felipe\\Desktop\\images\\'
    image_path = image_directory + image_filename
    zip_path = download_path + 'NL-' + remove_extension(image_filename) + '.zip'
    stl_path = download_path + 'NL-' + remove_extension(image_filename) + '.stl'

    return image_path, zip_path, stl_path

def image_to_stl(file_path):
    
    firefox_options = Options()
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/sla")  # MIME type for STL files
    url = 'https://lithophanemaker.com/Night%20Light%20Lithophane.html'
    global driver
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
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
    timeout = 40
    start_time = time.time()
    current_os = platform.system().lower()
    print('current_os: ', current_os)
    cura_command = ['open', '-a', '/Applications/Ultimaker Cura.app', stl_path] if current_os == 'darwin' else [r'C:\Program Files\Ultimaker Cura 5.6.0\UltiMaker-Cura.exe', stl_path]
    subprocess.Popen(cura_command)
    slice_button = None
    save_button  = None
    while time.time() - start_time < timeout:
        print('Timeout: ',time.time() - start_time)
        try:
            slice_button = pyautogui.locateCenterOnScreen(current_os + '_slice_button.png', confidence=0.9)
            if slice_button:
                time.sleep(2)
                # pyautogui.moveTo(1170, 850) #mac
                pyautogui.moveTo(slice_button.x/2, slice_button.y/2)
                # pyautogui.moveTo(1650, 1028) #monitor
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
            print('Timeout: ',time.time() - start_time)
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

    force_quit_cura()
    time.sleep(3)
    print('Trying again...')
    stl_to_gcode(stl_path)

def unzip_stl(zip_file_path):
    zip_dir = os.path.dirname(zip_file_path)
    extracted_stl_files = []
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        all_files = zip_ref.namelist()
        stl_files = [f for f in all_files if f.lower().endswith('.stl')]
        for stl_file in stl_files:
            zip_ref.extract(stl_file, zip_dir)
            extracted_stl_files.append(os.path.join(zip_dir, stl_file))

def monitor_download(zip_path):
    while not os.path.exists(zip_path):
        print('File not yet downloaded...')
        time.sleep(3)
    print('Downloaded')
    time.sleep(10)
    driver.quit()

try:
    filename='input.jpg'
    image_path, zip_path, stl_path = get_paths(filename)
    # image_to_stl(image_path)
    # monitor_download(zip_path)
    # unzip_stl(zip_path)
    stl_to_gcode(stl_path)
    # unzip_stl('/Users/admin/Downloads/NL-rorro.zip')

except Exception as e:
    print(f"An error occurred: {e}")