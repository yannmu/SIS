#initialise command
#only works if units are in remote control mode 
#initialise all, or only specific units
#initialisation of all units as default (init.py)
#initialisation of only a certain unit (1, 2, 3) if and only if the corresponding single unit number is specified (e.g. init.py 1)  
#the expected time to finish is printed in the beginning
#an overview of the current positions is printed every 5 sec
#the speed of the movement is approx. 10 mm/s
#the setup of the units needs to be as follows: 1, 2, 3 at control box ports 1, 2, 3; usb-to-serial converter port 2) 
#in case of errors the script exits on 1




import platform
import serial
import time
import sys
import os
from datetime import datetime


port = 1
baudrate = 9600

#time step for position update during movement 5 sec
delta_t = 5
#average speed 10 mm / sec
v = 10
#bandlength
length = [9500, 8690, 9500]
#precision
prec = 10


#read in unit specification
try:
    unit = int(sys.argv[1])
    units = [unit]
except(IndexError):
    units = [1, 2, 3]
    unit = "(1, 2, 3)"
    
for unit_num in units:
   if not (1 <= unit_num <= 3): 
       print("Valid unit numbers are 1, 2, or 3. ")
       time.sleep(5)
       sys.exit(1)
       
       
#prepare log-file
time_start = datetime.now().strftime("%H-%M-%S")
date = datetime.now().strftime("%Y-%m-%d")
file_name = datetime.now().strftime("%H-%M-%S")

#global port specification
if platform.system() == "Windows":
    global_port_spec = 'COM'
    plat_sys = 1
    dir_name = 'C:/Users/ym-st/OneDrive/Desktop/GERDA_SIS/log/' + str(date)
    
if platform.system() == "Linux":
    global_port_spec = '/dev/ttyMXUSB' 
    plat_sys = 0    
    dir_name = 'log/' + str(date)
  
port_spec = global_port_spec
port += plat_sys
port_spec += str(port)

if not os.path.exists(dir_name):
    os.mkdir(dir_name)

file = open(dir_name +'/log-init_' + file_name + '.txt', 'w')
file.write('Initialisation started at: ' + time_start + '\n')
file.write('Script called with external unit specification ' + str(units) + '\n\n')



#checksum used to ensure correct communication
def check_sum (array): 
   csum = (sum(array) & 255) ^ 255
   return csum


#transmitting and receiving byte array
def tx_rx(tx_array, rx_length):
    communication_time = time.time() + 2 #maximal time span until communication is considered nonreliable 2 sec
    
    while True:
        if time.time() > communication_time:
            return 0
        
        #send tx_array
        ser = serial.Serial(port_spec, baudrate, timeout = 0.1)
        ser.write(bytearray(tx_array))
    
        #read in rx_array
        try:
            rx_array = ser.read(rx_length)
            rx_array = list(rx_array)
            acknow_byte = rx_array[2]
            ser.close()
        except (IndexError):
            ser.close()
            continue
        
        #check rx_array
        current_time = datetime.now().strftime("%H-%M-%S")
        bits=['{0:08b}'.format(rx_array[n]) for n in range(len(rx_array))] 
        
        if (rx_length == len(rx_array) and rx_array[0] == tx_array[0]):  
            
            if (rx_length == 4 and acknow_byte != 0):
                print("Make sure that remote control mode is turned on!")
                file.write(current_time + ': Make sure that remote control mode is turned on!\n')
                file.write('Received bytes: ' + str(rx_array) + '\n')
                file.write('Received bits: ' + str(bits) + '\n')
                file.close()
                time.sleep(5)
                sys.exit(1)
                
            elif (rx_length == 6 and acknow_byte != 0):
                if acknow_byte == 1:
                    print("Make sure that remote control mode is turned on!")
                    file.write(current_time + ': Make sure that remote control mode is turned on!\n')
                if acknow_byte == 4:
                    print("Position specifications invalid!")
                    file.write(current_time + ': Position specifications invalid!\n')
                if acknow_byte == 8:
                    print("A unit needs to be initialised before it can be moved!")
                    file.write(current_time + ': A unit needs to be initialised before it can be moved!\n')
                    
                file.write('Received bytes: ' + str(rx_array) + '\n')
                file.write('Received bits: ' + str(bits) + '\n')
                file.close()
                time.sleep(5)
                sys.exit(1)
             
            else:
                return rx_array
            
        time.sleep(0.1)
        



#internal commands needed for initialisation:
#stop(): stop command is sent to specified units; script is terminated, and exits on 1
#get_status(): get current status of specified units, save status of all units to file
#get_position(): get current positions (in mm) of specified units, save and print positions of all units to file/to terminal
#init(): initialise specified units
   

