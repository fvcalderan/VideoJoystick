# Video Joystick
Simple computer vision program to create joysticks out of paper

## How to install
This procedure should be standard across platforms. First, make sure you have
the latest stable version of `Python3` and `pip3` installed on your system.
Then, open up a terminal in Video Joystick's root folder and type:
```
pip3 install -r requirements.txt
```
Wait for the dependencies installation to finish and you should be able to
proceed to te controller's calibration.

## Calibrating the controller
Before using the controller, it's important to calibrate it. Point your
webcam to the controller, preferably in a top-down manner (or with as little
angle as possible) and execute `calibrate.py`.

### Calibrate Position
The first screen "Calibrate Position" shows what your camera is seeing.
Position the controller as centered and straight as possible. The buttons
shouldn't be too near the lateral borders of the screen. When you are satisfied
with the position, press the `Left Mouse Button` to continue.

### Calibrate Contours
The next screen lets you fine-tune the contour finding system. If you
positioned the controller accordingly in the previous step and you are in a
properly illuminated ambient, the buttons should already be marked with a
green circle (indicating they have been recognized). If not, it's highly
recommended that you redo the first step, but it's also possible to fix the
problem in this one.

Notice two lines in yellow text: `Area` and `Perimeter`. They show you the
range for these geometric features in which Video Joystick is looking for
buttons. Here, you should fine-tune so that it's as strict as possible, without
causing interference (an exception to this rule would be if you want to be able
to move the controller around a bit, then you shouldn't be too strict). To
change the parameters, use the following hotkeys:
```
W and S: Increase/decrease Area range
E and D: Increase/decrease Perimeter range
R and F: Increase/decrease Area offset
T and G: Increase/decrease Perimeter offset
```
When it's well calibrated, press the `Left Mouse Button` to continue or the
`Right Mouse Button` to go back.

### Button Bindings
Now, it's time to bind keyboard keys to Video Joystick. To do this, for each
button (on at a time) in Video Joystick, keep the button pressed, then press
the desired key on the computer's keyboard. This will generate a new key
binding. The order in which the characters appear on the yellow text doesn't
need to reflect the position of the buttons. When all the buttons have been
configured, press the `Left Mouse Button` to finish the calibration or the
`Right Mouse Button` to go back.

### Calibration file
After the calibration has been successfully completed, a binary file called
`calibration.dat` is generated. This file contains all the necessary
calibration information for Video Joystick to execute. It should be in the same
folder as `video_joystick.py`.

## Running Video Joystick
Having a valid (and adequate) `calibration.py` file on the folder, run
`video_joystick.py`. To exit the program, selection Video Joystick's screen
and press `SPACE`.

## Troubleshooting

### Neither .py files open
Your camera is probably offline or in a different device number (and not the
expected default `0`). Change the constant `VIDEO_DEVICE_NUM` in both source
codes to your device number (which is typically a low number, like `0`, `1` or
`2`.

## Article, SI and Video Recordings

[Link to the Article](https://fvcalderan.github.io/myworks/articles/video_joystick_article.pdf)

[Link to the Supporting Information](https://fvcalderan.github.io/myworks/articles/video_joystick_SI.pdf)

[Link to the Video](https://youtu.be/FDVQ30AovbA)

## License
```
Copyright (C) 2021 Felipe V. Calderan <fvcalderan@gmail.com>
Copyright (C) 2021 Silvio de Souza Neves Neto <nevesuser@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
