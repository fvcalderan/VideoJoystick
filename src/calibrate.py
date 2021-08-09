# This is Video Joystick's calibration program
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

import cv2
import pickle
import numpy as np

# Important global variables
VIDEO_DEVICE_NUM = 0
ESTIMATE_PRECISION = 30
NUM_OF_BUTTONS = 4

# Helper functions
get_gray = lambda s_frame : cv2.medianBlur(
    cv2.cvtColor(s_frame, cv2.COLOR_BGR2GRAY), 9)

get_thresh = lambda s_frame : cv2.threshold(
    s_frame, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)


def calibrate_position(cap : cv2.VideoCapture, pd : dict) -> int:
    next_step = 2
    end_step = False

    while True:
        ret, frame = cap.read()
        cv2.imshow('Calibrate Position (Mouse 1 to confirm)', frame)

        # Check for input
        cv2.waitKey(1)

        # Mouse controls
        def onMouse(event, x, y, flags, param):
            nonlocal end_step, next_step
            if event == cv2.EVENT_LBUTTONDOWN:
                end_step = True
        cv2.setMouseCallback(
            'Calibrate Position (Mouse 1 to confirm)', onMouse
        )
        if end_step:
            break

    cv2.destroyAllWindows()
    return next_step


def approximate_contours(cap : cv2.VideoCapture, pd : dict):
    contour_tuples = []

    for i in range(ESTIMATE_PRECISION):
        ret, frame = cap.read()
        gray = get_gray(frame)
        ret, thresh = get_thresh(gray)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
        )
        for c in contours:
            contour_tuples.append((cv2.contourArea(c),
                                   cv2.arcLength(c, True)))
        cv2.imshow('Please Wait...', frame)

    cv2.destroyAllWindows()

    CONTOURS_DATA = list(zip(*contour_tuples))
    CD_AREA, CD_PERIM = CONTOURS_DATA
    pd['MED_AREA']  = np.median(CD_AREA)
    pd['MED_PERIM'] = np.median(CD_PERIM)


def calibrate_contours(cap : cv2.VideoCapture, pd : dict) -> int:
    next_step = 3
    end_step = False

    approximate_contours(cap, pd)

    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, frame = cap.read()
        gray = get_gray(frame)
        ret, thresh = get_thresh(gray)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
        )
        for c in contours:
            condition1 = pd['MED_AREA'] - pd['ARANGE']\
                       < cv2.contourArea(c)\
                       < pd['MED_AREA'] + pd['ARANGE']

            condition2 = pd['MED_PERIM'] - pd['PRANGE']\
                       < cv2.arcLength(c, True)\
                       < pd['MED_PERIM'] + pd['PRANGE']

            if condition1 and condition2:
                cframe = cv2.drawContours(frame, c, -1, (0, 255, 0), 3)
            else:
                cframe = frame

        text1 = ' '.join([f"Area:      {int(pd['MED_AREA']-pd['ARANGE'])}",
                         f"~ {int(pd['MED_AREA']+pd['ARANGE'])}"])
        text2 = ' '.join([f"Perimeter: {int(pd['MED_PERIM']-pd['PRANGE'])}",
                          f"~ {int(pd['MED_PERIM']+pd['PRANGE'])}"])
        cv2.putText(cframe, text1, (50, 50), font, 1,
                    (0, 255, 255), 2, cv2.LINE_4)
        cv2.putText(cframe, text2, (50, 100),font, 1,
                    (0, 255, 255), 2, cv2.LINE_4)
        cv2.imshow(
            'Calibrate Contours (Mouse 1 to confirm / 2 to back)', cframe
        )

        if k := cv2.waitKey(1):
            if (k == ord('S') or k == ord('s')) and pd['ARANGE']    > 50:
                pd['ARANGE']    -= 50
            if (k == ord('W') or k == ord('w')) and pd['ARANGE']    < 3000:
                pd['ARANGE']    += 50
            if (k == ord('D') or k == ord('d')) and pd['PRANGE']    > 25:
                pd['PRANGE']    -= 25
            if (k == ord('E') or k == ord('e')) and pd['PRANGE']    < 3000:
                pd['PRANGE']    += 25
            if (k == ord('F') or k == ord('f')) and pd['MED_AREA']  > 50:
                pd['MED_AREA']  -= 50
            if (k == ord('R') or k == ord('r')) and pd['MED_AREA']  < 9000:
                pd['MED_AREA']  += 50
            if (k == ord('G') or k == ord('g')) and pd['MED_PERIM'] > 50:
                pd['MED_PERIM'] -= 50
            if (k == ord('T') or k == ord('t')) and pd['MED_PERIM'] < 9000:
                pd['MED_PERIM'] += 50

        # Mouse controls
        def onMouse(event, x, y, flags, param):
            nonlocal end_step, next_step
            if event == cv2.EVENT_LBUTTONDOWN:
                end_step = True
            elif event == cv2.EVENT_RBUTTONDOWN:
                end_step = True
                next_step = 1
        cv2.setMouseCallback(
            'Calibrate Contours (Mouse 1 to confirm / 2 to back)', onMouse
        )
        if end_step:
            break

    cv2.destroyAllWindows()
    approximate_screen_rect(cap, pd)
    return next_step


