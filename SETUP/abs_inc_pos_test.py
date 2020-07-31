#code for iterative checks of the accuraccy of the absolute encoder positions with respect to the incremental encoder positions with/without initialisation in between
#movement to maximum position, and to minimum position afterwards
#absolute and incremental encoder positions of specified unit at specified port are saved in txt file
#time step delta_t and minimum/maximum position need to be specified; delta_t of few sec seems reasonable (0.1 sec communication timeout with each get position and get status command needed in any case); maximum position (in mm) depends on setup 


import platform
import serial
import time


baudrate = 9600

#ALWAYS ADJUST FILENAME, TIME INTERVAL, POSITIONS, ITERATIONS, INITIALISATION, PORT, UNIT!!!

delta_t = 1  #2 >= 0 sec
max_pos = 6200
min_pos = 0

positions = [1000, 2000, 3000, 4000, 5000, 6000, 6100, 6000, 5000, 4000, 3000, 2000, 1900, 2000, 3000, 4000, 5000, 6000, 6100, 6000, 5000, 4000, 3900, 4000, 5000, 6000, 6100, 6000, 5000, 4000, 3000, 2000, 1900, 2000, 3000, 4000, 5000, 6000, 6100, 6000, 5000, 4000, 3000, 2000, 1000, 0] #(for pos. repetition test, 32.7 m, maybe 15 iterations) #[max_pos, min_pos] (12 m, maybe 20 iterations for each setup (20 with init, 20 without, each with calibration of abs enc and without)) ; 

iterations = 15 #20
init_yes_no = 1 #set to 0 or 1 for test of stability of abs. pos. over time, set to 1 for pos. repetition test

port = 1 #1 or 2
unit = 1 #1, 2, or 3

#internal port/unit specification
port -= 1
unit -= 1 

#global port specification
if platform.system() == "Windows":
    global_port_spec = 'COM'
    plat_sys = 1
if platform.system() == "Linux":
    global_port_spec = '/dev/ttyMXUSB' 
    plat_sys = 0
port_spec = global_port_spec
port += plat_sys
port_spec += str(port)
    

file = open('pos_repetition_UZH_2020_05_09.txt', 'w') #adjust filename


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
            ser.close()
        except(IndexError):
            ser.close()
            continue
        
        if (rx_length == len(rx_array) and rx_array[0] == tx_array[0]): 
            return rx_array

        time.sleep(0.1)


def init(unit):
    rx_length = 4
    cmd_byte = 170
    tx_array=[cmd_byte,
             unit,
             cmd_byte ^ 255,
             unit ^ 255,
             cmd_byte ^ 255,
             unit ^ 255]

    tx_array.append(check_sum(tx_array))
    rx_array = tx_rx(tx_array, rx_length)
    return tx_array


def goto_position(unit, pos):
    rx_length = 6
    cmd_byte = 15
    pos_lsb = pos & 255
    pos_msb = pos // 256
    tx_array = [cmd_byte,
                unit,
                pos_lsb,
                pos_msb,
                cmd_byte ^ 255,
                unit ^ 255]
    
    tx_array.append(check_sum(tx_array))
    rx_array = tx_rx(tx_array, rx_length)
    return rx_array


def get_position():
    rx_length = 20
    cmd_byte = 85
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    rx_array = tx_rx(tx_array, rx_length)
    return rx_array


def get_status():
    rx_length = 15
    cmd_byte = 51
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    rx_array = tx_rx(tx_array, rx_length)
    return rx_array


iterator = 1
while iterator <= iterations:
    
    for pos in positions:
        #transmit desired position
        if (pos == 0 and init_yes_no == 1):
            init(unit)
        else:
            goto_position(unit, pos)

        #repeatedly check position until motor has stopped        
        max_time = time.time() + 60*20 #maximal waiting time 20 mins
        while True:
        
            if time.time() > max_time:
                break
    
            rx_array = get_position()
    
            try:
                abs_pos_lsb = rx_array[1 + 4 * unit]
                abs_pos_msb = rx_array[2 + 4 * unit]
                inc_pos_lsb = rx_array[3 + 4 * unit]
                inc_pos_msb = rx_array[4 + 4 * unit]
                rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
                rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
            except(IndexError):
                continue
    
            if not -25 <= rx_pos_abs <= 10500:
                rx_pos_abs = -9999
            if not -25 <= rx_pos_inc <= 10500:
                rx_pos_inc = -9999
            
            #if (rx_pos_abs != -9999 and rx_pos_inc != -9999): 
                #print(rx_pos_abs,",",rx_pos_inc) #comment out for pos. repetition test
                #file.write(str(rx_pos_abs) + ' , ' + str(rx_pos_inc) + '\n') #comment out for pos. repetition test
    
            rx_array = get_status()

            try:
                rx_motor = rx_array[8 + unit] & 3
            except(IndexError):
                continue
    
            if rx_motor == 0: 
                print(rx_pos_abs,",",rx_pos_inc)
                if rx_pos_inc not in [1900, 3900, 6100]: #uncomment for pos. repeptition test
                    file.write(str(rx_pos_abs) + ' , ' + str(rx_pos_inc) + '\n')              
                break
    
            time.sleep(delta_t)

    iterator += 1


file.close()
print("Program finished.")
