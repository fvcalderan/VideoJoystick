# This is Video Joystick's main program
# Copyright (C) 2021 Felipe V. Calderan <fvcalderan@gmail.com>
# Copyright (C) 2021 Silvio de Souza Neves Neto <nevesuser@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import cv2
import pickle
import numpy as np
from pynput.keyboard import Key, Controller

# Important global variables
VIDEO_DEVICE_NUM = 0
NUM_OF_BUTTONS = 4
VIEW_THRESH    = False

keyboard = Controller()

# Helper functions
get_gray = lambda s_frame : cv2.medianBlur(
    cv2.cvtColor(s_frame, cv2.COLOR_BGR2GRAY), 9)

get_thresh = lambda s_frame : cv2.threshold(
    s_frame, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

# Font to display text
font = cv2.FONT_HERSHEY_SIMPLEX

# Configuration dictionary
with open('calibration.dat', 'rb') as f:
    pd = pickle.load(f)
CENTROIDS = (pd['CENTR'][0], pd['CENTR'][1],
             pd['CENTR'][2], pd['CENTR'][3])

# Webcam video capture
cap = cv2.VideoCapture(VIDEO_DEVICE_NUM)

while True:
    ret, frame = cap.read()

    # Crop the frame
    frame = frame[pd['RECT'][1]:pd['RECT'][3], pd['RECT'][0]:pd['RECT'][2]]

    # Set to gray scale
    gray = get_gray(frame)

    ret, thresh = get_thresh(gray)

    # Identify all the contours
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
    )

    # Pressed buttons set
    pressed = set()

    for c in contours:
        # calibrated specifications
        condition1=pd['MED_AREA']-pd['ARANGE']  < cv2.contourArea(c)\
                                                < pd['MED_AREA']+pd['ARANGE']
        condition2=pd['MED_PERIM']-pd['PRANGE'] < cv2.arcLength(c, True)\
                                                < pd['MED_PERIM']+pd['PRANGE']

        # If the contour has the calibrated specifications, draw it
        if condition1 and condition2:
            cframe = cv2.drawContours(frame, c, -1, (0, 255, 0), 3)
        else:
            cframe = frame

        # Calculate the moments matrix for the contour
        M = cv2.moments(c)

        # Get the centroids from the moments matrix
        mx, my = int(M['m10']/(M['m00']+0.1)), int(M['m01']/(M['m00']+0.1))

        # Check if a button was pressed by verifying if its contour's
        # centroid is inside the calibrated range for this button
        for i, ct in enumerate(CENTROIDS):
            if ((ct[0]-pd['RECT'][0]-mx)**2 +\
                (ct[1]-pd['RECT'][1]-my)**2)**(1/2) < 6:
                pressed.add(i)

    # Get the length of buttons pressed. If zero, display nothing and release
    # keyboard emulated key presses.
    if len(set(range(NUM_OF_BUTTONS)) - pressed) == 0:
        cv2.putText(
            cframe, f'Buttons Pressed: {{}}',
            (25, 25), font, 1, (0, 255, 255), 2, cv2.LINE_4
        )
        for key in pd['KEYS']:
            keyboard.release(chr(key))

    # If not zero, display pressed buttons and emulate appropriate key press
    else:
        pressed_set = set(range(NUM_OF_BUTTONS)) - pressed
        cv2.putText(
            cframe, f'Buttons Pressed: {pressed_set}',
            (25, 25), font, 1, (0, 255, 255), 2, cv2.LINE_4
        )
        for i in range(NUM_OF_BUTTONS):
            if i in pressed_set: keyboard.press(chr(pd['KEYS'][i]))

    # Check if the user wants to see the camera or threshold
    if VIEW_THRESH:
        cv2.imshow('Video Joystick Threshold', thresh)
    else:
        cv2.imshow('Video Joystick', cframe)

    # Check for input
    if k := cv2.waitKey(1):
        if k == ord('P') or k==ord('p'):
            VIEW_THRESH = not VIEW_THRESH
            cv2.destroyAllWindows()
        if k == ord(' '): break

cap.release()
cv2.destroyAllWindows()
