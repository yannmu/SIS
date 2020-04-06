#iteratively call init, pos scripts
#pseudo_calib for unit 3 only

import time
import platform
import subprocess
from datetime import datetime

iter_file_name = datetime.now().strftime("%Y-%m-%d")

iterations = 10
iterator = 1

while iterator <= iterations:
    print(iterator)
    
    if platform.system() == "Windows":
        iter_file = open('iterations_' + iter_file_name + '_windows.txt', 'w')
        iter_file.write(str(iterator))
        iter_file.close()
        
        #init.py 3
        runfile('C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND/init.py', args='4', wdir='C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND')
        time.sleep(1)
        #pos.py x x 50 x   
        runfile('C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND/pos.py', args='x x 50 x', wdir='C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND')
        time.sleep(1)     
        #pos.py x x 100 x    
        runfile('C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND/pos.py', args='x x 100 x', wdir='C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND')
        time.sleep(2) 
        #pos.py x x 120 x    
        runfile('C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND/pos.py', args='x x 120 x', wdir='C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND')
        time.sleep(2) 
        #pos.py x x 140 x     
        runfile('C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND/pos.py', args='x x 140 x', wdir='C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND')
        time.sleep(2)
        #pos.py x x 50 x   
        runfile('C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND/pos.py', args='x x 50 x', wdir='C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND')
        time.sleep(1)   
        #init.py 3
        runfile('C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND/init.py', args='4', wdir='C:/Users/ym-st/OneDrive/Documents/SIS/SIS_code/calib_commands_LEGEND')
        time.sleep(1)
        
    if platform.system() == "Linux":
        iter_file = open('iterations_' + iter_file_name + '_linux.txt', 'w')
        iter_file.write(str(iterator))
        iter_file.close()
        
        subprocess.call('python3 init.py 1', shell=True)
        time.sleep(1)
        subprocess.call('python3 init.py 3', shell=True)
        time.sleep(1)
        subprocess.call('python3 pos.py 50 x 50 x', shell=True)
        time.sleep(1)
        subprocess.call('python3 pos.py 100 x x x', shell=True)
        time.sleep(2)
        subprocess.call('python3 pos.py x x 120 x', shell=True)
        time.sleep(2)
        #subprocess.call('python3 pos.py 140', shell=True)
        #time.sleep(2)
        #subprocess.call('python3 pos.py 50', shell=True)
        #time.sleep(1)
        subprocess.call('python3 pos.py 0 x 0 x', shell=True)
        
    iterator += 1
