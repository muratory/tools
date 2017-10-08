import os
import shutil
import re
import sys
import tkFileDialog
import random
from pycuda.driver import Out


classes = ['dog', 'stop']

#ask the directory where is located the annotated files (out directory created by labeltool.py)
dirname = tkFileDialog.askdirectory()
#get file list from it


#create out dir where we will create all file for darknet framework
mypath=os.getcwd()
outDirDarknet = mypath + '/outDarknet'
if os.path.exists(outDirDarknet):
    #raw_input("outDirDarknet will be removed and created with new files. Press Enter to continue...")
    shutil.rmtree(outDirDarknet,ignore_errors=True)
os.mkdir(outDirDarknet)

imageList=[]
with open(dirname+'/fileList.txt', 'r') as f:
    for imageName in f:
        #create imageList
        imageList.append(imageName)
        print 'file image ',imageName
        #for each image an annotated file as to be created even if empty
        #get image name without all path
        fileStr = os.path.basename(imageName)
        #replace extension image by .txt 
        fileStr = os.path.splitext(fileStr)[0]+'.txt'
        #create output file name
        fileStr = outDirDarknet+'/'+fileStr
        print 'create file ',fileStr  
        
        with open(fileStr,'w') as fileToWrite:
            #get filename to read
            fileStr=fileStr.replace(outDirDarknet,dirname)
            #create the list of object we want to train
            listObjectInFile = []
            #read file in dir
            with open(fileStr,'r') as fileToRead:
                #go through all the line in file
                for line in fileToRead:
                    lineSplit = line.split(' ')
                    print 'line in file',lineSplit
                    #check if label found in file is one of the label we want 
                    if lineSplit[0] in classes:
                        #add in object list the index + coordinates (replacing label with index in classes because darknet need a number here
                        #so that we have something like -> 0 x y w h
                        listObjectInFile.append(str(classes.index(lineSplit[0]))+' '+lineSplit[1]+' '+lineSplit[2]+' '+lineSplit[3]+' '+lineSplit[4])
                        print 'found object '+str(classes.index(lineSplit[0]))+' '+lineSplit[1]+' '+lineSplit[2]+' '+lineSplit[3]+' '+lineSplit[4]
    
                fileToRead.close()
                
            fileToWrite.write("".join(listObjectInFile))
            fileToWrite.close()
            
    f.close()        
                      
#shuffle the list in case the file comes from a video 
random.shuffle(imageList)

#create Train file list used for train and test
#splitTest is the pourcentage of file we keep for Test 
splitTest = 25
print 'Split is done at ',(len(imageList) - int(splitTest*len(imageList)/100))
trainList = imageList[0:(len(imageList) - int(splitTest*len(imageList)/100))]
testList =  imageList[(len(imageList) - int(splitTest*len(imageList)/100)): len(imageList)]

#create file for both train and test:
#create fileName where to put all labels used (see aboves the classes to use
fileNameTrain = outDirDarknet+'/trainList.txt'
with open(fileNameTrain, 'w') as f:
    f.write("".join(trainList))
    f.close()

fileNameTest = outDirDarknet+'/testList.txt'
with open(fileNameTest, 'w') as f:
    f.write("".join(testList))
    f.close()
    
#create file  where to put all labels used (see aboves the classes to use
fileNameLabel = outDirDarknet+'/labels.names'
with open(fileNameLabel, 'w') as f:
    f.write("\n".join(classes))


#create data file
#finally create file  where to put all labels used (see aboves the classes to use
fileNameData = outDirDarknet+'/dataFile.data'
with open(fileNameData, 'w') as f:
    f.write('classes=%d\n'%(len(classes)))
    f.write('train=%s\n'%(fileNameTrain))
    f.write('valid=%s\n'%(fileNameTest))
    f.write('names=%s\n'%(fileNameLabel))
    f.write('backup = backup\n')
    f.close()


