#!/usr/bin/env python
# coding: utf-8

# # Python Code for IO controller
# 
# Author: Anniken Semb Kvalsund
# 
# This file contains the python code used for communication with an Arduino microcontroller configured as an IO-module. The python program communicates with the Arduino through serial bus.

# **NOTE:**
# Information sent to the Arduino must be bytewise, not as strings, as the Arduino controller reads strings too slow.
# Capital letters, special symbols and lower case a,b,c and d are reserved for ASCII byte representation of integer values between 0-100. 
# 
# If access to port denied, close Arduino IDE and try again.

# ## Main Code

# Importing libraries etc:

# In[1]:


#%pylab notebook
import serial
import time
import numpy as np


# Establishing communication with the serial port. Remember to change the 'COM3' to whichever port is in use. The time.sleep(2) allows for some startup time for the Arduino.

# In[2]:


ser = serial.Serial('COM3', baudrate = 9600, timeout = 1)   # Timeout unit = seconds
time.sleep(2)


# **Scaling function**
# <br> 
# An allround useful function for scaling variables
# 

# In[3]:


# Function to convert value to different scales
def scaleVal(invalue, in_min, in_max, out_min, out_max):                            
    out = ((invalue - in_min)/(in_max-in_min))*(out_max-out_min)+out_min       
    return out

#print(ScaleVal(0,-10,10,-1000,1000))


# 
# **Defining variables** etc.
# numPoints defines how many data point one wants to collect in one round (based on a for-loop). This will eventually be removed in a final stage of the program. The dataList creates a list for said collected datapoints.

# In[4]:


numPoints = 20                       # Number of data rows to be collected. Remove when program is continuously reading.
dataList = np.array([0]*numPoints)   # Create list for data points.           
#AIs = [None]*numPoints]       # Analogue input matrix
whileLoop = True
Ch = ['0','1','2','3']

rounds = 0 # For counting round of AI read

AI_1_temp = [None]*numPoints
AI_2_temp = [None]*numPoints
AI_3_temp = [None]*numPoints


# **Sanitising input function**
# <br>
# Makes the user type in answers until they type in a valid one. <br>
# Found at: https://stackoverflow.com/questions/23294658/asking-the-user-for-input-until-they-give-a-valid-response

# In[5]:


def clean_input(prompt, type_=None, min_=None, max_=None, range_=None):
    if min_ is not None and max_ is not None and max_ < min_:
        raise ValueError("min_ must be less than or equal to max_.")
    while True:
        ui = input(prompt)
        if type_ is not None:
            try:
                ui = type_(ui)
            except ValueError:
                print("Input type must be {0}.".format(type_.__name__))
                continue
        if max_ is not None and ui > max_:
            print("Input must be less than or equal to {0}.".format(max_))
        elif min_ is not None and ui < min_:
            print("Input must be greater than or equal to {0}.".format(min_))
        elif range_ is not None and ui not in range_:
            if isinstance(range_, range):
                template = "Input must be between {0.start} and {0.stop}."
                print(template.format(range_))
            else:
                template = "Input must be {0}."
                if len(range_) == 1:
                    print(template.format(*range_))
                else:
                    expected = " or ".join((
                        ", ".join(str(x) for x in range_[:-1]),
                        str(range_[-1])
                    ))
                    print(template.format(expected))
        else:
            return ui


# ### Functions

# **Read analogue inputs** 
# <br>
# The 'AI_read' function reads values from the analogue inputs (A0-A3). The data is transmitted with 10bit resolution.

# In[6]:


# Function for reading analogue values
def AI_read():    
    #ser.write(b'e')                                     # b signifies that we're writing a byte to the serial bus
    arduinoData = ser.readline().decode().rstrip()      # Reads the arduino point from the ser port specified above. Readline reads until the end of line character. ascii decode removes the information around data read (byte rn)   
    list_values = arduinoData.split('x')                # Splits the multiple elements by x
