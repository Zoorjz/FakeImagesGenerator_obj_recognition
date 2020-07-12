import shutil
import time
import os

names = os.listdir(os.getcwd())
file = open("labels.txt", "w")
string = ""
for name in names:
    fullname = os.path.join(os.getcwd(),name)
    if( name != 'Folders') & (name != 'ParsForMaking_labels_txt.py') & (not os.path.isfile(name)):  
       
        
        #print(os.path.isfile(name))
        string += name + "\n"
       
file.write(string) 
file.close() 



