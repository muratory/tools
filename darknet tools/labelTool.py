#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014

#
#-------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
import tkFileDialog
import tkMessageBox
from PIL import Image, ImageTk
import os
import glob
import random
import cv2

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']

# image sizes for the examples
IMAGE_WIDTH = 600

def convert(size, box):
    dw = 1./float(size[1])
    dh = 1./float(size[0])
    x = box[0]*dw
    w = box[2]*dw
    y = box[1]*dh
    h = box[3]*dh
    return (x,y,w,h)
    
    


class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.labelImage = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.bboxListSaved = ''
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.ldBtn = Button(self.frame, text = "Browse", command = self.askDir)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 40, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBoxAndSave)
        self.btnClear.grid(row = 4, column = 2, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Save+Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        
        self.nnextBtn = Button(self.ctrPanel, text='Next unlabel', width = 15, command = self.nnextImage)
        self.nnextBtn.pack(side = LEFT, padx = 5, pady = 4)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.labelLabel = Label(self.ctrPanel, text = "Label")
        self.labelLabel.pack(side = LEFT, padx = 5)
        self.labelText = Entry(self.ctrPanel, width = 10)
        self.labelText.pack(side = LEFT)
        self.labelBtn = Button(self.ctrPanel, text = 'Set', command = self.label)
        self.labelBtn.pack(side = LEFT)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)
        
        # set up output dir
        self.outDir = os.getcwd()+'/out'
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
 
        self.fileListName = self.outDir+'/'+'fileList.txt'
        self.fileListLabel = self.outDir+'/'+'labels.names'
        
        self.fileListNameList = []
        
        #init list of file already done
        if os.path.exists(self.fileListName):
            with open(self.fileListName, 'r') as f:
                for line in f:
                    line=line.split('\n')[0]
                    self.fileListNameList.append(line)
                    
                                

    def askDir(self,):
        dirname = tkFileDialog.askdirectory()
        
        self.entry.delete(0,len(self.entry.get()))
        self.entry.insert(0,dirname)

        self.imageDir = os.path.join(dirname)
        #self.parent.focus()
        print 'search images into '+self.imageDir
        # get image list
        self.imageList = sorted(glob.glob(os.path.join(self.imageDir+'/*.*')))
        
        if len(self.imageList) == 0:
            print 'No . images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.cur = 0
        self.total = len(self.imageList)
        
        self.loadImage()
        

    def loadImage(self):
        # load image
        self.imagepath = self.imageList[self.cur]
        print 'Loaded image =',self.imagepath
        
        #resize image if need to have better display        
        self.imgCv2 = cv2.imread(self.imagepath)

        self.mult = float(IMAGE_WIDTH/self.imgCv2.shape[1])

        self.imgCv2 = cv2.resize(self.imgCv2,(0,0),fx=self.mult,fy=self.mult)

        self.imgCv2 = cv2.cvtColor(self.imgCv2,cv2.COLOR_BGR2RGB)
        self.img = Image.fromarray(self.imgCv2)
        
        self.imageName = os.path.split(self.imagepath)[-1].split('.')[0]
        
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.labelfilename = os.path.join(self.outDir+'/'+self.imageName+'.txt')
        self.clearBBox()
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                className = ''
                for line in f:
                    print 'retrieve object ',line
                    lineSplit = line.split(' ')
                    className = lineSplit[0]
                    print 'Classname =',className
                    x = int(float(lineSplit[1])*self.imgCv2.shape[1])
                    y = int(float(lineSplit[2])*self.imgCv2.shape[0])
                    w = int(float(lineSplit[3])*self.imgCv2.shape[1])
                    h = int(float(lineSplit[4])*self.imgCv2.shape[0])
                    tmp = (x-w//2,y-h//2,x+w//2,y+h//2,x,y,w,h,className)
                    self.bboxList.append(tmp)
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d):%s' %(tmp[0], tmp[1], tmp[2], tmp[3], className))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
                    
                #save back the label
                self.labelImage = className   
                self.labelText.delete(0,len(self.labelText.get()))
                self.labelText.insert(0,className)
                
                
    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            for bbox in self.bboxList:
                #format used here is the one for darknet
                bboxConvert = convert(self.imgCv2.shape,(bbox[4],bbox[5],bbox[6],bbox[7]))
                #check if label already exist
                s = bbox[8] +' '+str(bboxConvert[0])+' '+str(bboxConvert[1])+' '+str(bboxConvert[2])+' '+str(bboxConvert[3])+'\n'
                print 'write into',self.labelfilename+' '+s
                f.write(s)
            f.close()
            

    def mouseClick(self, event):
        if self.labelImage !='':
            if self.STATE['click'] == 0:
                self.STATE['x'], self.STATE['y'] = event.x, event.y
            else:
                x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
                y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
                self.bboxList.append((x1, y1, x2, y2,x1+(x2-x1)//2,y1+(y2-y1)//2,(x2-x1),(y2-y1),self.labelImage))
                self.bboxIdList.append(self.bboxId)
                self.bboxId = None
                self.listbox.insert(END, '(%d, %d) -> (%d, %d):%s' %(x1, y1, x2, y2,self.labelImage))
                self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
                self.saveImage()
            self.STATE['click'] = 1 - self.STATE['click']
        else:
            print 'please enter a label before to draw the bounding box'

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0
                self.saveImage()

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        print 'selection =',sel[0]
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)
        self.saveImage()

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        
    def clearBBoxAndSave(self):
        self.clearBBox()
        self.saveImage()


    def prevImage(self, event = None):
        self.cur -= 1
        if self.cur >= 0:
            self.loadImage()
        else:
            self.cur = 0

    def nextImage(self, event = None):
        #write image file list 
        with open(self.fileListName, 'a+') as f:
            if self.imagepath in self.fileListNameList:
                print 'file already listed in file list'
            else:
                f.write(self.imagepath+'\n')
                self.fileListNameList.append(self.imagepath)
            f.close()
            
        self.cur += 1
        if self.cur < self.total:
            self.loadImage()
        else:
            self.cur = self.total-1
            

    #go to next image not already done
    def nnextImage(self, event = None):
        #reset index
        self.cur=0
        for image in self.imageList:
            if image in self.fileListNameList:
                self.cur += 1
                if self.cur >= self.total:
                    self.cur = self.total-1
            else:
                break
        self.loadImage()

            
        
    def label(self):
        self.labelImage = self.labelText.get()



if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
