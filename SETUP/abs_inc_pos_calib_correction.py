from numpy import trapz
from scipy.interpolate import interp1d
from matplotlib.cbook import flatten
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import csv
#import pandas as pd
import time
from datetime import datetime
#import random


#ALWAYS ADJUST FILENAME OF CORRECTION TABLE, FILENAMES OF DATA, MULTI TURN VALUE, CYCLES, POLYNOM ORDER

max_len_possible = 10500.
turns_tot = 64
multi_turns = 54 #59, 54, 59 #this value depends on the initliatisation of the absolute encoder, which may differ between different units 
max_len = max_len_possible / turns_tot * multi_turns
delta_s = max_len / multi_turns
cycles = 1
pol_ord = 5

print('\n',delta_s,'\n')

corr_table = 0 #1 for yes
date = datetime.now().strftime("%Y-%m-%d")
corr_file_name = 'abs_inc_pos_GS_2_pol_5_corr_' + date + '.txt' #adjust filename

inc_enc_1d = [] #incrementel encoder positions, run 1, downwards
abs_enc_1d = [] #absolute encoder positions, run 1, downwards; to be corrected

data_file = open('abs_inc_pos_GS_2020_07_21_S2_old_down.txt', 'r') #adjust filename
data = csv.reader(data_file, delimiter=',')
for row in data:
    inc_enc_1d.append(float(row[1]))
    abs_enc_1d.append(float(row[0]))
    
data_file.close()

inc_enc_1d = [inc_enc_1d]
abs_enc_1d = [abs_enc_1d]

inc_enc_1u = [] #incrementel encoder positions, run 1, upwards
abs_enc_1u = [] #absolute encoder positions, run 1, upward; to be corrected

data_file = open('abs_inc_pos_GS_2020_07_21_S2_old_up.txt', 'r') #adjust filename
data = csv.reader(data_file, delimiter=',')
for row in data:
    inc_enc_1u.append(float(row[1]))
    abs_enc_1u.append(float(row[0]))
    
data_file.close()





#generate pseudodata
#x = [50 * n + np.random.uniform(0, 2) for n in range(10 + 1)]
#y = [50 * m + np.random.uniform(0, 20) for m in range(10 + 1)]


#file = open('abs_inc_pos_1_3.txt', 'w')
#for i in range(len(x)):
#    file.write(str(y[i]) + ' , ' + str(x[i]) + '\n')
        
#file.close()        


inc_enc_1u = [inc_enc_1u]
abs_enc_1u = [abs_enc_1u]

inc_enc_1 = inc_enc_1d + inc_enc_1u
abs_enc_1 = abs_enc_1d + abs_enc_1u
#print(inc_enc_1,'\n')

"""
inc_enc_2d = [] #incrementel encoder positions, run 2, downwards
abs_enc_2d = [] #absolute encoder positions, run 2, downwards; to be corrected

data_file = open('abs_inc_pos_UZH_2020_02_05_1_2_run_2_down.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    inc_enc_2d.append(float(row[1]))
    abs_enc_2d.append(float(row[0]))
    
data_file.close()

inc_enc_2d = [inc_enc_2d]
abs_enc_2d = [abs_enc_2d]

inc_enc_2u = [] #incrementel encoder positions, run 2, upwards
abs_enc_2u = [] #absolute encoder positions, run 2, upward; to be corrected

data_file = open('abs_inc_pos_UZH_2020_02_05_1_2_run_2_up.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    inc_enc_2u.append(float(row[1]))
    abs_enc_2u.append(float(row[0]))
    
data_file.close()

inc_enc_2u = [inc_enc_2u]
abs_enc_2u = [abs_enc_2u]

inc_enc_2 = inc_enc_2d + inc_enc_2u
abs_enc_2 = abs_enc_2d + abs_enc_2u
#print(inc_enc_2,'\n')


inc_enc_3d = [] #incrementel encoder positions, run 3, downwards
abs_enc_3d = [] #absolute encoder positions, run 3, downwards; to be corrected

data_file = open('abs_inc_pos_UZH_2020_02_05_1_2_run_3_down.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    inc_enc_3d.append(float(row[1]))
    abs_enc_3d.append(float(row[0]))
    
data_file.close()

inc_enc_3d = [inc_enc_3d]
abs_enc_3d = [abs_enc_3d]

inc_enc_3u = [] #incrementel encoder positions, run 3, upwards
abs_enc_3u = [] #absolute encoder positions, run 3, upward; to be corrected

data_file = open('abs_inc_pos_UZH_2020_02_05_1_2_run_3_up.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    inc_enc_3u.append(float(row[1]))
    abs_enc_3u.append(float(row[0]))
    
data_file.close()

inc_enc_3u = [inc_enc_3u]
abs_enc_3u = [abs_enc_3u]

inc_enc_3 = inc_enc_3d + inc_enc_3u
abs_enc_3 = abs_enc_3d + abs_enc_3u
#print(inc_enc_3,'\n\n')

"""
#inc_enc.append(list(reversed([50 * n + np.random.uniform(0, 2) for n in range(10 + 1)])))
#abs_enc.append(list(reversed([50 * m + np.random.uniform(0, 20) for m in range(10 + 1)])))