#    list_values_int = list(map(int, list_values))      # Converts lists of strings to list of integers
    return list_values


# **Sort Collected Data in Matrix**
# <br>
# The function 'sortData' calls the 'AI_read' function, as described above and sorts the arrays into a matrix-form.. Each column in the matrix represents the values collected from one input.

# In[7]:


#Function to sort data in Matrix
def sortData(AI1, AI2, AI3):
    for i in range(0,numPoints):               # Limits number of data transferred. Can be removed later
        ser.write(bytes('e', 'utf-8'))         # calls for an analogue input reading
        ser.write(bytes('\n', 'utf-8'))
        data = AI_read()                       # Call the Function that reads the Analogue values
        #print(data)                            # Prints the recieved data

        # Sorting data from the three different channels to their own array     
        AI_1_temp[i] = round(scaleVal(int(data[0]),0,1023,-10,10),3)
        AI_2_temp[i] = round(scaleVal(int(data[1]),0,1023,-10,10),3)
        AI_3_temp[i] = round(scaleVal(int(data[2]),205,1023,4,20),3)

    AI1_return = AI1 + AI_1_temp
    AI2_return = AI2 + AI_2_temp
    AI3_return = AI3 + AI_3_temp
    
    #print('\nAI 1 = ', AI1_return,'\nAI 2 = ', AI2_return,'\nAI 3 = ', AI3_return,)
    #print('\nAI 1 = ', AI_1, '\nAI 2 = ', AI_2, '\nAI 3 = ', AI_3)
    
    return AI1_return,AI2_return,AI3_return


# **Controlling built in Arduino LED**
# <br>
# The function can switch on and off the built in Arduino LED. It is not a vital function, but comes in handy during troubleshooting plausible connectin issues.

# In[8]:


# Function for controlling built in Arduino LED
def LEDonoff(LEDcontr):
    if LEDcontr == 'on':
        ser.write(bytes('h', 'utf-8'))
        ser.write(bytes('\n', 'utf-8'))
    elif LEDcontr == 'off':
        ser.write(bytes('i', 'utf-8'))
        ser.write(bytes('\n', 'utf-8'))
    arduinoData = ser.readline().decode()
    return arduinoData


# **Limit Function (utils)**
# <br>
# This function makes sure the number is within a specified range. Default is 0-100

# In[9]:


#Limits input 'num' between minimum and maximum values
def limit(num, minimum=0, maximum=100):
    limited = max(min(num, maximum), minimum)
    return limited


# **Analog / Digital Out write**
# <br>
# This function formats the neccessary info and sends it bytewise to the bus. The values are collected form an array separated by x'es and ended by a '~' <br> 
# - The first value in array chooses between digital or analogue channels. 'o' for analogue and 'p' for digital.
# - The second value specifies the channel number
# - The third value specifies the value to be sent on said channel. For analogue 0-100, for digital 0 or 1.

# In[10]:


# Function for sending an array of information to serial bus, separated by x'es and endedn with \n. UTILS
def byteWriteArray(AD,chNo,chVal):              # Inputs must be characters
    
    channelAD = bytes(AD, 'utf-8')              # Convert AD (o/p) to byte
    channelNo = bytes(chNo, 'utf-8')            # Convert chNumber to byte
    channelVal = bytes(chVal, 'utf-8')     # Converts ch value to ASCII character to byte
                
    fullArray = [channelAD, channelNo, channelVal] # Creates array of analog,chNumber and value
        
    for i in range(0, (len(fullArray))):        # Send values for the length og the array
        ser.write(fullArray[i])                 # Send value in array
        #print(fullArray[i])
        if i <= (len(fullArray)-2):             # Goes to else at second last element
            ser.write(bytes('x', 'utf-8'))      # Separate by x between each element, exept for after the last
        else:
            ser.write(bytes('\n', 'utf-8'))           # End with new line char  
    
    print(channelAD,channelNo,channelVal)


