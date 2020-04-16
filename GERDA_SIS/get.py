#get status + get position script
#prints and saves both positions and status parameters of all units (1, 2, 3) 
#the setup of the units needs to be as follows: 1, 2, 3 at control box ports 1, 2, 3; usb-to-serial converter port 1) 
#in case of success, the script exits on 0, otherwise on 1




import platform
import serial
import time
import sys
from datetime import datetime


baudrate = 9600

#bandlength
length = 8690


#prepare log-file
time_start = datetime.now().strftime("%H-%M-%S")
file_name = datetime.now().strftime("%Y-%m-%d-%H") #-%M-%S")
file = open('log-get_' + file_name + '.txt', 'w')
file.write('Status and position check at: ' + time_start + '\n')


#global port specification
if platform.system() == "Windows":
    global_port_spec = 'COM'
    plat_sys = 1
if platform.system() == "Linux":
    global_port_spec = '/dev/ttyMXUSB' 
    plat_sys = 0    
port_spec = global_port_spec
port = 0
port += plat_sys
port_spec += str(port)




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
                sys.exit(1)
             
            else:
                return rx_array
            
        time.sleep(0.1)
        



#internal commands needed for status/position check:
#get_status(): get current status of all nits, save and status of all units to file/to terminal
#get_position(): get current positions (in mm) of specified units, save and print positions of all units to file/to terminal


def get_status():      
    err = 0
    cmd_byte = 51
    rx_length = 15
    
    rx_init = []
    rx_motor = [] 
    rx_bits = []
    rx_bytes = []
    
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
        rx_init.extend((-999, -999, -999))
        rx_motor.extend((-999, -999, -999)) 
        rx_bits.extend((-999, -999, -999))
        rx_bytes.extend((-999, -999, -999))
    
    #data processing
    else: 
        rx_bits.append(['{0:08b}'.format(rx_array[n]) for n in range(len(rx_array))])     
        rx_bytes.append(rx_array)   
    
        for unit_num in range(3):
            #initialisation status
            rx_init.append(rx_array[8 + unit_num] >> 2 & 1)        
            #state of motor movement
            rx_motor.append(rx_array[8 + unit_num] & 3)  
    
    print("Movement (0: idle/break, 1: down, 2: up):",str(rx_motor))
    print("Initialisitaion status (0: not init., 1: init.):",str(rx_init))
    current_time = datetime.now().strftime("%H-%M-%S") 
    file.write(current_time + ': Status check:\n')
    file.write('Received bytes: ' + str(rx_bytes) + '\n')
    file.write('Received bits: ' + str(rx_bits) + '\n')
    file.write('Movement (0: idle/break, 1: down, 2: up): ' + str(rx_motor) + '\n')
    file.write('Initialisitaion status (0: not init., 1: init.): ' + str(rx_init) + '\n')   

    status = [rx_init, rx_motor]
    
    #error handling       
    if err > 0:
        print("Communication error occured during status check!")
        file.write(current_time + ': Communication error occured during status check!\n')
        file.close()
        sys.exit(1)
        
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
        inc_pos.extend((-999, -999, -999))
        abs_pos.extend((-999, -999, -999))
        discr.extend((-999, -999, -999)) 
        
    #data processing
    else:
        for unit_num in range(3):
            inc_pos.append(256 * rx_array[4 + 4 * unit_num] + rx_array[3 + 4 * unit_num])
            abs_pos.append(256 * rx_array[2 + 4 * unit_num] + rx_array[1 + 4 * unit_num])
            discr.append(inc_pos[unit_num] - abs_pos[unit_num])
    
    for unit_num in range(3):
        if not -10 <= inc_pos[unit_num] <= length:
            inc_pos[unit_num] = -9999
        if not -10 <= abs_pos[unit_num] <= length:
            abs_pos[unit_num] = -9999
        if not -100 <= discr[unit_num] <= 100:
            discr[unit_num] = -9999
    
        #positions to be saved
        if inc_pos[unit_num] != -9999:
            pos.append(inc_pos[unit_num])
        else:
            pos.append(abs_pos[unit_num])
            
    print("Current positions:",str(pos))
    file.write('Absolute encoder: ' + str(abs_pos) + '\n') 
    file.write('Discrepancies (incremental - absolute): ' + str(discr) + '\n')
    pos_file = open('current_positions.txt', 'w')
    pos_file.write('Positions:\n' + str(pos) + '\nIncremental encoder:\n' + str(inc_pos) + '\nAbsolute encoder:\n' + str(abs_pos) + '\nDiscrepancies (incremental - absolute):\n' + str(discr))
    pos_file.close()
    
    current_time = datetime.now().strftime("%H-%M-%S")        
    file.write(current_time + ': Current positions: \n')
    file.write('Incremental encoder: ' + str(inc_pos) + '\n')
    file.write('Absolute encoder: ' + str(abs_pos) + '\n') 
    file.write('Discrepancies (incremental - absolute): ' + str(discr) + '\n')
    
    #error handling
    current_time = datetime.now().strftime("%H-%M-%S")        
    if err > 0:
        print("Communication error occured during position check!")
        file.write(current_time + ': Communication error occured during position check!\n')
        file.close()
        sys.exit(1)
        
    return pos     


    
   
#main program
    
#check current status  
get_status()  
#check current positions  
get_position()

#finish log-file
time_end = datetime.now().strftime("%H-%M-%S")
file.write('\nStatus and position check finished at: ' + time_end + '\n')
file.close()
exit(0)        