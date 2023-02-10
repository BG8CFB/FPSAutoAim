import mss
import numpy as np
import pyautogui

SCREEN_W, SCREEN_H = pyautogui.size()
SCREEN_CX = SCREEN_W // 2  # 屏幕中心x
SCREEN_CY = SCREEN_H // 2  # 屏幕中心y
SCREEN_C = [SCREEN_CX, SCREEN_CY]  # 屏幕中心坐标
SCREENSHOT_W = 640  # 截图区域长
SCREENSHOT_H = 640  # 截图区域高
LEFT = SCREEN_CX - SCREENSHOT_W // 2  # 检测框左上角x
TOP = SCREEN_CY - SCREENSHOT_H // 2  # 检测框左上角y
monitor = {'top': 220, 'left': 640, 'width': 640, 'height': 640}

# 截图
def ScreenShout():
    return np.array(mss.mss().grab(monitor))
    # return np.array(pyautogui.screenshot(region=[LEFT, TOP, SCREENSHOT_W, SCREENSHOT_H]))



if __name__ == "__main__":
    pass