# **Print Results**
# <br>
# -- NOT needed, useful when troubleshooting. --
# <br>
# This function simply prints the feedback and its type sent from the arduino.

# In[11]:


# This function is for testing purposes only
def printResults():
    feedback = ser.readline().decode().rstrip()  # Reads the arduino point from the ser port specified above. Readline reads until the end of line character. ascii decode removes the information around data read (byte rn)   
    print('Recieved arduino Data: ',feedback)
    print('Recieved data type: ',type(feedback),'\n\n')


# **Arduino max AO cal**
# <br>
# This functio is made for ard. AO calibration. The PWM AO should ideally put out about 5V, but the real voltage is usually a bit higher. The function is based on arduinos maximum out value being 255, and adjusts this down accordingly to create exactly 5V out. To avoid too large numbers on the serial bus (should ideally be between 0 and 100, sent as byte) the function finds the difference between the desired output(10V) and real output, multiplies it by 100 to avoid decimals and sends this value to the arduino. The measured voltage should be between 10 and 11. If outside this range, other measures must be take to correct it anyways. The function is based on:
# 
# $$ArduinoAO_{max,new}=\frac{V_{max,desired}}{\frac{V_{max,real}}{Arduino_{max}}} = \frac{10V}{\frac{10.xV}{255}}$$
# 
# 

# In[12]:


# This funtion is used to adjust the maximum output value for arduino PWM outputs

def arduinocal(Vmeas_max,Vmeas_min,Vdesired):
    i = 0
    Vclosetomin = False   # Used to reset and try again is voltage is too low
    Vreset = False # Used to reset max value
    sendValue = 0  # Difference value to be sent to Arduino

    AOchannels = ['AO_0','AO_1','AO_2','AO_3']   # Array of analogue output channels
    print(' - Press enter to go to next channel. \n - Type reset to reset channel value.\n')
    
    for i in range(0, (len(AOchannels))):
        Vreset = False # Resets the Vreset variable for every channel.
        
        while True: # Only accepts numbers as input, loops to avoid errors.
            Vmeas_str = input('Measured output voltage channel {}: '.format(AOchannels[i]))
            
            if not Vmeas_str:   # If user presses "enter", then break loop and go to next channel
                break
            else:
                if Vmeas_str == 'reset' or Vmeas_str == 'Reset':  # Reset maximum value
                    Vreset = True
                else:
                    try:
                        Vmeas_float = float(Vmeas_str)    # Ensures the input is a number
                    except ValueError:
                        print('Not a valid number. Use . as decimal symbol.')
                        continue
                        
            if (not Vreset) and (Vmeas_float > Vmeas_max or Vmeas_float < (Vmeas_min-1)):   # Checks if the number is (not) within the right range
                print('Find other source of adjustment. Voltage deviance too high.')
                break

            else:
                if (not Vreset) and (Vmeas_float > (Vmeas_min-1) and Vmeas_float < Vmeas_min): # If measured value is between 9-10, reset
                    Vreset = True
                    Vclosetomin = True
                    print('Channel ', AOchannels[i],' is too low. Max value reset to default.\nPlease try again.')
                
                if Vreset == True:
                    sendValue = 'r'
                else:
                    dev_val = int(round((Vmeas_float - Vdesired)*100))  # Calculates deviation between desired and actual value
                    #print("Deviation 0-100 = ",dev_val)
                    sendValue = str(chr(dev_val))
                
                byteWriteArray('q', str(i), sendValue) # Change the max value
                byteWriteArray('o', str(i), 'd') # Set said channel to max
                
                if Vclosetomin == True:  # Resets Vclosetomin variable and runs the loop once more if value between 9 and 10.
                    Vclosetomin = False
                    continue
                else:
                    break


