#code for calibration of the absolute encoder positions with respect to the incremental encoder positions (or lasermeasurement)
#movement to maximum position, and back to parking position afterwards
#absolute and incremental encoder positions of specified unit at specified port are saved in txt file named "abs_inc_pos_--number of port--_number of unit_.txt"
#time step delta_t and maximum position need to be specified; delta_t of a few sec seems reasonable (1 sec communication timeout with each get position and get status command needed in any case); maximum position (in mm) depends on setup 


import platform
import serial
import time


baudrate = 9600


#ALWAYS ADJUST FILENAMES, TIME INTERVAL, POSITIONS, PORT, UNIT!!!

delta_t = 4  # >= 0 sec
max_pos = 9500 #9500, 8690, 9500
min_pos = 0

port = 2 #1 or 2
unit = 3 #1, 2, or 3

if platform.system() == "Windows":
    global_port_spec = 'COM' 
if platform.system() == "Linux":
    global_port_spec = '/dev/ttyMXUSB'    
    port -= 1
    
port_spec = global_port_spec
port_spec += str(port)
unit -= 1
   

file_down = open('abs_inc_pos_GS_2020_07_21_S3_corr_down.txt', 'w') #adjust filename
file_up = open('abs_inc_pos_GS_2020_07_21_S3_corr_up.txt', 'w') #adjust filename

#checksum used to ensure correct communication
def check_sum (array):
   csum = (sum(array) & 255) ^ 255
   return csum


def goto_position(unit, pos):
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
    return tx_array


def get_position():
    cmd_byte = 85
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    return tx_array


def get_status():
    cmd_byte = 51
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    return tx_array


#transmit desired maximum position
ser = serial.Serial(port_spec, baudrate, timeout = 0.1)
ser.write(bytearray(goto_position(unit, max_pos)))
rx_array = ser.read(6)
rx_array = list(rx_array)
ser.close()

print("Moving down.")

#repeatedly check position until motor has stopped        
max_time = time.time() + 60*25 #maximal waiting time 25 mins
while True:
        
    if time.time() > max_time:
        break
    
    ser = serial.Serial(port_spec, baudrate, timeout = 0.1)
    ser.write(bytearray(get_position()))
    rx_array = ser.read(20)
    rx_array = list(rx_array)
    ser.close()
    
    try:
        abs_pos_lsb = rx_array[1 + 4 * unit]
        abs_pos_msb = rx_array[2 + 4 * unit]
        inc_pos_lsb = rx_array[3 + 4 * unit]
        inc_pos_msb = rx_array[4 + 4 * unit]
        rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
        rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
    except (IndexError):
        continue
    
    if not -20 <= rx_pos_abs <= 10500:
            rx_pos_abs = -99
    if not -20 <= rx_pos_inc <= 10500:
            rx_pos_inc = -99
    
    print(rx_pos_abs,",",rx_pos_inc)
    file_down.write(str(rx_pos_abs) + ' , ' + str(rx_pos_inc) + '\n')
    
    ser = serial.Serial(port_spec, baudrate, timeout = 0.1)
    ser.write(bytearray(get_status()))
    rx_array = ser.read(15)
    rx_array = list(rx_array)
    ser.close()

    try:
        rx_motor = rx_array[8 + unit] & 3
    except (IndexError):
        continue
    
    if rx_motor == 0:
        break
    
    time.sleep(delta_t)

file_down.close()
    

#transmit minimum position
ser = serial.Serial(port_spec, baudrate, timeout = 0.1)
ser.write(bytearray(goto_position(unit, min_pos)))
rx_array = ser.read(6)
rx_array = list(rx_array)
ser.close()


print("Moving up.")

#repeatedly check position until motor has stopped        
max_time = time.time() + 60*25 #maximal waiting time 25 mins
while True:
       
    if time.time() > max_time:
        break
    
    ser = serial.Serial(port_spec, baudrate, timeout = 0.1)
    ser.write(bytearray(get_position()))
    rx_array = ser.read(20)
    rx_array = list(rx_array)
    ser.close()
    
    try:
        abs_pos_lsb = rx_array[1 + 4 * unit]
        abs_pos_msb = rx_array[2 + 4 * unit]
        inc_pos_lsb = rx_array[3 + 4 * unit]
        inc_pos_msb = rx_array[4 + 4 * unit]
        rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
        rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
    except (IndexError):
        continue
    
    if not -20 <= rx_pos_abs <= 10500:
            rx_pos_abs = -99
    if not -20 <= rx_pos_inc <= 10500:
            rx_pos_inc = -99
    
    print(rx_pos_abs,",",rx_pos_inc)
    file_up.write(str(rx_pos_abs) + ' , ' + str(rx_pos_inc) + '\n')
    
    ser = serial.Serial(port_spec, baudrate, timeout = 0.1)
    ser.write(bytearray(get_status()))
    rx_array = ser.read(15)
    rx_array = list(rx_array)
    ser.close()
    
    try:
        rx_motor = rx_array[8 + unit] & 3
    except (IndexError):
        continue
    
    if rx_motor == 0:
        break
    
    time.sleep(delta_t)
  
file_up.close()


print("Program finished.")
