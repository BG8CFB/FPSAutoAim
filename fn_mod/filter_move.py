import ctypes
import math

import pyautogui

SCREEN_W, SCREEN_H = pyautogui.size()
SCREEN_CX = SCREEN_W // 2  # 屏幕中心x
SCREEN_CY = SCREEN_H // 2  # 屏幕中心y
SCREEN_C = [SCREEN_CX, SCREEN_CY]  # 屏幕中心坐标
SCREENSHOT_W = 640  # 截图区域长
SCREENSHOT_H = 640  # 截图区域高
LEFT = SCREEN_CX - SCREENSHOT_W // 2  # 检测框左上角x
TOP = SCREEN_CY - SCREENSHOT_H // 2  # 检测框左上角y

try:
    driver = ctypes.CDLL('lib/logitech.driver.dll')
    ok = driver.device_open() == 1
    if not ok:
        print('初始化失败, 未安装lgs/ghub驱动')
except FileNotFoundError:
    print('初始化失败, 缺少文件')


def BoxCenter(xyxy):
    """
    返回目标在截图的瞄准坐标;
    :param xyxy: [lx,ly,w,h]->[左上x坐标，左上y坐标]
    :return: [x,y]
    """
    box_center = [(xyxy[2] - xyxy[0]) // 2, (xyxy[3] - xyxy[1]) // 3]
    return [box_center[0] + xyxy[0], box_center[1] + xyxy[1]]


def Distance(a, b):
    """
    两点间距离
    :param a:a点 (xa,ya)
    :param b: b点(xb,yb)
    :return: sqrt((xa-xb)**2 + (yb-ya)**2)
    """
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2))


def FilterData(res):
    """根据检测的结果，寻找最佳射击坐标
    :param res: 检测结果
    :return: {center：目标在屏幕的位置，dt：准星和目标距离}最佳射击坐标
    """
    res_data = {'center': [], 'dt': float('inf'), 'point': [0, 0, 0, 0]}
    for name, xyxy, conf in res:
        center_point = BoxCenter(xyxy)
        dt = Distance([center_point[0] + LEFT, center_point[1] + TOP], SCREEN_C)
        if dt < res_data['dt']:
            res_data['center'] = [center_point[0] + LEFT, center_point[1] + TOP]
            res_data['dt'] = dt
            res_data['point'] = xyxy
    return res_data


def Move(res_data):
    if len(res_data['center']) == 0:
        return
    x, y = res_data['center'][0], res_data['center'][1]
    dt = res_data['dt']
    print('目标位置：' + str(x) + ',' + str(y) + '.目标距离：' + str(dt))

    res_x = x - SCREEN_CX
    res_y = y - SCREEN_CY

    move_x = 0
    move_y = 0

    if dt >= 100:
        move_speed = 10
    elif 10 < dt < 100:
        move_speed = 6
    elif 4 <= dt <= 10:
        move_speed = 2
    elif dt < 4:
        move_speed = 1

    if res_y > 0:
        move_y = move_speed
    elif res_y < 0:
        move_y = -1 * move_speed
    elif res_y == 0:
        move_y = 0

    if res_x > 0:
        move_x = move_speed
    elif res_x < 0:
        move_x = -1 * move_speed
    elif res_x == 0:
        move_x = 0

    if (x == 0) & (y == 0):
        return
    driver.moveR(int(move_x), int(move_y), True)


def FilterMove(res):
    res_data = FilterData(res)
    Move(res_data)
