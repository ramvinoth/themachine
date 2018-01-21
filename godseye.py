import numpy # Hint to PyInstaller
from CVForwardCompat import cv2
import os
import socket
import sys
import time
import ctypes

import BinasciiUtils
import GeomUtils
import MailUtils
import PyInstallerUtils
import ResizeUtils
import IdGenerator


def recognizeAndReport(recognizer, grayImage, rects, maxDistance,
                       noun='human'):
    for x, y, w, h in rects:
        print "recognized"
        crop = cv2.equalizeHist(grayImage[y:y+h, x:x+w])
        labelAsInt, distance = recognizer.predict(crop)
        labelAsStr = BinasciiUtils.intToFourChars(labelAsInt)
        #cv2.imshow('Found', crop)
        randomid = IdGenerator.id_generator()

        print noun, labelAsStr, distance
        if distance <= maxDistance:
            print "Inside email"
            cv2.imwrite("found_Faces/found_%s_%s.jpg" %(labelAsStr ,randomid),crop)
            cv2.imwrite("found_Faces/withBg/found_%s_%s.jpg" %(labelAsStr ,randomid),grayImage)
       	    fromAddr = 'ramvinoth37@gmail.com' # TODO: Replace
            toAddrList = ['vinothvallavan6@gmail.com'] # TODO: Replace
            ccAddrList = []
            subject = 'God\'s Eye'
            #message = 'We have sighted the %s known as %s.' % \
            #        (noun, labelAsStr)
            login = 'ramvinoth37@gmail.com' # TODO: Replace
            password = 'Wdcvgy1$3' # TODO: Replace
            # TODO: Replace if not using Gmail.
            smtpServer='smtp.gmail.com:587'
            try:
                problems = MailUtils.sendEmail(
                        fromAddr, toAddrList, ccAddrList, subject, labelAsStr, randomid,
                        login, password, smtpServer)
                if problems:
                    print >> sys.stderr, 'Email problems:', problems
                else:
                    return True
            except socket.gaierror:
                print >> sys.stderr, 'Unable to reach email server'
        else:
            print "unknown..........",distance
            cv2.imwrite("Unknown_Faces/new_%s_%s.jpg" %(labelAsStr,distance),crop)
            cv2.imwrite("Unknown_Faces/withBg/new_%s.jpg",grayImage)
            user32 = ctypes.cdll.LoadLibrary("user32.dll") 
            user32.LockWorkStation()
            time.sleep(50)
    return False

def main():

    humanCascadePath = PyInstallerUtils.resourcePath(
            # Uncomment the next argument for LBP.
            #'cascades/lbpcascade_frontalface.xml')
            # Uncomment the next argument for Haar.
            'cascades/haarcascade_frontalface_alt.xml')
    humanRecognizerPath = PyInstallerUtils.resourcePath(
            'recognizers/lbph_human_faces.xml')
    if not os.path.isfile(humanRecognizerPath):
        print >> sys.stderr, \
                'Human face recognizer not trained. Exiting.'
        print humanRecognizerPath
      

    capture = cv2.VideoCapture(0)
    imageWidth, imageHeight = \
            ResizeUtils.cvResizeCapture(capture, (1280, 720))
    minImageSize = min(imageWidth, imageHeight)

    humanDetector = cv2.CascadeClassifier(humanCascadePath)
    humanRecognizer = cv2.createLBPHFaceRecognizer()
    humanRecognizer.load(humanRecognizerPath)
    humanMinSize = (int(minImageSize * 0.25),
                    int(minImageSize * 0.25))
    humanMaxDistance = 100


    while True:
        print "start"
        success, image = capture.read()
        if image is not None:
            grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            equalizedGrayImage = cv2.equalizeHist(grayImage)

            humanRects = humanDetector.detectMultiScale(
                    equalizedGrayImage, scaleFactor=1.3,
                    minNeighbors=4, minSize=humanMinSize,
                    flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
            if recognizeAndReport(
                    humanRecognizer, grayImage, humanRects,
                    humanMaxDistance, 'human'):
                break

if __name__ == '__main__':
    main()