#for i in range(cycles - 1): #first cycle already above
#    inc_enc.append([50 * n + np.random.uniform(0, 2) for n in range(10 + i + 1)])
#    inc_enc.append(list(reversed([50 * n + np.random.uniform(0, 2) for n in range(10 + i + 1)])))
#    abs_enc.append([50 * n + np.random.uniform(0, 20) for n in range(10 + i + 1)])
#    abs_enc.append(list(reversed([50 * m + np.random.uniform(0, 20) for m in range(10 + i + 1)])))
     

inc_enc = inc_enc_1# + inc_enc_2 + inc_enc_3
abs_enc = abs_enc_1 #+ abs_enc_2 + abs_enc_3

delta_inc_abs = []
for dim in range(2 * cycles):
    delta_inc_abs.append([inc_enc[dim][n]-abs_enc[dim][n] for n in range(len(inc_enc[dim]))])

print(delta_inc_abs,'\n')


inc_enc_tot = list(flatten(inc_enc))
abs_enc_tot = list(flatten(abs_enc))


#print(abs_enc_tot,'\n')
#print(inc_enc_tot,'\n')


print(max(inc_enc_tot),'\n')
max_index = int(max(inc_enc_tot) / delta_s)
print(max_index,'\n')

delta_inc_abs_tot = [inc_enc_tot[n]-abs_enc_tot[n] for n in range(len(inc_enc_tot))]


#f_int = interp1d(inc_enc_tot, delta_inc_abs_tot, kind='cubic')
f_pol = np.polyfit(inc_enc_tot, delta_inc_abs_tot, pol_ord)
print(f_pol,'\n')

def f_pol_new(x):
    res = 0
    for i in range(pol_ord + 1):
        res += x**(pol_ord-i) * f_pol[i] 
    return res

f_pol_new_inc_val = [f_pol_new(elem) for elem in inc_enc_tot]
delta_corr = [delta_inc_abs_tot[n] - f_pol_new_inc_val[n] for n in range(len(inc_enc_tot))]

print(min(delta_corr),'\n')
print(max(delta_corr),'\n')

print(len(inc_enc_tot),'\n')
print(len(abs_enc_tot),'\n')
print(len(delta_inc_abs_tot),'\n\n')

pos = [delta_s * n for n in range(multi_turns)]      
print(pos,'\n')

abs_corr = [int(f_pol_new(elem)) for elem in pos]
print(abs_corr,'\n')

for index in range(len(pos)):
    if index > max_index:
        abs_corr[index] = 0

abs_corr = list(reversed(abs_corr))
print(abs_corr,'\n')

print(len(abs_corr),'\n')

for zeros in range(turns_tot - multi_turns):
    abs_corr.append(0)

print(abs_corr,'\n')

print(len(abs_corr),'\n')

if corr_table == 1:
    file = open(corr_file_name, 'w') 
    for elem in abs_corr:
        file.write(str('{:+}'.format(elem).zfill(4) + '\n'))
    file.close()
     
mean_before = np.mean(delta_inc_abs_tot)
mean_after = np.mean(delta_corr)

print('\n',mean_before,'\n')
print(mean_after,'\n')


#pos_ax = np.linspace(min(inc_enc_tot), max(inc_enc_tot), num=100, endpoint=True)
#plt.plot(inc_enc[0], delta_inc_abs[0], 'vr', label='moving down', markersize=3)
#plt.plot(inc_enc[1], delta_inc_abs[1], '^b', label='moving up', markersize=3)
#plt.plot(inc_enc[2], delta_inc_abs[2], 'vy', label='cycle 2, down', markersize=3)
#plt.plot(inc_enc[3], delta_inc_abs[3], '^y', label='cycle 2, up', markersize=3)
#plt.plot(inc_enc[4], delta_inc_abs[4], 'vg', label='cycle 3, down', markersize=3)
#plt.plot(inc_enc[5], delta_inc_abs[5], '^g', label='cycle 3, up', markersize=3)
#plt.plot(pos_ax, f_pol_new(pos_ax), 'k-', label='polynomial fit')
#plt.plot(inc_enc_tot, delta_corr, 'sk', label='corrected values', markersize=3)
#plt.hlines(y=mean_before, xmin=0, xmax=9500, color='k', linestyle=':', label='mean of dev.')
#plt.hlines(y=mean_after, xmin=0, xmax=9500, color='k', linestyle='--', label='mean after correction')
#plt.hlines(y=mean_before, xmin=0, xmax=8900, color='k', linestyle='-', label='Mean of abs. enc. position')
#plt.vlines(x=1850, ymin=-6.1, ymax=1.1, color='k', linestyle='--')
#plt.rc('text', usetex=False)
#plt.rc('font', family='serif')
#plt.title('Calibration of the absolute encoder, S3')
#plt.title('After calibrating the absolute encoder')
#plt.xlabel("Incremental encoder position [mm]")
#plt.ylabel("Incremental - absolute encoder position [mm]")
#plt.ylim(-1.25, 2.25)
#plt.yticks([-1, 0, 1, 2])
#plt.legend()
#plt.show()














