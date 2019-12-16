# Give your robot the gift of intelligent sight
EVS is code designed to bring machine learning object detection to the First Robotics Competition. It was designed from the ground up for FRC teams, from a FRC team. The program makes it easy to generate code that runs complicated neural networks. EVS, also known as Edge Vision System, is named after it's core component, EdgeIQ. 

## Why Neural Networks?
The first question that needs to be answered is, "Why you would machine learning in the first place?" The benefits are as follows:

1. More accurate object detection
2. A single vision pipeline can be used to detect as many objects as you like
3. Wider target angles - robot doesn't need to spare up to the target before the robot can detect it.
4. Universal setup, can be used in any environment without recalibration
5. Built-in frame-by-frame object tracking

## What are the drawbacks?
There are 2 drawbacks. The first is the creation of the machine learning model. This is avoided by using our model (used in tutorial), but if you further want more or different objects, you will have to take the time to train a new model. The second drawback is processing power. In our setup, EVS is able to achieve 10 frames per second. Compared to the ~360 frames of a similar implementation such as Chameleon Vision, this is a small amount. Considering the fps difference, this may seem like a huge drawback. However. considering that path finding calculations, such as those used by 254, the Cheesy Poofs, take 10ms to complete on a standard Rio, this supposed drawback isn't that influential. Even if a team used every frame, they would spend ~10% of the processor's cycles on motion planning. This repeated motion planning is more than enough to saturate a Rio to the point where it becomes slow to respond, or sluggish. In reality, a frame a second would be fine. If this is still a problem, other single board computers, such as a Nvidia Jetson, could be used for a higher framerate.

## Why has no one else been able to implement a solution similar to EVS in the past? 
Unfortunately, systems that use machine learning are both complicated to set up, but also complicated to keep running. The library that this code is built around the EdgeIQ library from AlwaysAi. This library allows the quick and easy generation and setup of dedicated Docker images, with little effort to the user. EVS is a implementation of this library in a way that allows teams to worry more about writing robot code, not vision. 

## Requirements:
As with any project, a few items are needed
1. Raspberry Pi
2. A micro SD card for the Pi
4. An Ethernet cable to connect the coprocessor (#1) to the robot's radio
5. A USB webcam
6. Java - based RoboRio code
7. (Optional) A Intel Neural Compute Stick 2. This can be used to obtain higher frame rates.

## Setup
This is the standard implementation of the EVS system. It uses a Raspberry Pi as the coprocessor. Further options for more advanced users can be found in the improvements section.
1. Linux installation onto a RasPi (Raspberry Pi)
  - Download the RasPi image from the Dropbox link. Extract the .zip once it finishes.
  - Install the burning software of your choice. Our team uses [Win32 Disk Imager.](https://sourceforge.net/projects/win32diskimager/)
  - Insert your micro SD card into your computer
  - Open File Explorer (Windows) or Finder (Mac) to ensure that your SD card appears. Make sure to remember the letter before the name of the drive (ex. E:)
  - Launch the burning software, in this example Win32 Disk Imager, and click the folder icon to select the .iso file that was extracted from the image download. Then select the letter of your drive under devices, and click write. This will take a while.
  - Connect the RasPi with an Ethernet cable to the radio of your robot.




