import numpy # Hint to PyInstaller
import cv2

CV_MAJOR_VERSION = int(cv2.__version__.split('.')[0])
if CV_MAJOR_VERSION > 2:
    
    # Create a dummy object in lieu of the cv2.cv module.
    cv2.cv = lambda : None
    
    # Create aliases to make parts of the OpenCV 3.x library
    # backward-compatible.
    cv2.CV_AA = cv2.LINE_AA
    cv2.CV_LOAD_IMAGE_COLOR = cv2.IMREAD_COLOR
    cv2.SimpleBlobDetector = cv2.SimpleBlobDetector_create
    cv2.cv.CV_CAP_PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
    cv2.cv.CV_CAP_PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
    cv2.cv.CV_FILLED = cv2.FILLED
    cv2.cv.CV_HAAR_SCALE_IMAGE = cv2.CASCADE_SCALE_IMAGE
    try:
        cv2.createLBPHFaceRecognizer = cv2.face.createLBPHFaceRecognizer
    except:
        # The face module from opencv_contrib is unavailable.
        pass
