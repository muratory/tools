import os
from shutil import copyfile,rmtree
import re
import sys
import tkFileDialog
import random
from pycuda.driver import Out


classes = ['dog', 'stop']

#ask the directory where is located the annotated files (out directory created by labeltool.py)
dirname = tkFileDialog.askdirectory()
#get file list from it


#create lables directory and basedir  where we will create all file for darknet framework
baseDir=os.getcwd()
labelsDir = baseDir + '/labels'
ImagesDir = baseDir + '/Images'
if os.path.exists(labelsDir):
    #raw_input("labelsDir will be removed and created with new files. Press Enter to continue...")
    rmtree(labelsDir,ignore_errors=True)
os.mkdir(labelsDir)

#create label and images directory
for classLabel in classes:
    dirLabel = labelsDir+'/'+classLabel
    dirImages = ImagesDir+'/'+classLabel 
    #create from scratch label directory 
    if not os.path.exists(dirLabel):
        os.mkdir(dirLabel)
    
    if not os.path.exists(dirImages):
        os.mkdir(dirImages)



imageList=[]

with open(dirname+'/fileList.txt', 'r') as f:
    for imageName in f:
        #create imageList
        imageList.append(imageName)
        #print 'file image ',imageName
        #for each image an annotated file as to be created even if empty
        #get image name without all path
        imageName = os.path.basename(imageName)
        #replace extension image by .txt 
        fileStr = os.path.splitext(imageName)[0]+'.txt'
        fileName = fileStr
        
        #set file to read
        fileNameToRead =  dirname+'/'+fileStr

        #init dictionnary of object
        dictObject={}
        for classLabel in classes:
            dictObject[classLabel] = []
            
        #read file and append in the directory the file if need 
        with open(fileNameToRead,'r') as fileToRead:
            #go through all the line in file
            for line in fileToRead:
                lineSplit = line.split(' ')
                print 'line in file',lineSplit
                #check if label found in file is one of the label we want 
                if lineSplit[0] in classes:
                    #add in object list the index + coordinates (replacing label with index in classes because darknet need a number here
                    #so that we have something like -> 0 x y w h
                    print 'found object '+str(classes.index(lineSplit[0]))+' '+lineSplit[1]+' '+lineSplit[2]+' '+lineSplit[3]+' '+lineSplit[4]
                    dictObject[lineSplit[0]].append((str(classes.index(lineSplit[0]))+' '+lineSplit[1]+' '+lineSplit[2]+' '+lineSplit[3]+' '+lineSplit[4]))
                    #create the dir and file if not exist 
            
            fileToRead.close()
            
            #now recreate directory and file to write 
            for key in dictObject:
                fileNameToWrite = labelsDir+'/'+key+'/'+fileName
                print 'write file into ',fileNameToWrite
                if len(dictObject[key])>0:
                    with open(fileNameToWrite,'w') as fileToWrite:
                        fileToWrite.write("".join(dictObject[key]))
                        #copy image into this directory as wel
                        copyfile(imageList[len(imageList)-1].strip(), ImagesDir+'/'+key+'/'+imageName)
                    fileToWrite.close()
            fileToRead.close()

    f.close()        
                      
#shuffle the list in case the file comes from a video 
random.shuffle(imageList)

#create Train file list used for train and test
#splitTest is the pourcentage of file we keep for Test 
splitTest = 25
print 'Total image processed =',len(imageList)
print 'Split is done at ',(len(imageList) - int(splitTest*len(imageList)/100))
trainList = imageList[0:(len(imageList) - int(splitTest*len(imageList)/100))]
testList =  imageList[(len(imageList) - int(splitTest*len(imageList)/100)): len(imageList)]

#create file for both train and test:
#create fileName where to put all labels used (see aboves the classes to use
fileNameTrain = baseDir+'/trainList.txt'
with open(fileNameTrain, 'w') as f:
    f.write("".join(trainList))
    f.close()

fileNameTest = baseDir+'/testList.txt'
with open(fileNameTest, 'w') as f:
    f.write("".join(testList))
    f.close()
    
#create file  where to put all labels used (see aboves the classes to use
fileNameLabel = baseDir+'/labels.names'
with open(fileNameLabel, 'w') as f:
    f.write("\n".join(classes))

#create data file
#finally create file  where to put all labels used (see aboves the classes to use
fileNameData = baseDir+'/dataFile.data'
with open(fileNameData, 'w') as f:
    f.write('classes=%d\n'%(len(classes)))
    f.write('train=%s\n'%(fileNameTrain))
    f.write('valid=%s\n'%(fileNameTest))
    f.write('names=%s\n'%(fileNameLabel))
    f.write('backup = backup\n')
    f.close()