def stop():
    err = 0
    cmd_byte = 195
    rx_length = 4
    
    for unit_num in units:
        unit_num = unit_num - 1
        
        #prepare tx_array
        tx_array = [cmd_byte,
                    unit_num,
                    cmd_byte ^ 255,
                    unit_num ^ 255,
                    cmd_byte ^ 255,
                    unit_num ^ 255]
        tx_array.append(check_sum(tx_array))
        
        #send and receive
        rx_array = tx_rx(tx_array, rx_length)
        if rx_array == 0:
            err += 1    

    #error handling
    current_time = datetime.now().strftime("%H-%M-%S")        
    if err > 0:
        print("Communication error occured when sending stop command as backstop!")
        file.write(current_time + ': Communication error occured when sending stop command as backstop!\n')   
    else:
        print("Stop command sent to specified units!")
        file.write(current_time + ': Stop command sent to specified units!\n')
        
    file.close()
    time.sleep(5)
    sys.exit(1)


def get_status():      
    err = 0
    cmd_byte = 51
    rx_length = 15
    
    rx_init = []
    rx_motor = [] 
    rx_bits = []
    rx_bytes = []
    rx_status = []
    rx_error = []
    
    #prepare tx_array
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]    
    tx_array.append(check_sum(tx_array))
        
    #send and receive
    rx_array = tx_rx(tx_array, rx_length)
    if rx_array == 0:
        err += 1
        rx_init.extend((-1111, -1111, -1111))
        rx_motor.extend((-1111, -1111, -1111)) 
        rx_bits.extend((-1111, -1111, -1111))
        rx_bytes.extend((-1111, -1111, -1111))
        rx_status.extend((-1111, -1111, -1111))
        rx_error.extend((-1111, -1111, -1111))
    
    #data processing
    else: 
        rx_bits.append(['{0:08b}'.format(rx_array[n]) for n in range(len(rx_array))])     
        rx_bytes.append(rx_array)   
    
        for unit_num in range(3):
            #initialisation status
            rx_init.append(rx_array[8 + unit_num] >> 2 & 1)        
            #state of motor movement
            rx_motor.append(rx_array[8 + unit_num] & 3) 
            #status flags
            rx_status.append(rx_array[8 + unit_num])
            #error flags
            rx_error.append(rx_array[11 + unit_num])
    
    print("----------Movement (0: idle/break, 1: down, 2: up):",str(rx_motor))
    print("----------Initialisitaion status (0: not init., 1: init.):",str(rx_init))
    print("----------Status flags:",str(rx_status))
    print("----------Error flags:",str(rx_error))

    current_time = datetime.now().strftime("%H-%M-%S") 
    file.write(current_time + ': Status check:\n')
    file.write('Received bytes: ' + str(rx_bytes) + '\n')
    file.write('Received bits: ' + str(rx_bits) + '\n')
    file.write('Movement (0: idle/break, 1: down, 2: up): ' + str(rx_motor) + '\n')
    file.write('Initialisitaion status (0: not init., 1: init.): ' + str(rx_init) + '\n')
    file.write('Status flags: ' + str(rx_status) + '\n') 
    file.write('Error flags: ' + str(rx_error) + '\n')      
    
    #status to be returned
    if len(units) == 1:  
        status = [[rx_init[units[0] - 1]], [rx_motor[units[0] - 1]]]
    if len(units) == 2:
        status = [[rx_init[units[0] - 1], rx_init[units[1] - 1]], [rx_motor[units[0] - 1], rx_motor[units[1] - 1]]]
    if len(units) == 3:
        status = [rx_init, rx_motor]
        
    #error handling       
    if err > 0:
        print("Communication error occured during status check!")
        file.write(current_time + ': Communication error occured during status check!\n')
        stop()
        
    return status


