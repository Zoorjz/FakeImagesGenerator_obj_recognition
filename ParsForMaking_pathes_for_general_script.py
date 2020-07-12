import shutil
import time
import os

names = os.listdir(os.getcwd())
file = open("Pathes.txt", "w")
string = ""
for name in names:
    fullname = os.path.join(os.getcwd(),name)
    if( name != 'Folders') & (name != 'ParsForMaking_pathes_for_general_script.py') & (not os.path.isfile(name)):  #ЭТо просьба не считать папку в 
       
        
        print(os.getcwd()+"/" + name)
        string += "\"" + "img/sourse_png/" + name + "\",\n"
        string = string.replace("\\", "/")
       
file.write(string) 
file.close() 



