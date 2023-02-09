import torch
from numpy import random, ascontiguousarray

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import check_img_size, non_max_suppression, apply_classifier, \
    scale_coords, set_logging
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier


class simulation_opt:
    def __init__(self, weights='weights/yolov7.pt',
                 img_size=640, conf_thres=0.7,
                 iou_thres=0.5, device='', view_img=False,
                 classes=None, agnostic_nms=False,
                 augment=False, update=False, exist_ok=False):
        self.weights = weights
        self.source = None
        self.img_size = img_size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.device = device
        self.view_img = view_img
        self.classes = classes
        self.agnostic_nms = agnostic_nms
        self.augment = augment
        self.update = update
        self.exist_ok = exist_ok


class detectapi:
    def __init__(self, weights, img_size=640):
        self.opt = simulation_opt(weights=weights, img_size=img_size)
        weights, imgsz = self.opt.weights, self.opt.img_size

        # Initialize
        set_logging()
        self.device = select_device(self.opt.device)
        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(imgsz, s=self.stride)  # check img_size

        if self.half:
            self.model.half()  # to FP16

        # Second-stage classifier
        self.classify = False
        if self.classify:
            self.modelc = load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=self.device)['model']).to(
                self.device).eval()

        # read names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]

    def detect(self, source, debug=False):  # 使用时，调用这个函数
        # Padded resize
        img = letterbox(source, self.imgsz, stride=self.stride)[0]
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        # Inference
        pred = self.model(img, augment=self.opt.augment)[0]
        # Apply NMS
        pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes,
                                   agnostic=self.opt.agnostic_nms)
        # Apply Classifier
        if self.classify:
            pred = apply_classifier(pred, self.modelc, img, source)
        '''
        对于一张图片，可能有多个可被检测的目标。所以结果标签也可能有多个。
        每被检测出一个物体，result_txt的长度就加一。result_txt中的每个元素是个列表，记录着被检测物的类别引索，在图片上的位置，以及置信度
        '''
        det = pred[0]
        result_txt = []
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], source.shape).round()
            # Write results
            for *xyxy, conf, cls in reversed(det):
                name = self.names[int(cls)]
                line = (name, [int(_.item()) for _ in xyxy], conf.item())  # label format
                result_txt.append(line)
                if debug:
                    label = f'{name} {conf:.2f}'
                    plot_one_box(xyxy, source, label=label, color=self.colors[int(cls)], line_thickness=3)
        return source, result_txt
