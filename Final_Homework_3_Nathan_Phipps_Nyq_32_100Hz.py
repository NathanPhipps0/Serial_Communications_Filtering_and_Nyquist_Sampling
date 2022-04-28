#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author: nathanphipps
"""


import serial
from signal import signal, SIGINT
from time import sleep

import time
import struct

import matplotlib.pyplot as plt
import numpy as np

#Ready ACK


keepRunning = True 

def handler(signal, frame):
    global keepRunning 
    print('SIGINT or CTRL+C detected, setting keepRunning to False')
    keepRunning = False


def serialConnect(portName):
    try: 
        ser = serial.Serial(portName)
        print("opened port " + ser.name + '\n')
        # give Arduino time to reset
        sleep(2)
        # flush input buffer, discarding all contents
        ser.reset_input_buffer()
        return ser 
    except serial.SerialException:
        raise IOError("problem connecting to " + portName)


def waitForReadySignal(ser):
    readyMsg = 'READY'
    global keepRunning 
    readyReceived = False  

    while readyReceived  == False and keepRunning == True:
        while ser.in_waiting < len(readyMsg):
            pass
        
        '''
        read_until(expected=LF,size=None)
        read until an expected sequence is found('\n' by default),
        the size is exceeded or until timeout occurs. With no timeout
        it will block until the requested number of bytes is read
        '''
        print("ready to read")
        bytesRead = ser.read_until()
        print("bytesRead: ", end='')
        print(bytesRead)

        # convert byte string to unicode string, remove leading and trailing whitespace
        receivedMsg = bytesRead.decode().strip()   # decode default is 'utf-8'
        print(receivedMsg)
        if receivedMsg == readyMsg:
            readyReceived = True
            print("received ready message: " + receivedMsg)
        else:
            print("expected ready message, received: " + str(bytesRead))

        return ser


def sendAck(ser):
    ackMessage = 'ACK\n'
    ser.write(ackMessage.encode())
    return ser


#Frequency Ack

keepRunning = True 

def handler(signal, frame):
    global keepRunning 
    print('SIGINT or CTRL+C detected, setting keepRunning to False')
    keepRunning = False


def serialConnect(portName):
    try: 
        ser = serial.Serial(portName)
        print("opened port " + ser.name + '\n')
        # give Arduino time to reset
        time.sleep(2)
        # flush input buffer, discarding all contents
        ser.reset_input_buffer()
        return ser 
    except serial.SerialException:
        raise IOError("problem connecting to " + portName)


def getSignalFrequency():
    freq = -1.0
    while(freq < 1.0 or freq > 250.0):
        # input returns a string, convert it to a float
        freq = float(input('enter signal frequency in range [1.0,250.0] '))
        freq = round(freq, 2) #round frequency to two decimal places
    return freq
    

def sendSignalFrequency(ser, freq):
    # convert float to 4 byte, bytes object
    freqBytes = struct.pack('f',freq)

    # not necessary to convert to bytearray type
    # but can do so with the code below
    #freqBytes = bytearray(struct.pack('f',freq))

    #print("Debug: sendSignalFrequency(ser,freq) ")
    print("freqBytes: ", end='')
    print([ "0x%02x" % b for b in freqBytes])
    if len(freqBytes) == 4:
        ser.write(freqBytes)
        return True 
    else:
        print("error: len(freqBytes) " + str(len(freqBytes)))
        print("Arduino expects 4 bytes")
        return False 

'''def recursive_bounds():
    if q == 0:
        return []
    return recursive_bounds(q-1) + [q-1]'''


if __name__ == '__main__':
    #register the signal handler
    signal(SIGINT, handler)
    portName = "/dev/cu.usbmodem411"
    ser = serialConnect(portName)
    ser = waitForReadySignal(ser) 
    Signal_Values_Transmitted = False
    values_list = [] #list for storing values from signal arrays
    
    
    if Signal_Values_Transmitted != True:
        ser.reset_input_buffer() #discards and clears everything in input buffer
        ser = sendAck(ser) #send acknowledgement string
        print("ack sent") 
        signalFreq = getSignalFrequency()
        
        
    if sendSignalFrequency(ser, signalFreq) == True:
        print("transmitted signal frequency")
    else:
        print("failed to transmit signal frequency")
        ser.close()
        exit(1)

    print("Waiting for ack")
    
    start = time.monotonic()
    while(time.monotonic() - start) < 1./10.:
        pass

    print(time.monotonic() - start)
    
    
    # Inside here we read serial data, clean it, form lists, clean the lists, and prepare for plotting
    while Signal_Values_Transmitted != True and keepRunning == True: # This condition ends when we hit the last serial print value in the sine function in arduino this value is "Signal Values Transmitted"
            if ser.in_waiting > 0: # if theres data read the data below
                val = ser.read_until().decode('utf-8') #added the "until" and removed number in bracket to allow 4 bytes per line rather than vertical bytes, keeps reading data
                print(val)
            
                val_clean = val
                
                #code below cleans the list, strips whitespace and appends a list with cleaned out values to later be turned into a floated list for plotting
                if val_clean.strip() != "READY": #Uses serial statement read from arduino in python, if the ready signal is received in val_clean which has the list that val previously serially read, a cleaned out list named values_list is created 
                    #strips whitespace so that a list of Signal values can be broken down into only values, not strings, in order to plot
                    val_clean = val.lstrip()
                    val_clean = val.rstrip()
                    values_list.append(val_clean) #append and store values into values_list
                    
            else:
                print("main keepRunning loop")
                #print(clean_sine_list)
                sendSignalFrequency(ser,signalFreq)
            
                
                #This comment piece is nonfunctional, I tried to make this to adapt the indexing I did in future segments, when storing lists, easier
                #detect string noisey data so we can set a range determining the length of the first clean sine list and the start of the next list
                #this idea was scrapped since I couldn't get it working and am strapped for time.
                '''clean_index = 0
                Detect_string = 0
                keep_loopingA = 1
                while keep_loopingA == 1:
                    Detect_string += 1 #indexes string detector so I can input my index bounds
                    if values_list[Detect_string] == "Noisey Data":
                        clean_index = int(Detect_string)
                        print("Index until ")
                        print(clean_index)
                        keep_loopingA = 0'''
                
                
                # Below is different functional comments for different nyq frequencys
                # These comments work
                # If you change arduino nyquist settings in arduino, you must comment out any other nyquist based code, and uncomment this
                # Below is the code for Nyquist 100
                
                '''#eleiminate strings so we only get numbers in list, this was reliant on trial and error process until strings removed
                # I changed this initial process in my other nyquist dependent codes since it was weird in the other ones.
                #c1, c2, c3 are unaffected sine signal data, being cleaned up for the printing process
                values_list_c1 = values_list[4:] #skips first four messages to ensure only values
                values_list_c2= values_list_c1[:int(len(values_list)/3)] #Here, the colon denotes the first list will stop at 1/3 of the values after skipping the first 4 values
                values_list_c3 = values_list_c2[:-3] # this ends the loop before "noisey signal" string
                clean_sine_list = values_list_c3
                #print(clean_sine_list) #prints clean sine values list
                
                # noisey data being cleaned up with 3 processes, trial and error til strings such as "noisey data" is perfectly removed
                values_list_n1 = values_list_c1[400:] # starts array near 2nd partition denoted by "noisey data" string in array
                values_list_n2 = values_list_n1[2:] #eliminates "noisey data" string leaving only values from noisey data list
                values_list_n3 = values_list_n2[:-406] # end of noisey signal list range
                noisey_sine_list = values_list_n3 #
                
                #print(noisey_sine_list)
                
                #Low Pass List
                values_list_lp1 = values_list_c1[804:-5] 
                low_passed_list = values_list_lp1
                print(low_passed_list)'''
                
                # This comment works 
                # If you change arduino nyquist settings in arduino, you must comment out any other nyquist based code, and uncomment this
                # Below is the nyquist code for a nyquist of 16
                
                '''#eleiminate strings so we only get numbers in list, this was reliant on trial and error process until strings removed
                #clean sine
                values_list_c1 = values_list[4:69] 
                clean_sine_list = values_list_c1
                #print(clean_sine_list) #prints clean sine values list
                
                #noisey data being cleaned up trial and error til strings such as "noisey data" is perfectly removed
                #noisey data
                values_list_n1 = values_list[70:135] #perfectly indexed
                noisey_sine_list = values_list_n1
                #print(noisey_sine_list) 
                
                #Low Pass List
                values_list_lp1 = values_list[136:201]
                low_passed_list = values_list_lp1
                #print(low_passed_list)'''
                
                # Theis comment works
                # If you change arduino nyquist settings in arduino, you must comment out any other nyquist based code, and uncomment this
                #below is nyquist code for 32
                
                #Unaffected Sine, eleiminate strings via indexing so we only get numbers in list, this was reliant on trial and error process until strings removed
                values_list_c1 = values_list[4:133] #perfect index
                clean_sine_list = values_list_c1
                
                #print(clean_sine_list) #prints clean sine values list
                
                #Noisey, trial and error, indices perfect
                values_list_n1 = values_list[134:263] # perfect, starts array near 2nd partition denoted by "noisey data" string in array
                noisey_sine_list = values_list_n1 
                
                #print(noisey_sine_list)
                
                #Low Pass List, indices perfect
                values_list_lp1 = values_list[264:393] #perfect indexes
                low_passed_list = values_list_lp1
                
                #print(low_passed_list)
                
                

                print(values_list[-1]) #I used this print to determine final string in arduino values function, and then used that transmission to signal the end of my looping statements allowing the program to terminate
                
                
                if values_list[-1] == 'Signal Values Transmitted': # I used a print statement to determine the last value in values list to end looping statements, "Signal Values Transmitted" ends loop
                    Signal_Values_Transmitted = True #Important, ends bigger loop
            
                # kill a bit of time before running through loop again
                # Arduino program transmitting every 2 sec
                time.sleep(100/1000) 
    
    if Signal_Values_Transmitted == True:
        #create lists with values_list after converting to float for each value in list
        clean_sine_list_final = [float(i) for i in clean_sine_list] 
        noisey_sine_list_final = [float(i) for i in noisey_sine_list]
        low_passed_list_final = [float(i) for i in low_passed_list]
        
        
        '''#Solves RMSE Calculation to determine error
        rms_filter_to_sine = float(np.sqrt(np.mean(((float(i) for i in low_passed_list_final) - (float(i) for i in clean_sine_list_final))**2)))
        rms_noise_to_sine = float(np.sqrt(np.mean((noisey_sine_list_final-clean_sine_list_final)**2)))
        rms_filter_to_noise = float(np.sqrt(np.mean((low_passed_list_final-noisey_sine_list_final)**2)))
        
        #Print Statements for RMS
        print("Low pass compared to sine")
        print(rms_filter_to_sine)
        print("Noise compared to sine")
        print(rms_noise_to_sine)
        print("Low pass compared to noise")
        print(rms_filter_to_noise)'''
        
        # using different values_lists to generate a list of sample times for axis, probably could have just used one axis since same samples in each
        e = list(range(len(noisey_sine_list)))
        t = list(range(len(clean_sine_list))) 
        g = list(range(len(low_passed_list))) 
        
        #float all the data in the lists for output into a plot
        clean_sine_list_final = [float(i) for i in clean_sine_list] 
        noisey_sine_list_final = [float(i) for i in noisey_sine_list]
        low_passed_list_final = [float(i) for i in low_passed_list]
                        
     
        #Prints a graph of Clean, Noisey, and LowPassed Signal
        plt.figure()
        plt.plot(t, clean_sine_list_final, color='green',label='Unaffected Sine', linewidth = 6)
        plt.plot(e, noisey_sine_list_final, color='red',label='Noisey Signal')
        plt.plot(g, low_passed_list_final, color='blue',label='Low Passed Siganal')
        plt.xlabel("Number of Samples")
        plt.ylabel("Signal Amplitude")
        plt.title("Amplitude per Samples")
        plt.legend()
        plt.savefig("Signal_Plots.png") #saves plots
        
        print('while loop terminated') #end of program
        ser.close()
        print("closed port") 
    
    