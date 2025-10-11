import time
import cv2
import dxcam
from PIL import Image
from MapleScript import MapleScript
from XiaoController import XiaoController
import numpy as np


class Pipe:

    def __init__(self):
        self.__template = cv2.cvtColor(cv2.imread(r"C:\Users\abc21\Pictures\train_data_png\move_frame_00.png"), cv2.COLOR_BGR2GRAY)
        self.__threshold = 0.8
        self.__h, self.__w = self.__template.shape[:2]

    def match(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_frame, self.__template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= self.__threshold)
        return loc

    def draw(self, loc, frame):
        for pt in zip(*loc[::-1]):
            cv2.rectangle(frame, pt, (pt[0] + self.__w, pt[1] + self.__h), (0, 255, 0), 2)

    def loop(self):
        with XiaoController() as Xiao:
            Maple = MapleScript(Xiao)
            left, top, width, height = Maple.maple_full_screen_area
            region = (left, top, left+width, top+height)

            camera = dxcam.create(region=region, device_idx=0, output_color="BGR")
            camera.start()
            for i in range(900):
                latest_frame = camera.get_latest_frame()
                loc = self.match(latest_frame)
                self.draw(loc, latest_frame)
                cv2.imshow("test", latest_frame)
                cv2.waitKey(1)
            camera.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    pipe = Pipe()
    pipe.loop()