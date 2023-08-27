import sensor, image, time, lcd
import pyb
from pyb import Pin
from pyb import LED
# 串口初始化
uart = pyb.UART(3,115200,timeout_char = 1000)



sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.HQVGA) # use QQVGA for speed.
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_gain(False) # 关闭增益（色块识别时必须要关）
sensor.skip_frames(20) # Let new settings take affect.
sensor.set_auto_exposure(False, 5000)
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_vflip(True)
sensor.set_hmirror(True)

clock = time.clock() # Tracks FPS.

# 提取最大的色块
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

red_threshold_white = (0, 37, 8, 127, -128, 127)
green_threshold_white = (18, 58, -117, -17, -128, 127)# (22, 90, -82, 9, -74, 42)

red_threshold_black = (5, 100, 127, 15, -128, 117)
green_threshold_black = (5, 100, -95, 11, -110, 127)

ROI1 = (45, 6, 140, 140 )
# 区分红绿色斑
def color_blob(threshold):
    blobs = img.find_blobs(threshold, merge = True)
    #img.binary(threshold)
    
    if len(blobs) == 1 :  # 一个红光斑
        # Draw a rect around the blob.
        b = blobs[0]
        cx = b[5]
        cy = b[6]
        img.draw_cross(b[5], b[6],color = (255, 0, 0), size = 20) # cx, cy
        return cx, cy, 0, 0

    elif len(blobs) == 1 and blobs[0].code() == 2: # 一个绿光斑
        b = blobs[0]
        cx = b[5]
        cy = b[6]
        img.draw_cross(b[5], b[6],color = (0, 255, 0), size = 20) # cx, cy
        return 0, 0, cx, cy

    elif len(blobs) == 2:  # 两个光斑（暂定为一红一绿）

        cx1 = blobs[0][5]
        cy1 = blobs[0][6]

        cx2 = blobs[1][5]
        cy2 = blobs[1][6]
        if blobs[0].code() == 1:
            img.draw_cross(cx1, cy1, color = (255, 0, 0), size = 20) # cx, cy
            img.draw_cross(cx2, cy2, color = (0, 255, 0), size = 20)
            return cx1, cy1, cx2, cy2

        elif blobs[0].code() == 2:
            img.draw_cross(cx2, cy2, color = (255, 0, 0), size = 20) # cx, cy
            img.draw_cross(cx1, cy1, color = (0, 255, 0), size = 20)
            return cx2, cy2, cx1, cy1

    return 0, 0, 0, 0


while(True):
#    lcd.display(sensor.snapshot())
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot().lens_corr(1.5) # Take a picture and return the image.
    
    coordinate = color_blob([red_threshold_white,(96, 0, 6, 127, -128, 127), (96, 0, 6, 127, -128, 127),(20, 100, 16, 127, 18, -21), (100, 0, 10, 127, -128, 127),(100, 0, 8, 127, -128, 127)])

    if coordinate != (0, 0, 0, 0):
        data = bytearray([0x5a, int(coordinate[0]), int(coordinate[1]),0xef])
        uart.write(data)

        print("coordinate:", coordinate)
#    if coordinate != (240, 160):

#        data = bytearray([0x5a, int(coordinate[0]), int(coordinate[1]), 0xef])
#        uart.write(data)

#        print("coordinate:", coordinate)
#
    print(clock.fps())
