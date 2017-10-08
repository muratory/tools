import os
import shutil
import re
import sys
import tkFileDialog

# this parameter define the number of file that will be kept
# if equal 10 -> 1 over 10 file will be kept
#if equal 5 -> 1 over 5 file will be kept
MODULO_FILE = 20

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


class ProgressBar:
    '''
    Progress bar
    '''
    def __init__ (self, valmax, maxbar, title):
        if valmax == 0:  valmax = 1
        if maxbar > 200: maxbar = 200
        self.valmax = valmax
        self.maxbar = maxbar
        self.title  = title
    
    def update(self, val):

        # process
        perc  = round((float(val) / float(self.valmax)) * 100)
        scale = 100.0 / float(self.maxbar)
        bar   = int(perc / scale)
  
        # render 
        out = '\r %5s [%s%s] %3d %%' % (self.title, '=' * bar, ' ' * (self.maxbar - bar), perc)
        sys.stdout.write(out)
        sys.stdout.flush()
        



dirname = tkFileDialog.askdirectory()

mypath=os.getcwd()


# Run the above function and store its results in a variable.   
full_file_paths = get_filepaths(dirname)

#create directory
dir = mypath + '/ImageResultDir'

if os.path.exists(dir):
    raw_input("resultDIR will be removed and created with new files. Press Enter to continue...")
    shutil.rmtree(dir,ignore_errors=True)

os.mkdir(dir)

print("Processing and copying file\n")

Bar = ProgressBar(len(full_file_paths), 60, 'Progress')

i=0
for file in full_file_paths:
    i=i+1
    f=os.path.basename(file)
    Bar.update(i)
    
    if ((i%MODULO_FILE) == 0 ):
        shutil.copy2(file,dir)
    else:
        continue






