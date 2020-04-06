#positions command
#only works if units are in remote control mode
#units need to be initialised, run init.py beforehand, if this is not the case
#set fixed positions for all units, or for each unit individually
#specifying just a single position will lead to a movement of all 3 units (e.g. pos 5000)
#send position <value> to a certain unit (1, 2, 3) when different positions are specified (e.g. pos.py 5000 5500 6000)
#a unit will not be moved if the position is set to x (e.g. pos.py 2000 x x means that only unit 1 will be moved to 2000, whereas units 2, 3 remain at their current position, only unit 2 would be x 2000 x, and only unit 3 would be x x 2000)
#the expected time to finish is printed in the beginning
#an overview of the current positions is printed every 10 sec
#the speed of the movement is approx. 10 mm/s
#the setup of the units needs to be as follows: 1, 2, 3 at control box ports 1, 2, 3; usb-to-serial converter port 1)
#in case of success, the script exits on 0, otherwise on 1




import platform
import serial
import time
import sys
from datetime import datetime


baudrate = 9600

#time step for position update during movement 10 sec
delta_t = 10
#average speed 10 mm / sec
v = 10
#bandlength
length = 8690
#precision
prec = 10


#read in positions
end_pos = []

for unit_num in range(3):
    if len(sys.argv) - 1 == 3: 
        if str(sys.argv[unit_num + 1]) == "x":
            ext_pos = -1
        else:
            try:
                ext_pos = int(sys.argv[unit_num + 1])
            except(ValueError):
                print("Positions must be integer values between 0 and the bandlength (",str(length),"mm).")
                sys.exit(1)
                
    elif len(sys.argv) - 1 == 1:
        try:
            ext_pos = int(sys.argv[1])
        except(ValueError):
            print("Positions must be integer values between 0 and the bandlength (",str(length),"mm).")
            sys.exit(1)
            
    else:
        print("Number of positions must be either 1 (for all units) or 3 (for all units individually). Use x to keep a unit at the current position.")
        sys.exit(1)
        
    if  -1 <= ext_pos <= length:
        end_pos.append(ext_pos)   
    else:
        print("Positions must be between 0 and the bandlength (",str(length),"mm).")
        sys.exit(1)


#prepare log-file     
time_start = datetime.now().strftime("%H-%M-%S")
file_name = datetime.now().strftime("%Y-%m-%d") #-%H-%M-%S")
file = open('log-pos_' + file_name + '.txt', 'w')
file.write('Sending positions started at: ' + time_start + '\n')
file.write('Script called with position specification (-1 <--> x (no movement)): ' + str(end_pos) + '\n\n')


#global port specification
if platform.system() == "Windows":
    global_port_spec = 'COM'
    plat_sys = 1
if platform.system() == "Linux":
    global_port_spec = '/dev/ttyMXUSB' 
    plat_sys = 0
port_spec = global_port_spec
port = 1 
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
                file.write('Received bits: ' + str(rx_bits) + '\n')
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
        
        
        
        
#internal commands needed for approaching positions:
#stop(): stop command is sent to all units; script is terminated, and exits on 1
#get_status(): get current status for all units (1, 2, 3), returns initialisation and motor status of all 3 units
#get_position(): get current positions (in mm) of units (1, 2, 3)
#goto_position(unit, pos): send position to unit


def stop():
    err = 0
    cmd_byte = 195
    rx_length = 4
    
    for unit_num in range(3):
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
        file.close()
        sys.exit(1)
    file.close()


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
    cmd_byte = 85
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
    
        #positions to be saved and returned
        if inc_pos[unit_num] != -9999:
            pos.append(inc_pos[unit_num])
        else:
            pos.append(abs_pos[unit_num])
            
    print("Current positions:",str(pos))
    pos_file = open('current_positions.txt', 'w')
    pos_file.write('Positions:\n' + str(pos) + '\nIncremental encoder:\n' + str(inc_pos) + '\nAbsolute encoder:\n' + str(abs_pos) + '\nDiscrepancies (incremental - absolute):\n' + str(discr))
    pos_file.close()
    
    current_time = datetime.now().strftime("%H-%M-%S")        
    file.write(current_time + ': Current positions: \n')
    file.write('Incremental encoder: ' + str(inc_pos) + '\n')
    file.write('Absolute encoder: ' + str(abs_pos) + '\n') 
    file.write('Discrepancies (incremental - absolute): ' + str(discr) + '\n')
    
    #error handling       
    if err > 0:
        print("Communication error occured during position check!")
        file.write(current_time + ': Communication error occured during position check!\n')
        stop()
    
    return pos
    

def goto_position(unit_num, pos):
    err = 0
    cmd_byte = 15
    rx_length = 6
    
    #prepare tx_array
    pos_lsb = pos & 255
    pos_msb = pos // 256
    tx_array = [cmd_byte,
                unit_num,
                pos_lsb,
                pos_msb,
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
        print("Communication error occured during transmission of desired position to units!")
        file.write(current_time + ': Communication error occured during transmission of desired position to units!\n')
        stop()           




#main program
    
#check current position, transmit desired positions, print expected time needed to finish   
pos = get_position()
diff = [0, 0, 0]

for unit_num in range(3):
    
    if end_pos[unit_num] != -1:   
        diff[unit_num] = abs(pos[unit_num] - end_pos[unit_num])
        goto_position(unit_num, end_pos[unit_num])
    else:
        end_pos[unit_num] = pos[unit_num]
        
print("Next stop positions:",str(end_pos))
file.write('Next stop positions: ' + str(end_pos) + '\n') 

t = int(max(diff) / v + 1)
    
current_time = datetime.now().strftime("%H-%M-%S")
print("Expected time needed to approach positions (in sec):",str(t))
file.write(current_time + ': Expected time needed to approach positions (in sec): ' + str(t) + '\n')
        
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
    motor = status[1]
    
    #exit loop when motor(s) has/have stopped
    if all(elem == 0 for elem in motor):
        time.sleep(1)
        break
        
#check that positions have been approached, and finish log-file        
dev = [pos[unit_num] - end_pos[unit_num] for unit_num in range(3)]

time_end = datetime.now().strftime("%H-%M-%S")

if all(abs(elem) <= prec for elem in dev):
    file.write('\nPositions approached at: ' + time_end + '\n')
    file.close()
    exit(0)  
    
else:
    print("Positions could not be approached successfully!")
    file.write(current_time + ': Positions could not be approached successfully!\n')
    file.close()
    sys.exit(1)
    
    
    
    
