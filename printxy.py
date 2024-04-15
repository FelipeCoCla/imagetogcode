import pyautogui
import time

try:
    while True:
        # Get the current mouse x and y positions.
        x, y = pyautogui.position()
        # slice_button = pyautogui.locateCenterOnScreen('slicing.png')
        # Print the current cursor position.
        print(f"Cursor position: X={x} Y={y}")
        # print('Slice button: ',slice_button)
        # Pause the loop for one second.
        time.sleep(1)
except KeyboardInterrupt:
    print("Program exited.")