def approximate_screen_rect(cap : cv2.VideoCapture, pd : dict):
    xlist, ylist, wlist, hlist, mlist = [], [], [], [], []
    for i in range(ESTIMATE_PRECISION):
        ret, frame = cap.read()
        gray = get_gray(frame)
        ret, thresh = get_thresh(gray)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
        )
        for c in contours:
            condition1 = pd['MED_AREA'] - pd['ARANGE']\
                       < cv2.contourArea(c)\
                       < pd['MED_AREA'] + pd['ARANGE']

            condition2 = pd['MED_PERIM'] - pd['PRANGE']\
                       < cv2.arcLength(c, True)\
                       < pd['MED_PERIM'] + pd['PRANGE']

            if condition1 and condition2:
                if i == 20:
                    M = cv2.moments(c)
                    mlist.append((int(M['m10']/M['m00']),
                                  int(M['m01']/M['m00'])))
                if i > 20: # wait for image stabilization (safety)
                    x,y,w,h = cv2.boundingRect(c)
                    xlist.append(x)
                    ylist.append(y)
                    wlist.append(w)
                    hlist.append(h)
            else:
                cframe = frame
        cv2.imshow('Please Wait...', cframe)

    cv2.destroyAllWindows()

    pd['CENTR'][0], pd['CENTR'][1], pd['CENTR'][2], pd['CENTR'][3] = mlist
    pd['RECT'][0] = min(xlist)-50
    pd['RECT'][1] = min(ylist)-50
    pd['RECT'][2] = max(np.array(xlist)+np.array(wlist))+50
    pd['RECT'][3] = max(np.array(ylist)+np.array(hlist))+50
    # Window borders are the limit
    pd['RECT'][0] = max(0, pd['RECT'][0])
    pd['RECT'][1] = max(0, pd['RECT'][1])
    pd['RECT'][2] = min(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), pd['RECT'][2])
    pd['RECT'][3] = min(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), pd['RECT'][3])


def calibrate_keys(cap : cv2.VideoCapture, pd : dict) -> int:
    next_step = 4
    end_step = False

    CENTROIDS = (pd['CENTR'][0], pd['CENTR'][1],
                 pd['CENTR'][2], pd['CENTR'][3])

    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, frame = cap.read()
        frame = frame[pd['RECT'][1]: pd['RECT'][3],
                      pd['RECT'][0]: pd['RECT'][2]]
        gray = get_gray(frame)
        ret, thresh = get_thresh(gray)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
        )
        # Pressed buttons set
        pressed     = set()
        pressed_set = set()

        for c in contours:
            condition1 = pd['MED_AREA'] - pd['ARANGE']\
                       < cv2.contourArea(c)\
                       < pd['MED_AREA'] + pd['ARANGE']

            condition2 = pd['MED_PERIM'] - pd['PRANGE']\
                       < cv2.arcLength(c, True)\
                       < pd['MED_PERIM'] + pd['PRANGE']

            if condition1 and condition2:
                cframe = cv2.drawContours(frame, c, -1, (0, 255, 0), 3)
            else:
                cframe = frame

            M = cv2.moments(c)
            mx = int(M['m10']/(M['m00']+0.1))
            my = int(M['m01']/(M['m00']+0.1))
            # Check if a button was pressed by verifying if its contour's
            # centroid is inside the calibrated range for this button
            for i, ct in enumerate(CENTROIDS):
                if ((ct[0]-pd['RECT'][0]-mx)**2 +\
                    (ct[1]-pd['RECT'][1]-my)**2)**(1/2) < 6:
                    pressed.add(i)

        # Write keybindings on the screen
        cv2.putText(
            cframe,
            f"['{chr(pd['KEYS'][0])}', '{chr(pd['KEYS'][1])}', "
            f"'{chr(pd['KEYS'][2])}', '{chr(pd['KEYS'][3])}']",
            (50, 50), font, 1, (0, 255, 255), 2,cv2.LINE_4
        )

        # Get inputs for each button
        if len(set(range(NUM_OF_BUTTONS)) - pressed) != 0:
            pressed_set = set(range(NUM_OF_BUTTONS)) - pressed

        cv2.imshow('Button Bindings (Mouse 1 to confirm / 2 to back)', cframe)

        # Check for input
        if k := cv2.waitKey(1):
            for i in range(NUM_OF_BUTTONS):
                if i in pressed_set and k != -1: pd['KEYS'][i] = k

        # Mouse controls
        def onMouse(event, x, y, flags, param):
            nonlocal end_step, next_step
            if event == cv2.EVENT_LBUTTONDOWN:
                end_step = True
            elif event == cv2.EVENT_RBUTTONDOWN:
                end_step = True
                next_step = 2
        cv2.setMouseCallback(
            'Button Bindings (Mouse 1 to confirm / 2 to back)', onMouse
        )
        if end_step:
            break

    cv2.destroyAllWindows()
    return next_step


def main():
    # Configuration dictionary
    pd = {
        'ARANGE' : 250, 'PRANGE' : 25,
        'MED_AREA' : 100, 'MED_PERIM' : 100, 'RECT' : [0, 0, 50, 50],
        'CENTR' : [[0,0], [0,0], [0,0], [0,0]],
        'KEYS' : [ord(' '), ord(' '), ord(' '), ord(' ')]
    }

    cap = cv2.VideoCapture(VIDEO_DEVICE_NUM)

    step = 1
    procedures = [calibrate_position, calibrate_contours, calibrate_keys]

    while step < 4:
        step = procedures[step-1](cap, pd)

    with open('calibration.dat', 'wb+') as f:
        pickle.dump(pd, f)

    print('Calibrated!')
    cap.release()


if __name__ == '__main__':
    main()
