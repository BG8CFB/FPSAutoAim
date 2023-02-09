import ctypes
import time
import pyautogui

try:
    driver = ctypes.CDLL('lib/logitech.driver.dll')
    ok = driver.device_open() == 1
    if not ok:
        print('初始化失败, 未安装lgs/ghub驱动')
except IOError as e:
    print("驱动dll文件引入失败" % (e.errno, e.strerror))


# 鼠标移动方法
def mouse_move(x, y, *, interval=0.001, game_state=True):
    while True:
        mouse_position = pyautogui.position()
        res_x = x - mouse_position.x
        res_y = y - mouse_position.y
        if res_x == 0 and res_y == 0:
            break
        move_x = 0
        move_y = 0
        move_default = 15
        if res_y > 0:
            move_y = move_default
        elif res_y < 0:
            move_y = -1 * move_default
        elif res_y == 0:
            move_y = 0

        if res_x > 0:
            move_x = move_default
        elif res_x < 0:
            move_x = -1 * move_default
        elif res_x == 0:
            move_x = 0

        driver.moveR(int(move_x), int(move_y), True)
        time.sleep(interval)
        if game_state:
            break


class Mouse:
    @staticmethod
    def move(x, y, absolute=False, game_state=True):
        """
        x: 水平移动的方向和距离, 正数向右, 负数向左
        y: 垂直移动的方向和距离
        absolute: 是否绝对移动, 是:跳到水平x和垂直y的位置, 否:水平跳x距离垂直跳y距离
        """
        if x == 0 and y == 0:
            return
        if absolute:
            mouse_move(x, y, game_state=game_state)
        else:
            mouse_position = pyautogui.position()
            x = x + mouse_position.x
            y = y + mouse_position.y
            mouse_move(x, y, game_state=game_state)



if __name__ == "__main__":
    pass
