import cv2
import numpy as np
from colorama import Fore, Back, Style
from enum import Enum
import math



def evaluation(image,image_solution,limit_values):

    
    boundaries = [((110, 50, 50), (130, 255, 255)), ((36, 25, 25), (70, 255, 255)), ((0, 0, 0), (9, 255, 255))]
    color_result = []
    Acc_by_color = {}

    for (lower, upper) in boundaries:

        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image_solution = cv2.cvtColor(image_solution,cv2.COLOR_BGR2RGB)
            
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")

        width = image.shape[1]
        height = image.shape[0]

        dim = (width,height)

        image_solution = cv2.resize(image_solution, dim, interpolation = cv2.INTER_AREA)

        ## convert to hsv both our drawing and the painted one
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        color_used= cv2.inRange(rgb, lower, upper)

        rgb_s = cv2.cvtColor(image_solution, cv2.COLOR_BGR2RGB)
        color_real = cv2.inRange(rgb_s, lower, upper)


        # we also need to remove the small components from the painted mask
        kernel = np.ones((5, 5), np.uint8)

        color_real = cv2.erode(color_real, kernel, 1)
        color_real = cv2.dilate(color_real, kernel, 1)

        # the masks of every color
        # the part painted that is right
        bitwiseAnd = cv2.bitwise_and(color_real, color_used)

        # ALL THE Paint
        bitwiseor = cv2.bitwise_or(color_used,color_real)


        # calculus
        bitwiseor[bitwiseor > 0] = 1
        bitwiseAnd[bitwiseAnd > 0] = 1

        painted = sum(sum(bitwiseAnd))
        total = sum(sum(bitwiseor))

        acc  = (painted / total) * 100


        color_result.append(acc)

    print(color_result)

    Acc_by_color = {"Blue": color_result[0],"Green": color_result[1],"Red": color_result[2]}

    print("The accuracy of the paiting is:" + str(Acc_by_color))




def program_instructions():
    print(Style.BRIGHT + 'Function of every key:')
    print(Style.BRIGHT + 'Colors:')
    print(Style.BRIGHT + Fore.RED + 'Red: ' + Style.RESET_ALL + 'r')
    print(Style.BRIGHT + Fore.BLUE + 'Blue: ' + Style.RESET_ALL + 'b')
    print(Style.BRIGHT + Fore.GREEN + 'Green: ' + Style.RESET_ALL + 'g\n')
    print(Style.BRIGHT + 'Thickness:')
    print(Style.BRIGHT + 'More thickness: ' + Style.RESET_ALL + '+')
    print(Style.BRIGHT + 'Less thickness: ' + Style.RESET_ALL + '-\n')
    print(Style.BRIGHT + 'Shapes:')
    print(Style.BRIGHT + 'Squares: ' + Style.RESET_ALL + 's')
    print(Style.BRIGHT + 'Circles: ' + Style.RESET_ALL + 'o')
    print(Style.BRIGHT + 'Draw in the video: ' + Style.RESET_ALL + 'm')
    print(Style.BRIGHT + 'Paint-by-number test: ' + Style.RESET_ALL + 't')
    print(Style.BRIGHT + 'finish / accuracy of the test: ' + Style.RESET_ALL + 'f\n')
    print(Style.BRIGHT + 'Save image: ' + Style.RESET_ALL + 'w')
    print(Style.BRIGHT + 'Clear the canvas: ' + Style.RESET_ALL + 'c')
    print(Style.BRIGHT + 'Quit: ' + Style.RESET_ALL + 'q')

def removeSmallComponents(image, threshold):
    # find all your connected components (white blobs in your image)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
    sizes = stats[1:, -1]
    nb_components = nb_components - 1
    x = None
    y = None
    img2 = np.zeros(output.shape, dtype=np.uint8)

    # for every component in the image, you keep it only if it's above threshold
    for i in range(0, nb_components):
        if sizes[i] >= threshold:
            # to use the biggest
            x, y = centroids[i + 1]
            threshold = sizes[i]
            img2[output == i + 1] = 255

    return img2, x, y