# **Main**
# <br>
# This is the main function of the program. The user is asked which function they would like to run, and the if-statements calls the respective function. In a final version, the read functions will run continuously, and the write will run when changed.

# In[13]:


#%% Main program

def application():

    whileLoop = True
     
    AI_0 = []
    AI_1 = []
    AI_2 = []
    
    AI0tmp = []  # Placeholders for AI lists
    AI1tmp = []
    AI2tmp = []
    
    modes = ['read','write','cal','on','off','q','Q'] # Modes/programs
    
    
    #Whileloop:
    while whileLoop == True:
    
        print('\nGet Data? \n - ',modes[0],' = analogue input values \n - ',modes[1],' = Write to analogue or digital out \n - ',modes[2],' = Calibrate arduino analogue outputs. \n - ',modes[3],' = LED on \n - ',modes[4],' = LED off \n - ',modes[5],' = Close Port \n')
        
        # Asking which function should be rund
        chooseMode = clean_input('Please choose mode: ', range_=modes)
            
            
        # Get datapoints from analogue inputs A0, A1, A2 and A3    
        if chooseMode == modes[0]:   # If user press AI, get datapoints 
            AI0tmp = AI_0
            AI1tmp = AI_1
            AI2tmp = AI_2
            AI_0, AI_1, AI_2 = sortData(AI0tmp, AI1tmp, AI2tmp)
            
            print('\nAI 0: ',AI_0,'\nAI 1: ',AI_1,'\nAI 2: ',AI_2,'\n')
    
        # Analogue/digital write
        if chooseMode == modes[1]: 
        
            # Ask if write to analogue or digital out
            ADInput = clean_input('Select A for analogue, or D for digital: ',range_=('A','a','D','d')) # Choose between analogue and digital channels
            chNumberInput = clean_input('Select channel number: ',range_=Ch) # Write desired channel number.  
        
            # Analogue write out
            if (ADInput == 'A' or ADInput == 'a') and chNumberInput in Ch: 
            
                numberinput = clean_input('Insert value 0-100: ', type_=int, min_=0, max_=100) # Ask for value between 0-100 to send to ard
                
                byteWriteArray('o', chNumberInput, str(chr(numberinput))) # chr=int to ASCII, then converted to string


            # Digital write out            
            elif (ADInput == 'D' or ADInput == 'd') and chNumberInput in Ch:
            
                onoffin = clean_input('True or False?', range_=('True','true','on','1','False','false','off','0')) # Ask if DO  should be high or low
            
                if onoffin == 'True' or onoffin == 'true'  or onoffin =='on' or onoffin == '1':# Checks if true
                    onoff = 100
            
                elif onoffin == 'False' or onoffin == 'false'  or onoffin =='off' or onoffin == '0':# Checks if false
                    onoff = 0        
                    
                else:
                    print('Something is wrong\n')
                
                byteWriteArray('p', chNumberInput, str(chr(onoff)))
                
            else:
                print('Invalid input. Channel must be A or D, and number between 0-3\n\n')
                

                
        if chooseMode == modes[2]:    # Calibration:
            
            enterCalMode = clean_input('Entering calibration mode. Please make sure equipment is disconnected before continuing.\nDo you want to proceed? Y/N: ',range_=('Y','y','N','n'))

            
            if enterCalMode == 'Y' or enterCalMode == 'y':
                for k in range(0, 4):
                    byteWriteArray('o', str(k), 'd') # Setting all the AO to max
            
                print('\nCalibration mode. Please measure the output analogue output one by one.')
                arduinocal(11,10,10)
                
        # Switch builtin LED on/off
        if chooseMode == modes[3] or [4]:
            LEDonoff(chooseMode)
                
        if chooseMode == modes[5] or chooseMode == modes[6]:
            print('Serial port closed.')
            ser.close()
            whileLoop = False


# **If name is main**
# <br>
# This runs the main function

# In[14]:


# %% Running
if __name__ == '__main__':
    application()
    

