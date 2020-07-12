import shutil
import time
import os

names = os.listdir(os.getcwd())
file = open("Pathes.txt", "w")
string = ""
for name in names:
    fullname = os.path.join(os.getcwd(),name)
    if( name != 'Folders') & (name != 'ParsForMaking_pathes_for_general_script.py'):  #ЭТо просьба не считать папку в 
       
        
        print(os.getcwd()+"/" + name)
        string +="\"C:\\\\DeepLearning\\\\DataBase\\\\heartstone\\\\cards\\\\Final\\\\Folders\\\\"+ name + "\",\n"
       
file.write(string) 
file.close() 



