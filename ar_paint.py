import argparse
from copy import deepcopy
from operator import index
from re import T
from xmlrpc.client import TRANSPORT_ERROR
import cv2
from textwrap import indent
import json
import os
from color_segmenter import *
from collections import deque
from functions import *
import copy
import random

drawing = False
first_mouse_point = (0,0)


# To define shake detection mode
def onModes(usp):
    if usp == True:
        return 'usp_mode'

def onMouse(event,x,y,flags,param):

    global  drawing
    global rgb_points
    global xm, xm
    global mouse_start


    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(paintWindow,(int(x),int(y)),10,(0,0,255),-1)
        xm = x
        xm = y
        k = 1
        mouse_start = (xm,ym)
        
        

def distance(current_location, previous_location):
    return int(math.sqrt(math.pow(current_location[0] - previous_location[0], 2) + math.pow(current_location[1] - previous_location[1],2)))                                                      

def shake_prevention(x, y, past_x, past_y):
    # Distancia ponto atual ao ponto anterior
    if past_x and past_y:
        # Se a distancia for superior a 50 retorna que é necessário fazer shake prevention caso contrario retorna que não é necessário
        if max(abs(past_x-x),abs(past_y-y))> 100:
            return True
        return False

def main():
    
    global paintWindow, thickness
    global rgb_points
    global xm, ym

    mouse_points = []

    past_x, past_y = 0,0
    
    parser = argparse.ArgumentParser(description='PSR augmented reality paint') #creates a argumentParser object
    parser.add_argument('-j','--json', type=str, required = True, help='Full path to json file') 
    parser.add_argument('-usp','--use_shake_prevention',action='store_true', help='To use shake prevention.')
    

    args = vars(parser.parse_args())
    
    #print com todos os comando possíveis para facilitar a utilização do programa ao utilizador
    program_instructions()



    limits_values = open(args['json'])
    limits_values = json.load(limits_values)
    
    paiting_images={'ball.png': 'ball.png','papagaio.png': 'papagaio.png'}

    # extract variables from the file 
    min_B=  limits_values['limits']['B']['min']
    min_G = limits_values['limits']['G']['min']
    min_R = limits_values['limits']['R']['min']
    max_B = limits_values['limits']['B']['max']
    max_G = limits_values['limits']['G']['max']
    max_R = limits_values['limits']['R']['max']

    lower_bound=np.array([min_B,min_G,min_R])
    upper_bound=np.array([max_B,max_G,max_R])

    rgb_points=[]
    thick_points=[]
    color_points=[]
    thickness=1

    #starting the painting window setup
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]# blue green red
    colorIndex = 0 #default blue color
    
    kernel = np.ones((10,10),np.uint8)

    paintWindow = np.zeros((471,636,3)) + 255
    #paintWindow = cv2.flip(paintWindow, 1)

    center = None

    square_mode=False
    ellipse_mode=False
    first_press=False
    debouncing=0
    last_point_rect=[]
    last_point_circle=[]
    my_rect=[]
    my_circle=[]

    painting_in_video = False
    painting_with_color=False

    video_capture = cv2.VideoCapture(0)

    while True: 
    
        _, frame = video_capture.read()
        vid_thresh = frame.copy()
        vid_mask=cv2.inRange(vid_thresh,lower_bound, upper_bound)
        frame = cv2.flip(frame, 1)

        #Fuzzy detections that result in little blobs are cleared leaving only bigger objects detected
        Mask, x, y= removeSmallComponents(vid_mask, 400)
        Mask = cv2.flip(Mask, 1)
    

        
        #find all the contours of the segmented mask
        cnts,_ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        #checking if any countor is detected then ru the following statements
        if len(cnts) > 0:
            # sorting the contours to find biggest contour
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            
            
            # Calculating the center of the detected contour
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            frame[(Mask== 255)] = (0, 255, 0)
            
            
            cv2.line(frame, (int(center[0]) - 10, int(center[1]) + 10), (int(center[0]) + 10, int(center[1]) - 10), (0, 0, 255), 5)
            cv2.line(frame, (int(center[0]) + 10, int(center[1]) + 10), (int(center[0]) - 10, int(center[1]) - 10), (0, 0, 255), 5)
            
            mode = onModes(args['use_shake_prevention'])
            
            # Shake detection parameters
            
            if past_x == 0 and past_y == 0:
                past_x = center[0]
                past_y = center[1]
                
            if args['use_shake_prevention'] is True:
                shake_prevention(x, y, past_x, past_y)
                if shake_prevention:
                    cv2.setMouseCallback('Paint',onMouse)

            rgb_points.append(center)
            color_points.append(colorIndex)
            thick_points.append(thickness)

            # draw stuff
            if len(rgb_points) > 2 :

                if square_mode == False and ellipse_mode == False:
                    paintWindow = np.zeros((471,636,3)) + 255
                    if painting_with_color == True:
                        draw = cv2.imread(path_to_image)
                    for k in range(1,len(rgb_points)-1):
                        if args['use_shake_prevention'] is True:
                            if max(abs(rgb_points[k-1][0]-rgb_points[k][0]),abs(rgb_points[k-1][1]-rgb_points[k][1])) > 30 : #if two points are too much distant is an error
                                continue
                        cv2.line(paintWindow, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])
                        
                        # painting with color
                        if painting_with_color == True:
                            cv2.line(draw, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])

                    for k in my_rect:
                        cv2.rectangle(paintWindow, k[0], k[1], colors[k[2]], k[3])
                        
                    for k in my_circle:
                        cv2.circle(paintWindow, k[0],k[1], colors[k[2]], k[3])


                if square_mode == True:
                    paintWindow = np.zeros((471,636,3)) + 255
                    for k in range(1,rgb_points.index(actual_point)):#redraw everything
                        if args['use_shake_prevention'] is True:
                            if max(abs(rgb_points[k-1][0]-rgb_points[k][0]),abs(rgb_points[k-1][1]-rgb_points[k][1])) > 30 : #if two points are too much distant is an error
                                continue
                        cv2.line(paintWindow, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])
                        
                    for k in my_rect:
                        cv2.rectangle(paintWindow, k[0], k[1], colors[k[2]], k[3])
                        
                    for k in my_circle:
                        cv2.circle(paintWindow, k[0],k[1],colors[k[2]], k[3])

                    cv2.rectangle(paintWindow, actual_point, rgb_points[-1], colors[colorIndex], thickness)
                    cv2.rectangle(frame, actual_point, rgb_points[-1], colors[colorIndex], thickness)
                    pt=(actual_point,rgb_points[-1], colorIndex, thickness)
                    last_point_rect.append(pt)
                    rgb_points.pop(-1) #avoid to draw line while drawing figure
                    color_points.pop(-1)
                    thick_points.pop(-1)


                if ellipse_mode == True:
                    paintWindow = np.zeros((471,636,3)) + 255
                    for k in range(1,rgb_points.index(actual_point)):#redraw everything
                        if args['use_shake_prevention'] is True:
                            if max(abs(rgb_points[k-1][0]-rgb_points[k][0]),abs(rgb_points[k-1][1]-rgb_points[k][1])) > 30 : #if two points are too much distant is an error
                                continue
                        cv2.line(paintWindow, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])

                    for k in my_rect:
                        cv2.rectangle(paintWindow, k[0], k[1], colors[k[2]], k[3])

                    for k in my_circle:
                        cv2.circle(paintWindow, k[0],k[1], colors[k[2]], k[3])

                    radius= max(abs(actual_point[0]-rgb_points[-1][0]),abs(actual_point[1]-rgb_points[-1][1]))
                    cv2.circle(paintWindow, actual_point, radius, colors[colorIndex], thickness)
                    cv2.circle(frame, actual_point, radius, colors[colorIndex], thickness)
                    pt=(actual_point, radius, colorIndex, thickness)
                    last_point_circle.append(pt)
                    rgb_points.pop(-1) #avoid to draw line while drawing figure
                    print(rgb_points[-1])
                    color_points.pop(-1)
                    thick_points.pop(-1)


        #case in which you're not painting, we have to keep the picture on the frame 
        if painting_in_video == True:
            for k in range(1,len(rgb_points)-1):
                if args['use_shake_prevention'] is True:
                    if max(abs(rgb_points[k-1][0]-rgb_points[k][0]),abs(rgb_points[k-1][1]-rgb_points[k][1])) > 30 : #if two points are too much distant is an error
                        continue
                cv2.line(frame, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])
            for k in my_rect:
                cv2.rectangle(frame, k[0], k[1], colors[k[2]], k[3])
            for k in my_circle:
                cv2.circle(frame, k[0],k[1], colors[k[2]], k[3])
            cv2.imshow("Tracking", frame)


        k=cv2.waitKey(1)
        if k == 99:  # c clean the drawing
            print('clear paint window')
            rgb_points=[]
            color_points=[]
            thick_points=[]
            my_rect=[]
            my_circle=[]
            paintWindow = np.zeros((471,636,3)) + 255
            if painting_with_color == True:
                draw = cv2.imread(path_to_image)
        #change color
        elif k== ord('b'):
            print('change color: blue')
            colorIndex = 0      
        elif k == ord('g'):
            print('change color: green')
            colorIndex = 1
        elif k == ord('r'):
            print('change color: red')
            colorIndex = 2
        elif k == ord('t'):
            #select a random painting from the dictionary
            painting_with_color=True

            path_to_image = random.choice(list(paiting_images.values()))
            draw_painted = None

            if path_to_image == 'ball.png':
                draw_painted = "ball_painted.png"
            elif path_to_image == 'papagaio.png':
                draw_painted = "papagaio_painted.png"

            draw = cv2.imread(path_to_image)
            draw_painted = cv2.imread(draw_painted)

            print('clear paint window')
            rgb_points=[]
            color_points=[]
            thick_points=[]
            my_rect=[]
            my_circle=[]
            paintWindow = np.zeros((471,636,3)) + 255

            cv2.imshow('draw', draw)
            print('1 or 4: Red \n2: Green \n3: Blue')   

        elif k == ord('f'):#finish painting with color
            painting_with_color = False
            evaluation(draw,draw_painted,limits_values)
            cv2.imshow('Solution',draw_painted)
            

            
        #thickness
        elif k == ord('+'):
            print('thickness +')
            thickness += 1
        elif k == ord('-'):
            if thickness> 1:
                print('thicknes -')
                thickness -= 1
            else:
                print('is the minimum thickness')
        #write image
        elif k == ord('w'):
            print('write actual image')
            cv2.imwrite(time.ctime().replace(' ','_')+'.png',paintWindow)
        #exit
        elif k ==ord('q'):
            print('exit')
            exit(0)

        # to activate the drawing in video functionality
        elif k == ord('m'):
            if painting_in_video == False:
                painting_in_video = True
            else:
                painting_in_video = False

        # drawing shapes
        #debouncing to read correctly the pression on the key
        elif k == ord('s'):# square drawing
            debouncing+=1
            if debouncing >= 1:
                if first_press == False:
                    first_press=True
                    print('drawing rectangle mode')
                    actual_point=center
                square_mode=True
                

        elif k == ord('o'):# ellipse drawing(circle)
            debouncing+=1
            if debouncing >=1:
                if first_press == False:
                    first_press=True
                    print('drawing ellipse mode')
                    actual_point=center
                ellipse_mode=True

        else :
            if debouncing>1:
                debouncing=0
                print('esc drawing mode')
                if len(last_point_rect)>0:
                    my_rect.append(last_point_rect[-1])
                    last_point_rect=[]
                if len(last_point_circle)>0:
                    my_circle.append(last_point_circle[-1])
                    last_point_circle=[]
                first_press=False
                square_mode=False
                ellipse_mode=False

        #paintWindow = cv2.flip(paintWindow, 1)
        cv2.imshow("Tracking", frame)
        cv2.imshow("Paint", paintWindow)
        cv2.imshow("mask",Mask)
        if painting_with_color == True:
            cv2.imshow('draw',draw)

if __name__ == '__main__':
    main()

