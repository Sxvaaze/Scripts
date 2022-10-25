import time
import cv2
import util as util
from djitello import tello
from multiprocessing import Process
from skimage.metrics import structural_similarity
    
def get_two_frames():
    img = drone.get_frame_read().frame
    time.sleep(0.1)
    img2 = drone.get_frame_read().frame
    return (img, img2)

def image_processing():
    f, s = get_two_frames()
    width = height = 400
    first = cv2.resize(f, (width, height))
    second = cv2.resize(s, (width, height))              
    first_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    second_gray = cv2.cvtColor(second, cv2.COLOR_BGR2GRAY)                      
    score, diff = structural_similarity(first_gray, second_gray, full=True)
    return round(score * 100, 2)

def handle_worker():
    while True:
        similarity_num = image_processing()
        if util.get_motion(similarity_num):
            print("Υπήρξε Κίνηση")
        else:
            print("Δεν Υπήρξε Κίνηση")

if __name__ == "__main__":
    drone = tello.Tello()
    drone.connect()
    drone.streamon()
    p = Process(target=handle_worker)
    p.start()
    p.join()
