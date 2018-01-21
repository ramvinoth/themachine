"""
Simple app that demonstrates how to use a wx.StaticBitmap, specifically
replacing bitmap dynamically.

Note: there needs to be an "Images" directory with one or more jpegs in it in the
      current working directory for this to work

Test most recently on OS-X wxPython 2.9.3.1

But it been reported to work on lots of other platforms/versions

"""
import numpy
from CVForwardCompat import cv2
from InteractiveRecognizer import InteractiveRecognizer
import os
import sys
import threading
import wx

import BinasciiUtils
import ResizeUtils
import WxUtils
import PyInstallerUtils

class TrainModel(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        # there needs to be an "Images" directory with one or more jpegs in it in the
        # current working directory for this to work
        self.jpgs = GetJpgList("./found_Faces/withBg") # get all the jpegs in the Images directory
        self.CurrentJpg = 0
        cascadePath = PyInstallerUtils.resourcePath('cascades/haarcascade_frontalface_alt.xml')
        print cascadePath
        self._detector = cv2.CascadeClassifier(cascadePath)
        humanRecognizerPath = PyInstallerUtils.resourcePath(
            'cascades/haarcascade_frontalface_default.xml')
        humanEyeRecognizerPath = PyInstallerUtils.resourcePath(
                    'cascades/haarcascade_eye.xml')
        #print "Path 1: %s" %humanRecognizerPath
        #print "Path 2: %s" %humanEyeRecognizerPath
        self._faceCascade = cv2.CascadeClassifier(humanRecognizerPath)
        self._eye_cascade = cv2.CascadeClassifier(humanEyeRecognizerPath)
        
        
        recognizerPath = PyInstallerUtils.resourcePath(
                'recognizers/lbph_human_faces.xml')
        self._recognizerPath = recognizerPath
        self._recognizer = cv2.createLBPHFaceRecognizer()
        if os.path.isfile(recognizerPath):
            self._recognizer.load(recognizerPath)
            self._recognizerTrained = True
        else:
            self._recognizerTrained = False
        
        self._referenceTextCtrl = wx.TextCtrl(
                self, style=wx.TE_PROCESS_ENTER)
        self._referenceTextCtrl.SetMaxLength(4)
        self._referenceTextCtrl.Bind(
                wx.EVT_KEY_UP, self._onReferenceTextCtrlKeyUp)
                
        self._updateModelButton = wx.Button(
                self, label='Add to Model')
        self._updateModelButton.Bind(
                wx.EVT_BUTTON, self._updateModel)
        self._updateModelButton.Disable()
        
        controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
        controlsSizer.Add(self._referenceTextCtrl, 0,
                          wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                          12)
        controlsSizer.Add(
                self._updateModelButton, 0,
                wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)
        controlsSizer.Add((0, 0), 1) # Spacer
        
        self.MaxImageSize = 200
        
        b = wx.Button(self, -1, "Display next")
        b.Bind(wx.EVT_BUTTON, self.DisplayNext)

        # starting with an EmptyBitmap, the real one will get put there
        # by the call to .DisplayNext()
        self.Image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(self.MaxImageSize, self.MaxImageSize))

        self.DisplayNext()

        # Using a Sizer to handle the layout: I never  use absolute positioning
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(b, 0, wx.CENTER | wx.ALL,10)

        # adding stretchable space before and after centers the image.
        box.Add((1,1),1)
        box.Add(self.Image, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        box.Add((1,1),1)
        
        box.Add(controlsSizer, 0, wx.EXPAND | wx.ALL, 12)
        
        self.SetSizerAndFit(box)
        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

    def DisplayNext(self, event=None):
        # load the image
        Img = wx.Image(self.jpgs[self.CurrentJpg], wx.BITMAP_TYPE_JPEG)
        
        Image = cv2.imread(self.jpgs[self.CurrentJpg])
        #print Img
        detectedImg = self._detectAndRecognize(Image)
        #detectedImg = self._detectFace(Image)
        cv2.imshow("detected",detectedImg)
        # scale the image, preserving the aspect ratio
        W = Img.GetWidth()
        H = Img.GetHeight()
        if W > H:
            NewW = self.MaxImageSize
            NewH = self.MaxImageSize * H / W
        else:
            NewH = self.MaxImageSize
            NewW = self.MaxImageSize * W / H
        Img = Img.Scale(NewW,NewH)
 
        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.Image.SetBitmap(wx.BitmapFromImage(Img))

        # You can fit the frame to the image, if you want.
        #self.Fit()
        #self.Layout()
        self.Refresh()

        self.CurrentJpg += 1
        if self.CurrentJpg > len(self.jpgs) -1:
            self.CurrentJpg = 0
    
    def _onReferenceTextCtrlKeyUp(self, event):
        self._enableOrDisableUpdateModelButton()
    
    def _updateModel(self, event):
        labelAsStr = self._referenceTextCtrl.GetValue()
        labelAsInt = BinasciiUtils.fourCharsToInt(labelAsStr)
        src = [self._currDetectedObject]
        labels = numpy.array([labelAsInt])
        if self._recognizerTrained:
            self._recognizer.update(src, labels)
            print "added"
        else:
            self._recognizer.train(src, labels)
            self._recognizerTrained = True
            self._clearModelButton.Enable()
            print "created"
    
    def onCloseWindow(self, event):
        self._running = False
        if self._recognizerTrained:
            modelDir = os.path.dirname(self._recognizerPath)
            print 'Creating.... %s' % modelDir
            if not os.path.isdir(modelDir):
                os.makedirs(modelDir)
            self._recognizer.save(self._recognizerPath)
        self.Destroy()
        
    def _detectAndRecognize(self, image):
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        equalizedGrayImage = cv2.equalizeHist(grayImage)
        rects = self._detector.detectMultiScale(
                equalizedGrayImage, scaleFactor=1.3,
                minNeighbors=2,
                minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        for x, y, w, h in rects:
            cv2.rectangle(image, (x, y), (x+w, y+h),
                          (0, 255, 0), 1)
        if len(rects) > 0:
            x, y, w, h = rects[0]
            self._currDetectedObject = cv2.equalizeHist(
                    grayImage[y:y+h, x:x+w])
            print "Success"
        else:
            self._currDetectedObject = None
        return image
    
    def _detectFace(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self._faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        img = frame
        if self._faceCascade.empty(): raise Exception("your cascade is empty. are you sure, the path is correct ?")
        faces = self._faceCascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = self._eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

        # Display the resulting frame
            return frame    
    
    def _enableOrDisableUpdateModelButton(self):
        labelAsStr = self._referenceTextCtrl.GetValue()
        if len(labelAsStr) < 1 or \
                    self._currDetectedObject is None:
            self._updateModelButton.Disable()
        else:
            self._updateModelButton.Enable()
            
def GetJpgList(dir):
    jpgs = [f for f in os.listdir(dir) if f[-4:] == ".jpg"]
    # print "JPGS are:", jpgs
    return [os.path.join(dir, f) for f in jpgs]

class App(wx.App):
    def OnInit(self):

        frame = TrainModel(None, -1, "Train", wx.DefaultPosition,size = (550,200))
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

if __name__ == "__main__":
    app = App(0)
    app.MainLoop()