def get_position():     
    err = 0
    cmd_byte = 85
    rx_length = 20
    
    inc_pos = []
    abs_pos = []
    discr = []
    pos = []
    
    #prepare tx_array
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    
    #send and receive
    rx_array = tx_rx(tx_array, rx_length)
    if rx_array == 0:
        err += 1
        inc_pos.extend((-1111, -1111, -1111))
        abs_pos.extend((-1111, -1111, -1111))
        discr.extend((-1111, -1111, -1111)) 
        pos.extend((-1111, -1111, -1111))
        
    #data processing
    else:
        for unit_num in range(3):
            inc_pos.append(256 * rx_array[4 + 4 * unit_num] + rx_array[3 + 4 * unit_num])
            abs_pos.append(256 * rx_array[2 + 4 * unit_num] + rx_array[1 + 4 * unit_num])
            discr.append(inc_pos[unit_num] - abs_pos[unit_num])
    
        for unit_num in range(3):
            if not -20 <= inc_pos[unit_num] <= length[unit_num] + 100:
                inc_pos[unit_num] = -9999
            if not -20 <= abs_pos[unit_num] <= length[unit_num] + 100:
                abs_pos[unit_num] = -9999
            if (not -999 < discr[unit_num] < 999) or inc_pos[unit_num] == -9999 or abs_pos[unit_num] == -9999:
                discr[unit_num] = -9999
    
            #positions to be saved
            if inc_pos[unit_num] != -9999:
                pos.append(inc_pos[unit_num])
            else:
                pos.append(abs_pos[unit_num])
    
    print("----------Incremental encoder:",str(inc_pos)) 
    print("----------Absolute encoder:",str(abs_pos)) 
    print("----------Discrepancies (incremental - absolute):",str(discr))        
    print("\nCURRENT POSITIONS:",str(pos),"\n")
    pos_file = open('current_positions.txt', 'w')
    pos_file.write('Positions:\n' + str(pos) + '\nIncremental encoder:\n' + str(inc_pos) + '\nAbsolute encoder:\n' + str(abs_pos) + '\nDiscrepancies (incremental - absolute):\n' + str(discr))
    pos_file.close()
    
    current_time = datetime.now().strftime("%H-%M-%S")        
    file.write(current_time + ': Current positions: \n')
    file.write('Incremental encoder: ' + str(inc_pos) + '\n')
    file.write('Absolute encoder: ' + str(abs_pos) + '\n') 
    file.write('Discrepancies (incremental - absolute): ' + str(discr) + '\n')
    
    #positions to be returned (all units or individual units)    
    if len(units) == 1:  
        pos = [pos[units[0] - 1]]
    if len(units) == 2:
        pos = [pos[units[0] - 1], pos[units[1] - 1]]
    
    #error handling
    current_time = datetime.now().strftime("%H-%M-%S")        
    if err > 0:
        print("Communication error occured during position check!")
        file.write(current_time + ': Communication error occured during position check!\n')
        stop()
        
    return pos
       

def init():
    err = 0      
    cmd_byte = 170
    rx_length = 4
    
    for unit_num in units:
        unit_num = unit_num - 1
 
        #prepare tx_array
        tx_array = [cmd_byte,
                    unit_num,
                    cmd_byte ^ 255,
                    unit_num ^ 255,
                    cmd_byte ^ 255,
                    unit_num ^ 255]
        tx_array.append(check_sum(tx_array)) 
    
        #send and receive
        rx_array = tx_rx(tx_array, rx_length)
        if rx_array == 0:
            err += 1
                
    current_time = datetime.now().strftime("%H-%M-%S")    
    #error handling
    if err > 0:
        print("Communication error occured when sending initialisation command!")
        file.write(current_time + ': Communication error occured when sending initialisation command!\n')
        stop()
    
    return 0
    
    
       

#main program
    
#check current position, send init command, print expected time needed to finish   
status = get_status()
pos = get_position()
init()
t = int(max(pos) / v + 1)
#2 seconds to hit end-switch and move back to parking position
t += 2

current_time = datetime.now().strftime("%H-%M-%S")
if t > 0:
    print("Expected time needed to initialise (in sec):",str(t),"\n")
    file.write(current_time + ': Expected time needed to initialise (in sec): ' + str(t) + '\n')
else:
    print("Expected time needed to initialise unknown (approx. 3 sec from parking position).\n")
    file.write(current_time + ': Expected time needed to initialise unknown (approx. 3 sec from parking position).\n')
     
#check positions and motor status during movement
max_time = time.time() + 60*20 #maximal waiting time 20 mins
while True:
            
    current_time = datetime.now().strftime("%H-%M-%S")
    if time.time() > max_time:
        print("Maximum waiting time has expired. Make sure that communication works properly.")
        file.write(current_time + ': Maximum waiting time has expired. Make sure that communication works properly.\n')
        stop()
    
    if 0 <= t <= delta_t:
        time.sleep(t)
    else:
        time.sleep(delta_t)   
    
    status = get_status()
    pos = get_position()
    init = status[0]
    motor = status[1]
    
    #exit loop when motor(s) has/have stopped
    if all(elem == 0 for elem in motor):
        time.sleep(1)
        break
     
#check initialisation status, ensure that parking position has been approached, and finish log-file
time_end = datetime.now().strftime("%H-%M-%S")

if (all(elem == 1 for elem in init) and all(abs(elem) <= prec for elem in pos)):
    file.write('\nInitialisation finished at: ' + time_end + '\n')
    file.close()
    print("Initialisation finished.")
    
else:
    file.write(current_time + ': Initialisation could not be finished successfully!\n')
    file.close()
    print("Initialisation could not be finished successfully!")
    sys.exit(1)     
    
#exit(0)
    
        

