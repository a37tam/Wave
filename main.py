from math import sqrt, degrees, acos
from platform import system
import cv2
import pyautogui

def getVideoCaptureObject():
    name = system()
    if name == "Windows":
        c = cv2.VideoCapture( 0, cv2.CAP_DSHOW )
    elif name == "Linux" or name == "Darwin":
        c = cv2.VideoCapture( 0 )
    else:
        raise Exception( "Wave only supports Windows, Linux, and Mac." )
    return c

def getVector( pt1, pt2 ):
    return [pt1[0] - pt2[0], pt1[1] - pt2[1]]

def getDistance( v ):
    return sqrt( pow( v[0], 2 ) + pow( v[1], 2 ) )

# Return angle between line segments pt1pt3 and pt2pt3
def getAngle( pt1, pt2, pt3 ):
    v1 = getVector( pt1, pt3 )
    v2 = getVector( pt2, pt3 )
    x = v1[0] * v2[0] + v1[1] * v2[1]
    y = getDistance( v1 ) * getDistance( v2 )
    return degrees( acos(x / y) )

def main():
    # Disable fail-safe mode.
    # When fail-safe mode is True, moving the mouse to the upper left corner will
    #  raise a pyautogui.FailSafeException that can abort your program.
    pyautogui.FAILSAFE = False

    # Capture video from webcam
    videoCapture = getVideoCaptureObject()

    # Screen resolution
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

    # Frame resolution
    FRAME_WIDTH = videoCapture.get( cv2.CAP_PROP_FRAME_WIDTH )
    FRAME_HEIGHT = videoCapture.get( cv2.CAP_PROP_FRAME_HEIGHT )

    # Scale frame dimensions to screen dimensions
    SCALE_X = SCREEN_WIDTH / FRAME_WIDTH
    SCALE_Y = SCREEN_HEIGHT / FRAME_HEIGHT

    while ( videoCapture.isOpened() ):
        ret, frame = videoCapture.read()

        # Flip image around the y axis
        frame = cv2.flip( frame, 1 )

        grayscaleImage = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )

        KERNEL_SIZE = (30, 30)
        blurredImage = cv2.blur( grayscaleImage, KERNEL_SIZE )

        MIN_INTENSITY = 0
        MAX_INTENSITY = 255
        ret, binaryImage = cv2.threshold( blurredImage,
                                          MIN_INTENSITY,
                                          MAX_INTENSITY,
                                          cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU )

        contours, hierarchy = cv2.findContours( binaryImage.copy(),
                                                cv2.RETR_EXTERNAL,
                                                cv2.CHAIN_APPROX_SIMPLE )

        contour = max( contours, key=cv2.contourArea )

        # Draw largest contour
        CONTOUR_COLOUR = (0, 255, 0)
        CONTOUR_THICKNESS = 2
        cv2.drawContours( frame, [contour], -1, CONTOUR_COLOUR, CONTOUR_THICKNESS )

        # Draw convex hull
        hull = cv2.convexHull( contour, returnPoints=True )
        CONVEX_HULL_COLOUR = (0, 0, 255)
        cv2.drawContours( frame, [hull], -1, CONVEX_HULL_COLOUR, CONTOUR_THICKNESS )

        hullIndices = cv2.convexHull( contour, clockwise=False, returnPoints=False )
        convexityDefects = cv2.convexityDefects( contour, hullIndices )

        # Determine which defects correspond to the user's hand
        relevantDefects = []
        for i in range( 0, len( convexityDefects ) ):
            s, e, f, d = convexityDefects[i, 0]
            pt1 = contour[s][0]
            pt2 = contour[e][0]
            pt3 = contour[f][0]
            if getAngle( pt1, pt2, pt3 ) < 90:
                if relevantDefects == [] or getDistance( getVector( relevantDefects[-1], pt1 ) ) > 20:
                    relevantDefects.append( pt1 )
                relevantDefects.append( pt2 )

        # Draw circles to represent all relevant convexity defects
        CIRCLE_COLOUR = (255, 255, 255)
        CIRCLE_RADIUS = 5
        CIRCLE_OUTLINE_THICKNESS = 3
        for i in range( 0, len( relevantDefects ) ):
            cv2.circle( frame,
                        tuple( relevantDefects[i] ),
                        CIRCLE_RADIUS,
                        CIRCLE_COLOUR,
                        CIRCLE_OUTLINE_THICKNESS )

        # Determine mouse's action
        numberOfDefects = len( relevantDefects )
        if numberOfDefects == 2:
            x = relevantDefects[0][0] * SCALE_X
            y = relevantDefects[0][1] * SCALE_Y
            pyautogui.moveTo( x, y, duration=0.1 )
        elif numberOfDefects == 3:
            pyautogui.click( button='left' )
        elif numberOfDefects == 4:
            pyautogui.click( button='right' )
        else:
            pass

        cv2.imshow( 'Wave', frame )

        # Press "q" to exit Wave when the application window has focus
        if cv2.waitKey( 1 ) & 0xFF == ord( 'q' ):
            break

    cv2.destroyAllWindows()
    videoCapture.release()

if __name__ == "__main__":
    main()
