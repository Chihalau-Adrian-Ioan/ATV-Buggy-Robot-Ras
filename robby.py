import RPi.GPIO as GPIO
import time
from adafruit_motorkit import MotorKit
from pynput.keyboard import Key, Listener
import pygame
import threading
from queue import Queue

kit = MotorKit()
on = False
TRIG = 21
ECHO = 20
distance_front = 10
stopSignal = False
GPIO.setmode(GPIO.BCM)

def forward():
    kit.motor1.throttle = 1.0
    kit.motor2.throttle = 1.0
    print('UP!')

def backward():
    kit.motor1.throttle = -1.0
    kit.motor2.throttle = -1.0
    print('DOWN!')


def left():
    kit.motor2.throttle = 0.2
    print('LEFT!')


def right():
    kit.motor1.throttle = 0.2
    print('RIGHT!')

def stop():
    kit.motor1.throttle = 0.0
    kit.motor2.throttle = 0.0
    print('STOP!')

def detectDistance(q):
    global TRIG, ECHO, distance_front, stopSignal
    while stopSignal == False:
        print("distance measurement in progress")
        GPIO.setup(TRIG,GPIO.OUT)
        GPIO.setup(ECHO,GPIO.IN)
        GPIO.output(TRIG,False)
        print("waiting for sensor to settle")
        time.sleep(0.2)
        GPIO.output(TRIG,True)
        time.sleep(0.00001)
        GPIO.output(TRIG,False)
        while GPIO.input(ECHO)==0:
            pulse_start=time.time()
        while GPIO.input(ECHO)==1:
            pulse_end=time.time()
        pulse_duration=pulse_end-pulse_start
        distance=pulse_duration*17150
        distance=round(distance,2)
        #print("distance:",distance,"cm")
        q.put(distance)
        #distance_front = distance

def init():
    pygame.init()
    win = pygame.display.set_mode((100, 100))

def getKey(keyName):
    ans = False

    for event in pygame.event.get():pass
    keyInput = pygame.key.get_pressed()
    pressedKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput [pressedKey]:
        ans = True
    pygame.display.update()

    return ans

def main(q):
    global distance_front, stopSignal
    if q.empty() == False:
       distance_front = q.get_nowait()
    print(f"distance measured: {distance_front} cm")
    if getKey('w') and distance_front > 5:
       forward()
    elif getKey('s'):
       backward()
    else:
       stop()

    if getKey('a'):
       left()
    elif getKey('d'):
       right()
    else:
       stop()
    if getKey('x'):
       stop()
       stopSignal = True
if __name__ == '__main__':
    q = Queue()
    init()
    distance_thread = threading.Thread(target = detectDistance, args = (q,))
    distance_thread.start()
    while stopSignal == False:
        main(q)
    distance_thread.join()
