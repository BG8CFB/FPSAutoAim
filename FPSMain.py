from multiprocessing import Process, freeze_support, Manager

init = {
    'fire_state': False,  # 开火状态
    'detect_res': [],
    'roundh': 16420,  # 游戏内以鼠标灵敏度为1测得的水平旋转360°对应的鼠标移动距离, 多次测量验证. 经过测试该值与FOV无关. 移动像素理论上等于该值除以鼠标灵敏度
    'roundv': 7710 * 2,  # 垂直, 注意垂直只能测一半, 即180°范围, 所以结果需要翻倍
}


def monitor(init_data):
    # 监听功能
    from pynput import mouse, keyboard
    from threading import Thread

    def Mouse():
        # 鼠标监听
        def on_click(x, y, button, pressed):
            if button == mouse.Button.left:
                init_data['fire_state'] = pressed
                print('鼠标点击开始执行')

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def Keyboard():
        # 键盘监听
        def on_press(key):
            if key == keyboard.KeyCode.from_char('f'):
                init_data['fire_state'] = True

        def release(key):
            pass

        with keyboard.Listener(on_click=on_press, on_release=release) as keylistener:
            keylistener.join()

    MouseThread = Thread(target=Mouse, args=())
    KeyThread = Thread(target=Keyboard, args=())
    MouseThread.start()
    KeyThread.start()


def FilterMove(init_data):
    import time
    # 数据过滤和移动鼠标
    from utils.filter_move import FilterMove
    while True:
        time.sleep(0.001)
        if len(init_data['detect_res']) & init_data['fire_state']:
            FilterMove(init_data['detect_res'])  # 结果筛选


def ScreenshotDetect(init_data, debug=False):
    # 截图和送入检测
    import time
    import cv2
    import detect_api
    from utils.FPSUtils import ScreenShout
    DETECT_API = detect_api.detectapi(weights='weights/ow_jqr_01.pt')

    while True:
        time_start = time.time()
        img = cv2.cvtColor(ScreenShout(), cv2.COLOR_RGB2BGR)  # 截取屏幕检测区域并转换图片格式：RGB-->BGR
        img, result = DETECT_API.detect(img, debug=debug)  # 送入yolo检测
        init_data['detect_res'] = result
        if debug:
            # 每一帧图像的识别结果（可包含多个物体）
            for name, (x1, y1, x2, y2), conf in result:
                print(name, x1, y1, x2, y2, conf)  # 识别物体种类、左上角x坐标、左上角y轴坐标、右下角x轴坐标、右下角y轴坐标，置信度
            print()  # 将每一帧的结果输出分开
            cv2.namedWindow('Debug', 0)
            cv2.imshow("Debug", img)
            cv2.waitKey(1)
        time_end = time.time()
        print('time cost', time_end - time_start, 's')


if __name__ == '__main__':
    from torch import no_grad

    freeze_support()  # windows 平台使用 multiprocessing 必须在 main 中第一行写这个
    with no_grad():
        # init_data = Manager().dict().update(init)  # 创建进程安全的共享变量,将初始数据导入到共享变量
        manager = Manager()
        init_data = manager.dict()  # 创建进程安全的共享变量
        init_data.update(init)  # 将初始数据导入到共享变量
        # 鼠标监听
        monitor_process = Process(target=monitor, args=(init_data,))
        filter_move = Process(target=FilterMove, args=(init_data,))
        monitor_process.start()
        filter_move.start()
        ScreenshotDetect(init_data, debug=True)
        monitor_process.join()
