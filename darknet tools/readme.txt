


1) for video: use fileReduction.py to reduce image numbers from video image directory (it will create ImagesResultDir with image reduced as expected 

2)in ImagesResultDir or directory of your dataset Convert all file into JPEG (ex for bmp conversion):
mogrify -format jpg *.bmp

3)Create darknet/data/DATASET_NAME/images directory where you place all the jpg image you want to use for the train (basically all the image made above)


4)from darknet/data/DATASET_NAME use labeltool.py on the image dataset directory to create your database with label. It will create out/ dir with annotation files 

5)from darknet/data/DATASET_NAME use convert2darknet.py on the out directory where is located the fileList.txt (it must be at the same level than all others annoted_file.txt). it  should create all file for darknet in the darknet/data/DATASET_NAME directory


6) change network.cfg file (you can take the one from yolo-voc) the last filter etage and below accordingly : 
			o first lines uncomment/comment lines to train and not to test
			o filters=30 for 1 class , 35 for 2 class ...
            o classes 1 or 2 or ...
			
7) go back to darknet dir and launch darknet as followed :
cd /home/darknet
./darknet detector train data/DATASET_NAME/dataFile.data data/DATASET_NAME/yolo-voc.cfg darknet19_448.conv.23

wait for at least 1000 

