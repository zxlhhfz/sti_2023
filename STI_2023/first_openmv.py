import sensor, image, time, lcd
import pyb
from pyb import Pin
from pyb import LED
# 串口初始化
uart = pyb.UART(3,115200,timeout_char = 1000)

# LED初始化
led = LED(1)
led.off()

clock = time.clock() # Tracks FPS.


ROI = (74, 45, 171, 171)  # QVGA
#ROI = (70, 40, 180, 179)  # QVGA
ROI_prepare = (39, 31, 86, 86)
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

# 区分红绿色斑
def color_blob(threshold):
    blobs = img.find_blobs(threshold,merge = True)
    #img.binary(threshold)
    if len(blobs) == 1 :  # 一个红光斑
        # Draw a rect around the blob.
        b = blobs[0]
        cx = b[5]
        cy = b[6]
        img.draw_cross(b[5], b[6],color = (255, 0, 0), size = 20) # cx, cy
        return cx, cy, 0, 0

#    elif len(blobs) == 1 and blobs[0].code() == 2: # 一个绿光斑
#        b = blobs[0]
#        cx = b[5]
#        cy = b[6]
#        img.draw_cross(b[5], b[6],color = (0, 255, 0), size = 20) # cx, cy
#        return 0, 0, cx, cy

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





sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA) # use QQVGA for speed.
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_gain(False) # 关闭增益（色块识别时必须要关）
sensor.skip_frames(20) # Let new settings take affect.
sensor.set_auto_exposure(False, 2000)
sensor.set_auto_whitebal(False) # turn this off.
#sensor.set_vflip(True)
#sensor.set_hmirror(True)

receive_data = 0

while(True):
    if uart.any():
        receive_data = uart.read(1).decode()
        
        if receive_data == '1':
            led.on()
            sensor.reset()
            sensor.set_pixformat(sensor.GRAYSCALE) # RGB565/GRAYSCALE灰度更快
            sensor.set_framesize(sensor.QVGA) # (160x120 max on OpenMV-M7)
            sensor.skip_frames(time = 25)
            sensor.set_auto_gain(False) # 关闭增益（色块识别时必须要关）
            sensor.set_auto_whitebal(False) # 关闭白平衡
            sensor.set_vflip(True)
            sensor.set_hmirror(True)
            
    
    
        
            cnt = 0
            while(cnt < 10):
                clock.tick()
            #    img.binary([])
            
                img = sensor.snapshot().lens_corr(1.6)
            
            #    img.draw_rectangle(ROI, color = (255,0,0))
            
            
                # 下面的`threshold`应设置为足够高的值，以滤除在图像中检测到的具有
                # 低边缘幅度的噪声矩形。最适用与背景形成鲜明对比的矩形。
            
            #    rects = img.find_rects(threshold = 10000)
                rects = img.find_rects(roi = ROI, threshold = 25000)
                img.draw_rectangle(ROI)
                if rects:
                    max_rect = find_max(rects)
            
            
                    
                    img.draw_rectangle(max_rect.rect(), color = (255, 0, 0))
                    for p in max_rect.corners():
                        img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
            
                    x1 = int(max_rect.corners()[0][0])
                    y1 = int(max_rect.corners()[0][1])
            
                    x2 = int(max_rect.corners()[1][0])
                    y2 = int(max_rect.corners()[1][1])
            
                    x3 = int(max_rect.corners()[2][0])
                    y3 = int(max_rect.corners()[2][1])
            
                    x4 = int(max_rect.corners()[3][0])
                    y4 = int(max_rect.corners()[3][1])
            
                    print(x1, y1, x4, y4, x3, y3, x2, y2)
                    
                    
                        
                    data = bytearray([0x5a,x1, y1, x4, y4, x3, y3, x2, y2,0xef])
                    
                    uart.write(data)
                    
                    break
            
                cnt += 1
                print("FPS %f" % clock.fps())
            
            
            sensor.reset() # Initialize the camera sensor.
            sensor.set_pixformat(sensor.RGB565) # use RGB565.
            sensor.set_framesize(sensor.QVGA) # use QQVGA for speed.
            sensor.skip_frames(time = 1500) # Let new settings take affect.
            sensor.set_auto_gain(False) # 关闭增益（色块识别时必须要关）
            
            sensor.set_auto_exposure(False, 1500)
            sensor.set_auto_whitebal(False) # turn this off.
        
            cnt = 0
            

            led.off()
            receive_data = 0

#    lcd.display(sensor.snapshot())
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot().lens_corr(1.6) # Take a picture and return the image.
    
#    coordinate = color_blob([red_threshold_white, (20, 100, 16, 127, 18, -21), (100, 0, 25, 127, -128, 127)])
    coordinate = color_blob([red_threshold_white, (20, 100, 16, 127, 18, -21), (85, 19, 9, 127, -128, 127)])

    if coordinate != (0, 0, 0, 0):
        data = bytearray([0xaa, int(coordinate[0]), int(coordinate[1]),0xbb])
        uart.write(data)

        print("coordinate:", coordinate)

    print(clock.fps())


















