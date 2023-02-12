from multiprocessing import Process, freeze_support, Manager

init = {
    'weights': 'weights/ow_jqr_01.pt',  # 检测权重文件
    'debug': True,  # 开启调试模式
    'fire_state': False,  # 开火状态
}


def monitor(share_data):
    # 监听功能
    from pynput import mouse, keyboard
    from threading import Thread

    def Mouse():
        # 鼠标监听
        def on_click(x, y, button, pressed):
            if button == mouse.Button.left:
                share_data['fire_state'] = pressed

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def Keyboard():
        # 键盘监听
        def on_press(key):
            if key == keyboard.KeyCode.from_char('f'):
                share_data['fire_state'] = True

        def release(key):
            pass

        with keyboard.Listener(on_click=on_press, on_release=release) as keylistener:
            keylistener.join()

    MouseThread = Thread(target=Mouse, args=())
    KeyThread = Thread(target=Keyboard, args=())
    MouseThread.start()
    KeyThread.start()
    MouseThread.join()
    KeyThread.join()


def ScreenshotDetect(detect_res):
    # 截图和送入检测
    import time
    import cv2
    import detect_api
    from fn_mod.screenshot import Screenshot
    DETECT_API = detect_api.detectapi(weights=init['weights'])

    while True:
        time_start = time.time()
        img = cv2.cvtColor(Screenshot(), cv2.COLOR_BGRA2BGR)
        img, result = DETECT_API.detect(img, debug=init['debug'])  # 送入yolo检测
        detect_res.put(result, block=True, timeout=1)

        if init['debug']:
            # 每一帧图像的识别结果（可包含多个物体）
            for name, (x1, y1, x2, y2), conf in result:
                print(name, x1, y1, x2, y2, conf)  # 识别物体种类、左上角x坐标、左上角y轴坐标、右下角x轴坐标、右下角y轴坐标，置信度
            print()  # 将每一帧的结果输出分开
            cv2.namedWindow('Debug', cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Debug", img)
            cv2.waitKey(1)
            print('time cost', time.time() - time_start, 's')


def FilterMove(share_data, detect_res):
    import time
    # 数据过滤和移动鼠标
    from fn_mod.filter_move import FilterMove
    while True:
        time.sleep(0.001)
        # 数据获取
        product = None
        try:
            product = detect_res.get(block=True, timeout=1)
        except:
            print('Consumer Error')

        if product and share_data['fire_state']:
            FilterMove(product)  # 结果筛选


if __name__ == '__main__':
    from torch import no_grad

    freeze_support()  # windows 平台使用 multiprocessing 必须在 main 中第一行写这个
    with no_grad():
        with Manager() as manager:
            detect_res = manager.Queue(maxsize=1)
            share_data = manager.dict()  # 创建进程安全的共享变量
            share_data.update(init)  # 将初始数据导入到共享变量

            monitor_process = Process(target=monitor, args=(share_data,))  # 监听按键
            detect = Process(target=ScreenshotDetect, args=(detect_res,))  # 截图和检测
            filter_move = Process(target=FilterMove, args=(share_data, detect_res))  # 结果筛选和移动

            monitor_process.start()
            detect.start()
            filter_move.start()

            monitor_process.join()
            filter_move.join()

            monitor_process.terminate()
