#library for the imagem processing
import cv2

#to save data in a json file- file made of text in a programming language, used to store and transfer data
import json

#to save the maximum and minimum in a array 
import numpy as np


import time 

#---Create each trackbar function using globals--------

#Let's create global variables so that the user can choose the treshold
# this way it will no trouble the code within the functions 
#in thiss functions it will be shown the values selected for the threshold for each value

#------BLUE---------
def onTrackbarmin_B(minB):
    global min_B
    min_B = minB
    print("Threshold " + str(minB) + " for the min of the B value")
    return min_B

def onTrackbarmax_B(maxB):
    global max_B
    max_B = maxB
    print("Threshold " + str(maxB) + " for the max of the B value")
    return max_B


#------GREEN---------
def onTrackbarmin_G(minG):
    global min_G
    min_G = minG
    print("Threshold " + str(minG) + " for the min of the G value")
    return min_G


def onTrackbarmax_G(maxG):
    global max_G
    max_G = maxG
    print("Threshold " + str(maxG) + " for the max of the G value")
    return max_G


#------RED---------
def onTrackbarmin_R(minR):
    global min_R
    min_R = minR
    print("Threshold " + str(minR) + " for the min of the R value")
    return min_R


def onTrackbarmax_R(maxR):
    global max_R
    max_R = maxR
    print("Threshold " + str(maxR) + " for the max  of the R value")
    return max_R



  
def cam_test(video_capture, max_B,min_B,max_G,min_G,max_R,min_R):
    
    # Capture frame-by-frame from the video - create one capture for the original frame and other for the mask
    _, frame = video_capture.read()
    
    
    #--------
    #Processing 
    #---------    
    
                #save the original to compare to the thresholded


    vid_thresh = frame.copy()
    
    #creates a dictionary for the max and min values chosen 
    total_limits={'limits':{'B':{'max':max_B, 'min':min_B}, 'G':{'max':max_G, 'min':min_G}, 'R':{'max':max_R, 'min':min_R}}}
    
    #for the object's color segmentation we have to use the inRange function for the mask creation, so we can apply the segmentation
    #with the maximum and minimum chosen we're using the num
    
    lower_bound=np.array([total_limits['limits']['B']['min'], total_limits['limits']['G']['min'],total_limits['limits']['R']['min']])
    upper_bound=np.array([total_limits['limits']['B']['max'], total_limits['limits']['G']['max'],total_limits['limits']['R']['max']])
    
    #masking the image using in.range function
    vid_mask=cv2.inRange(vid_thresh,lower_bound, upper_bound)
    
    
    #--------
    #Visualization 
    #---------
            
    cv2.imshow('Mask', vid_mask)       
    cv2.imshow('Original', frame)
    k=cv2.waitKey(1)

    return k, frame, total_limits, vid_mask



def main():
    #--------
    #Initialization
    #---------
    
    # creates global variables so they can be changed by the user 
    
    global min_B, min_G, min_R, max_B, max_G, max_R
    
    min_B = 0
    min_G = 0
    min_R = 0
    max_B = 255
    max_G = 255
    max_R = 255


    #--------
    #Execution
    #---------
    # Creates the Trackbars
    
    cv2.namedWindow("Assignment 2", cv2.WINDOW_AUTOSIZE)
    
    #cv2.createTrackbar('Trackbar_label', 'Window_Name', start_value, max_value, callback)
    cv2.createTrackbar('Min B', 'Assignment 2', 0, 255, onTrackbarmin_B)
    cv2.createTrackbar('Max B', 'Assignment 2', 255, 255, onTrackbarmax_B)
    cv2.createTrackbar('Min G', 'Assignment 2', 0, 255, onTrackbarmin_G)
    cv2.createTrackbar('Max G', 'Assignment 2', 255, 255, onTrackbarmax_G)
    cv2.createTrackbar('Min R', 'Assignment 2', 0, 255, onTrackbarmin_R)
    cv2.createTrackbar('Max R', 'Assignment 2', 255, 255, onTrackbarmax_R)

    #it loads the video from the webcam
    
    video_capture = cv2.VideoCapture(0)
    
    if not video_capture.isOpened():  # Check if the web cam is opened correctly
        print("failed to open cam")
    else:
    
        while True:   
            k,frame,total_limits,vid_mask=cam_test(video_capture, max_B,min_B,max_G,min_G,max_R,min_R)
  
    #--------
    #Termination
    #---------
##nao esta a funcionar bem 
            if k==ord('q'):
                image_gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                moment= cv2.moments(image_gray)
                X = int(moment ["m10"] / moment["m00"])
                Y = int(moment ["m01"] / moment["m00"])
                cv2.putText(frame, 'The end of the program', (X,Y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
                break
            elif k==ord('w'):
                with open('limits.json', 'w') as arquivo:
                    arquivo.write(json.dumps(total_limits))
              
  
if __name__ == '__main__':
    main()