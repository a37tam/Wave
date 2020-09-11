# Wave-2.0

A Python script which lets users control their cursor using hand gestures. [Take a look!](https://youtu.be/OOSNbBzDD1I)

![Hand Detection](Images/hand-detection.png?style=centerme)

### Getting Started

Clone and <code>cd</code> into the the repository.

```
git clone https://github.com/a37tam/Wave-2.0.git
cd Wave-2.0
```

Create a virtual environment to manage all the dependencies listed in <code>requirements.txt</code>.

```
python3 -m venv env
pip3 install -r requirements.txt
```

Run the Python script.

```
python3 main.py
```

## Implementation

Access video stream from the laptop's webcam.

For each individual frame,

1. Perform colour space conversion from BGR (the default colour space in OpenCV) to grayscale.
2. Convolve a blurring kernel over the frame to reduce background noise. 
3. Determine an appropriate pixel intensity threshold value. Use this threshold to obtain a binary image.
4. Process all the contours in the binary image and select the contour with the greatest area. This is the user's hand.
5. Obtain the convex hull of the largest contour.
6. From the convex hull, extract the total number of convexity defects and their coordinates.
7. Based on these convexity defects, invoke the corresponding mouse event.