"""

#for plots with 3 data sets


#2nd data set

zpol_ord = 5

zinc_enc_1d = [] #incrementel encoder positions, run 1, downwards
zabs_enc_1d = [] #absolute encoder positions, run 1, downwards; to be corrected

data_file = open('abs_inc_pos_GS_2020_07_21_S2_zeros_down.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    zinc_enc_1d.append(float(row[1]))
    zabs_enc_1d.append(float(row[0]))
    
data_file.close()

zinc_enc_1d = [zinc_enc_1d]
zabs_enc_1d = [zabs_enc_1d]

zinc_enc_1u = [] #incrementel encoder positions, run 1, upwards
zabs_enc_1u = [] #absolute encoder positions, run 1, upward; to be corrected

data_file = open('abs_inc_pos_GS_2020_07_21_S2_zeros_up.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    zinc_enc_1u.append(float(row[1]))
    zabs_enc_1u.append(float(row[0]))
    
data_file.close()

zinc_enc_1u = [zinc_enc_1u]
zabs_enc_1u = [zabs_enc_1u]

zinc_enc_1 = zinc_enc_1d + zinc_enc_1u
zabs_enc_1 = zabs_enc_1d + zabs_enc_1u

zinc_enc = zinc_enc_1
zabs_enc = zabs_enc_1

zdelta_inc_abs = []
for dim in range(2 * cycles):
    zdelta_inc_abs.append([zinc_enc[dim][n]-zabs_enc[dim][n] for n in range(len(zinc_enc[dim]))])

print(zdelta_inc_abs,'\n')

zinc_enc_tot = list(flatten(zinc_enc))
zabs_enc_tot = list(flatten(zabs_enc))

print(max(zinc_enc_tot),'\n')
zmax_index = int(max(zinc_enc_tot) / delta_s)
print(zmax_index,'\n')

zdelta_inc_abs_tot = [zinc_enc_tot[n]-zabs_enc_tot[n] for n in range(len(zinc_enc_tot))]

zf_pol = np.polyfit(zinc_enc_tot, zdelta_inc_abs_tot, zpol_ord)
print(zf_pol,'\n')

def zf_pol_new(x):
    res = 0
    for i in range(zpol_ord + 1):
        res += x**(zpol_ord-i) * zf_pol[i] 
    return res

zf_pol_new_inc_val = [zf_pol_new(elem) for elem in zinc_enc_tot]
zdelta_corr = [zdelta_inc_abs_tot[n] - zf_pol_new_inc_val[n] for n in range(len(zinc_enc_tot))]

print(min(zdelta_corr),'\n')
print(max(zdelta_corr),'\n')

print(len(zinc_enc_tot),'\n')
print(len(zabs_enc_tot),'\n')
print(len(zdelta_inc_abs_tot),'\n\n')

zpos = [delta_s * n for n in range(multi_turns)]      
print(zpos,'\n')

zabs_corr = [int(zf_pol_new(elem)) for elem in zpos]
print(zabs_corr,'\n')

for index in range(len(zpos)):
    if index > zmax_index:
        zabs_corr[index] = 0

zabs_corr = list(reversed(zabs_corr))
print(zabs_corr,'\n')

print(len(zabs_corr),'\n')

for zeros in range(turns_tot - multi_turns):
    zabs_corr.append(0)

print(zabs_corr,'\n')

print(len(zabs_corr),'\n')
     
zmean_before = np.mean(zdelta_inc_abs_tot)
zmean_after = np.mean(zdelta_corr)

print('\n',zmean_before,'\n')
print(zmean_after,'\n')



#3rd data set

cpol_ord = 3

cinc_enc_1d = [] #incrementel encoder positions, run 1, downwards
cabs_enc_1d = [] #absolute encoder positions, run 1, downwards; to be corrected

data_file = open('abs_inc_pos_GS_2020_07_21_S2_corr_down.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    cinc_enc_1d.append(float(row[1]))
    cabs_enc_1d.append(float(row[0]))
    
data_file.close()

cinc_enc_1d = [cinc_enc_1d]
cabs_enc_1d = [cabs_enc_1d]

cinc_enc_1u = [] #incrementel encoder positions, run 1, upwards
cabs_enc_1u = [] #absolute encoder positions, run 1, upward; to be corrected

data_file = open('abs_inc_pos_GS_2020_07_21_S2_corr_up.txt', 'r')
data = csv.reader(data_file, delimiter=',')
for row in data:
    cinc_enc_1u.append(float(row[1]))
    cabs_enc_1u.append(float(row[0]))
    
data_file.close()

cinc_enc_1u = [cinc_enc_1u]
cabs_enc_1u = [cabs_enc_1u]

cinc_enc_1 = cinc_enc_1d + cinc_enc_1u
cabs_enc_1 = cabs_enc_1d + cabs_enc_1u

cinc_enc = cinc_enc_1
cabs_enc = cabs_enc_1

cdelta_inc_abs = []
for dim in range(2 * cycles):
    cdelta_inc_abs.append([cinc_enc[dim][n]-cabs_enc[dim][n] for n in range(len(cinc_enc[dim]))])

print(cdelta_inc_abs,'\n')

cinc_enc_tot = list(flatten(cinc_enc))
cabs_enc_tot = list(flatten(cabs_enc))

print(max(cinc_enc_tot),'\n')
cmax_index = int(max(cinc_enc_tot) / delta_s)
print(cmax_index,'\n')

cdelta_inc_abs_tot = [cinc_enc_tot[n]-cabs_enc_tot[n] for n in range(len(cinc_enc_tot))]

cf_pol = np.polyfit(cinc_enc_tot, cdelta_inc_abs_tot, cpol_ord)
print(cf_pol,'\n')

def cf_pol_new(x):
    res = 0
    for i in range(cpol_ord + 1):
        res += x**(cpol_ord-i) * cf_pol[i] 
    return res

cf_pol_new_inc_val = [cf_pol_new(elem) for elem in cinc_enc_tot]
cdelta_corr = [cdelta_inc_abs_tot[n] - cf_pol_new_inc_val[n] for n in range(len(cinc_enc_tot))]

print(min(cdelta_corr),'\n')
print(max(cdelta_corr),'\n')

print(len(cinc_enc_tot),'\n')
print(len(cabs_enc_tot),'\n')
print(len(cdelta_inc_abs_tot),'\n\n')

cpos = [delta_s * n for n in range(multi_turns)]      
print(cpos,'\n')

cabs_corr = [int(cf_pol_new(elem)) for elem in cpos]
print(cabs_corr,'\n')

for index in range(len(cpos)):
    if index > cmax_index:
        cabs_corr[index] = 0

cabs_corr = list(reversed(cabs_corr))
print(cabs_corr,'\n')

print(len(cabs_corr),'\n')

for zeros in range(turns_tot - multi_turns):
    cabs_corr.append(0)

print(cabs_corr,'\n')

print(len(cabs_corr),'\n')
     
cmean_before = np.mean(cdelta_inc_abs_tot)
cmean_after = np.mean(cdelta_corr)

print('\n',cmean_before,'\n')
print(cmean_after,'\n')


#plot with 3 polynomial functions
#darkgreen, darkred, midnightblue

pos_ax = np.linspace(min(inc_enc_tot), max(inc_enc_tot), num=100, endpoint=True)
plt.plot(pos_ax, f_pol_new(pos_ax), '-', label='old', color='darkorange')
zpos_ax = np.linspace(min(zinc_enc_tot), max(zinc_enc_tot), num=100, endpoint=True)
plt.plot(zpos_ax, zf_pol_new(zpos_ax), '-', label='no corr.', color='red')
cpos_ax = np.linspace(min(cinc_enc_tot), max(cinc_enc_tot), num=100, endpoint=True)
plt.plot(cpos_ax, cf_pol_new(cpos_ax), '-', label='new', color='blue')
plt.hlines(y=mean_before, xmin=0, xmax=8690, color='darkorange', linestyle=':', label='mean of dev., old')
plt.hlines(y=zmean_before, xmin=0, xmax=8690, color='red', linestyle=':', label='mean of dev., no corr.')
plt.hlines(y=cmean_before, xmin=0, xmax=8690, color='blue', linestyle=':', label='mean of dev., new')
plt.rc('text', usetex=False)
plt.rc('font', family='serif')
plt.title('Absolute encoder calibration, S2')
plt.xlabel("Incremental encoder position [mm]")
plt.ylabel("Incremental - absolute encoder position [mm]")
#plt.ylim(-2.25, 1.25)
#plt.yticks([-2, -1, 0, 1])
plt.legend()
plt.show()




"""