from tkinter import *
import math
import time
import random
import numpy as np
import sys
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.unicode'] = True

np.set_printoptions(threshold=sys.maxsize)


##### --------------------------- VARIABLES ---------------------------

#Simulation mode random=0, logic=1
FindEPN = 0

#Simulation mode random=0, logic=1
FindCore = 0

#Plotting mode none=0 FLPLeaf-Core=1 Core-EPNLeaf=2 EPNs=3 ThesisMode=4
plottingMode = 4

#Showing only values from overflow rounds 0=no 1=yes
onlyOverflow = 0

#Simulation data
FLP_sending_rate = 25
EPN_receiving_rate = 100

speed = 0
rounds_displayed = 10000


#important constants
screenWidth = 1280
screenHeight = 720

num_FLP = 160
num_FLPLeaf = 4
num_Core = 5
num_EPNLeaf = 14
num_EPN = 756
EPN_per_row = 18
num_EPN_slots = 3

cap_FLP_to_FLPLeaf = 1
cap_FLPLeaf_to_Core = 3
cap_Core_to_EPNLeaf = 1
cap_EPNLeaf_to_EPN = 1

size_FLP = (screenHeight-20)/num_FLP
size_FLPLeaf = (screenHeight-20)/num_FLPLeaf/2
size_Core = (screenHeight-20)/num_Core/2
size_EPNLeaf = (screenHeight-20)/num_EPNLeaf/2
size_EPN = (screenHeight-20)/num_EPN*EPN_per_row/2

num_send_frames = int(EPN_receiving_rate/FLP_sending_rate)

#every second is one round
round = 0

#variables for sliding sending_frame
subTimeFrame_index = 0
sendFrame = 0
startIndex1 = 0
startIndex2 = 40
startIndex3 = 80
startIndex4 = 120

startIndex31 = 0
startIndex32 = 53
startIndex33 = 106
startIndex34 = 159

#counts overflow_errors
overflow_FLPLeaf_Core = 0
overflow_Core_EPNLeaf = 0
overflow_EPNLeaf_EPN = 0

overflow_rounds_FLPLeaf_Core = []
overflow_rounds_Core_EPNLeaf = []
overflow_rounds_EPNLeaf_EPN = []
overflow_rounds_total = []

for i in range(rounds_displayed):
    overflow_rounds_FLPLeaf_Core.append(0)
    overflow_rounds_Core_EPNLeaf.append(0)
    overflow_rounds_EPNLeaf_EPN.append(0)


###### --------------------------- SWITCHES AND LINKS ---------------------------

#Initialize devices/switches
FLP = [] #two-dimensional array contains subtimeframes as numbers
FLP_send = [] #contains values if FLP is sending
FLPLeaf = []
Core = []
EPNLeaf = []
EPN = []
EPN_process = []
EPN_slots = []

#Calculate the EPNs involved in overflows
EPN_ovf_involved = []
EPN_buffer_FLPLeaf_Core = []
EPN_buffer_Core_EPNLeaf = []

for i in range(num_FLP):
    FLP.append([])
    FLP_send.append(0)
for i in range(num_FLPLeaf):
    FLPLeaf.append(0)
for i in range(num_Core):
    Core.append(0)
for i in range(num_EPNLeaf):
    EPNLeaf.append(0)
for i in range(num_EPN):
    EPN.append(0)
    EPN_ovf_involved.append(0)
    EPN_process.append([])
    EPN_slots.append(0)
    EPN_buffer_FLPLeaf_Core.append(0)
    EPN_buffer_Core_EPNLeaf.append(0)
for i in range(num_EPN):
    for j in range(num_EPN_slots):
        EPN_process[i].append(0)


#Initialize connections between devices/switches
FLP_to_FLPLeaf = []
for i in range(num_FLP*cap_FLP_to_FLPLeaf):
    FLP_to_FLPLeaf.append(0)

FLPLeaf_to_Core = []
for i in range(num_FLPLeaf*num_Core*cap_FLPLeaf_to_Core):
    FLPLeaf_to_Core.append(0)

Core_to_EPNLeaf = []
for i in range(num_Core*num_EPNLeaf*cap_Core_to_EPNLeaf):
    Core_to_EPNLeaf.append(0)

EPNLeaf_to_EPN = []
for i in range(num_EPN*cap_EPNLeaf_to_EPN):
    EPNLeaf_to_EPN.append(0)

#following arrays count the total usage
FLP_to_FLPLeaf_total = []
for i in range(num_FLP*cap_FLP_to_FLPLeaf):
    FLP_to_FLPLeaf_total.append(0)

FLPLeaf_to_Core_total = []
for i in range(num_FLPLeaf*num_Core*cap_FLPLeaf_to_Core):
    FLPLeaf_to_Core_total.append(0)

Core_to_EPNLeaf_total = []
for i in range(num_Core*num_EPNLeaf*cap_Core_to_EPNLeaf):
    Core_to_EPNLeaf_total.append(0)

EPNLeaf_to_EPN_total = []
for i in range(num_EPN*cap_EPNLeaf_to_EPN):
    EPNLeaf_to_EPN_total.append(0)

##### --------------------------- PLOTTING ---------------------------
fdim = 0
plotName = ""

if(plottingMode==1):
    fdim = num_FLPLeaf*num_Core*cap_FLPLeaf_to_Core
    plotName = "Links between FLPLeafs and Core-Switches "
if(plottingMode==2):
    fdim = num_Core*num_EPNLeaf*cap_Core_to_EPNLeaf
    plotName = "Links between Core-Switches and EPN-Leafs "
if(plottingMode==3):
    fdim = num_EPN
    plotName = "Overview EPN nodes "
if(plottingMode==4):
    fdim = num_EPN
    plotName = "Overview EPN nodes triggering an overflow "
plottingArray = np.zeros((fdim, rounds_displayed))
plottingArray_cr_EPN = np.zeros((num_Core*num_EPNLeaf*cap_Core_to_EPNLeaf, rounds_displayed))
plottingArray_FLP_cr = np.zeros((num_FLPLeaf*num_Core*cap_FLPLeaf_to_Core, rounds_displayed))

plottingArray_amounts = np.zeros(21)


##### --------------------------- MAPPING IN NETWORK ---------------------------

#Calculate EPN_Array
EPN_array = []

if(FindEPN == 1):
    x=0
    y=0
    for i in range(num_EPN):
        EPN_array.append(x)
        if x+54 < num_EPN:
            x += 54
        else:
            y+=1
            x=y

#Calculate EPNLeaf Array
EPNLeaf_array = []
x=0
for i in range(num_EPN):
    EPNLeaf_array.append(x)
    if(x>0 and x%4 == 0):
        x = 0
    else:
        x += 1


def calculateEPNs():
    chosenEPN = random.randint(0,755)
    if(len(EPN_array)>1):
        while(EPN[chosenEPN] != 0 or EPN_slots[chosenEPN]>2 or EPN_array[len(EPN_array)-1]==chosenEPN):
            chosenEPN = random.randint(0, 755)
    EPN_array.append(chosenEPN)


##### --------------------------- CREATE CANVAS FOR DRAWING FUNCTIONS ---------------------------

root = Tk()
canvas = Canvas(root, width=screenWidth, height=screenHeight, bg='white')
canvas.pack()


##### --------------------------- FUNCTIONS (CALCULATION) ---------------------------

def resetDevices():
    for i in range(num_FLP):
        FLP_send[i]=0
        FLP_to_FLPLeaf[i]=0
    for i in range(num_FLPLeaf):
        FLPLeaf[i]=0
    for i in range(num_Core):
        Core[i]=0
    for i in range(num_EPNLeaf):
        EPNLeaf[i]=0
    for i in range(num_EPN):
        EPNLeaf_to_EPN[i]=0
        EPN_ovf_involved[i]=0
        EPN_buffer_FLPLeaf_Core[i]=0
        EPN_buffer_Core_EPNLeaf[i]=0
    for i in range(num_FLPLeaf*num_Core*3):
        FLPLeaf_to_Core[i]=0
    for i in range(num_Core*num_EPNLeaf):
        Core_to_EPNLeaf[i]=0

def addSubTimes():
    for i in range(num_FLP):
        FLP[i].append(subTimeFrame_index)

def chooseSendingFLP():
    for i in range(num_FLP):
        if(num_send_frames != 3):
            if(sendFrame == int(num_FLP/num_send_frames)):
                FLP_send[i] = 1
            else:
                if i>=startIndex1 and i<startIndex1+sendFrame and (num_send_frames==1 or num_send_frames==2 or num_send_frames==4):
                    FLP_send[i]=1
                if i>=startIndex2 and i<startIndex2+sendFrame and num_send_frames==4:
                    FLP_send[i]=1
                if i>=startIndex3 and i<startIndex3+sendFrame and (num_send_frames==2 or num_send_frames==4):
                    FLP_send[i]=1
                if i>=startIndex4 and i<startIndex4+sendFrame and num_send_frames==4:
                    FLP_send[i]=1
        else:
            if (sendFrame == int(num_FLP/num_send_frames)):
                FLP_send[i] = 1
                if i == startIndex34:
                    FLP_send[i] = 0
            else:
                if i >= startIndex31 and i < startIndex31 + sendFrame:
                    FLP_send[i] = 1
                if i >= startIndex32 and i < startIndex32 + sendFrame:
                    FLP_send[i] = 1
                if i >= startIndex33 and i < startIndex33 + sendFrame:
                    FLP_send[i] = 1
                if i == startIndex34:
                    FLP_send[i] = 0

def findNodes():
    node_FLPLeaf=0
    node_Core=0
    node_EPNLeaf=0
    node_EPN = 0

    #check which FLPs are sending this round and then calculate their route
    for i in range(num_FLP):
        if FLP_send[i] == 1:

            #calculate which FLPLeaf-Node is used
            if i<40:
                FLPLeaf[0] += FLP_sending_rate
                node_FLPLeaf=0
            elif i>=40 and i<80:
                FLPLeaf[1] += FLP_sending_rate
                node_FLPLeaf=1
            elif i>=80 and i<120:
                FLPLeaf[2] += FLP_sending_rate
                node_FLPLeaf=2
            else:
                FLPLeaf[3] += FLP_sending_rate
                node_FLPLeaf=3

            #calculate depending on the value of the subtimeframe -> target EPN
            buffer = FLP[i]
            if(FindEPN == 0):
                node_EPN = EPN_array[buffer[0]]
            else:
                node_EPN = EPN_array[buffer[0] % 756]

            EPN[node_EPN] += FLP_sending_rate

            #calculate the EPNLeaf to connect to EPN
            if node_EPN<54:
                EPNLeaf[0] += FLP_sending_rate
                node_EPNLeaf=0
            elif node_EPN>=54 and node_EPN<54*2:
                EPNLeaf[1] += FLP_sending_rate
                node_EPNLeaf=1
            elif node_EPN>=54*2 and node_EPN<54*3:
                EPNLeaf[2] += FLP_sending_rate
                node_EPNLeaf=2
            elif node_EPN>=54*3 and node_EPN<54*4:
                EPNLeaf[3] += FLP_sending_rate
                node_EPNLeaf=3
            elif node_EPN>=54*4 and node_EPN<54*5:
                EPNLeaf[4] += FLP_sending_rate
                node_EPNLeaf=4
            elif node_EPN>=54*5 and node_EPN<54*6:
                EPNLeaf[5] += FLP_sending_rate
                node_EPNLeaf=5
            elif node_EPN>=54*6 and node_EPN<54*7:
                EPNLeaf[6] += FLP_sending_rate
                node_EPNLeaf=6
            elif node_EPN>=54*7 and node_EPN<54*8:
                EPNLeaf[7] += FLP_sending_rate
                node_EPNLeaf=7
            elif node_EPN>=54*8 and node_EPN<54*9:
                EPNLeaf[8] += FLP_sending_rate
                node_EPNLeaf=8
            elif node_EPN>=54*9 and node_EPN<54*10:
                EPNLeaf[9] += FLP_sending_rate
                node_EPNLeaf=9
            elif node_EPN>=54*10 and node_EPN<54*11:
                EPNLeaf[10] += FLP_sending_rate
                node_EPNLeaf=10
            elif node_EPN>=54*11 and node_EPN<54*12:
                EPNLeaf[11] += FLP_sending_rate
                node_EPNLeaf=11
            elif node_EPN>=54*12 and node_EPN<54*13:
                EPNLeaf[12] += FLP_sending_rate
                node_EPNLeaf=12
            else:
                EPNLeaf[13] += FLP_sending_rate
                node_EPNLeaf=13

            #calculate the Core to connect between EPNLeaf and FLPLeaf
            if FindCore==1:
                node_Core = EPNLeaf_array[node_EPN]
            else:
                node_Core = random.randint(0, 4)
            Core[node_Core] += FLP_sending_rate

            #calculate the links between the chosen Switches
            FLP_to_FLPLeaf[i] += FLP_sending_rate
            FLPLeaf_to_Core[node_FLPLeaf     *     num_Core *3    +       node_Core*3    +node_EPN%3] += FLP_sending_rate
            Core_to_EPNLeaf[node_Core*num_EPNLeaf+node_EPNLeaf] += FLP_sending_rate
            EPNLeaf_to_EPN[node_EPN] += FLP_sending_rate

            #calculate EPN-Paths
            EPN_buffer_FLPLeaf_Core[node_EPN]=node_FLPLeaf * num_Core *3 + node_Core*3 + node_EPN%3
            EPN_buffer_Core_EPNLeaf[node_EPN]=node_Core*num_EPNLeaf+node_EPNLeaf

            #calculate the total throughput in a simulation
            FLP_to_FLPLeaf_total[i] += FLP_sending_rate
            FLPLeaf_to_Core_total[node_FLPLeaf * num_Core + node_Core] += FLP_sending_rate
            Core_to_EPNLeaf_total[node_Core * num_EPNLeaf + node_EPNLeaf] += FLP_sending_rate
            EPNLeaf_to_EPN_total[node_EPN] += FLP_sending_rate

    #calculate if EPN is inactive, loading timeframe or processing timeframe
    for i in range(num_EPN):
        counter = 0
        if(EPN[i]>=160*FLP_sending_rate):
            EPN[i] = 0
            processing_time = 0
            randInt = random.randint(0,99)
            if(randInt<63):
                processing_time=30
            elif(randInt>=63 and randInt<86):
                processing_time=31
            elif(randInt>=86 and randInt<94):
                processing_time=32
            elif(randInt>=94 and randInt<97):
                processing_time=33
            elif(randInt>=97 and randInt<99):
                processing_time=34
            else:
                processing_time=35
            if (EPN_process[i][0] == 0):
                EPN_process[i][0] += processing_time*40
            else:
                if(EPN_process[i][1] == 0):
                    EPN_process[i][1] += processing_time*40
                else:
                    if (EPN_process[i][2] == 0):
                        EPN_process[i][2] += processing_time*40

        for j in range(3):
            if EPN_process[i][j]>0:
                EPN_process[i][j] -= 1
                counter += 1
        EPN_slots[i] = counter


def deleteSubsFromFLPs():
    for i in range(num_FLP):
        if FLP_send[i] == 1:
            FLP[i].pop(0)


##### --------------------------- FUNCTIONS (DRAWING) ---------------------------

#draw devices (switches)
def drawDevices():
    for i in range(num_FLP):
        color=''
        if FLP_send[i] == 1:
            color='black'
        canvas.create_rectangle(10, i*size_FLP+10, size_FLP+10, i*size_FLP+size_FLP+10, fill=color)

    for i in range(num_FLPLeaf):
        color = ''
        if FLPLeaf[i] >= 25 and FLPLeaf[i] <= 600:
            color='lime green'
        elif FLPLeaf[i] > 600 and FLPLeaf[i] <= 600*5:
            color='yellow'
        elif FLPLeaf[i] > 600*5:
            color='red'
        canvas.create_rectangle(200, i*size_FLPLeaf*2+(10+size_FLPLeaf/2), size_FLPLeaf/2+200, i*size_FLPLeaf*2+size_FLPLeaf+(10+size_FLPLeaf/2), fill=color)

    for i in range(num_Core):
        color = ''
        if Core[i] >= 25 and Core[i] <= 200:
            color = 'lime green'
        elif Core[i] > 200 and Core[i] <= 200*14:
            color = 'yellow'
        elif Core[i] > 200*14:
            color = 'red'
        canvas.create_rectangle(450, i*size_Core*2+(10+size_Core/2), size_Core/2+450, i*size_Core*2+size_Core+(10+size_Core/2), fill=color)

    for i in range(num_EPNLeaf):
        color = ''
        if EPNLeaf[i] >= 25 and EPNLeaf[i] <= 2700:
            color = 'lime green'
        elif EPNLeaf[i] > 2700 and EPNLeaf[i] <= 5400:
            color = 'yellow'
        elif EPNLeaf[i] > 5400:
            color = 'red'
        canvas.create_rectangle(750, i*size_EPNLeaf*2+(10+size_EPNLeaf/2), size_EPNLeaf/2+750, i*size_EPNLeaf*2+size_EPNLeaf+(10+size_EPNLeaf/2), fill=color)

    for i in range(int(num_EPN / EPN_per_row)):
        for j in range(EPN_per_row):
            color = ''
            border_color = 'black'
            border_line = 1
            if (EPN_slots[i * EPN_per_row + j] == 1):
                color = 'yellow'
            elif (EPN_slots[i * EPN_per_row + j] == 2):
                color = 'orange'
            elif EPN_slots[i * EPN_per_row + j] == 3:
                color = 'red'

            if EPN[i * EPN_per_row + j] >= 25 and EPN[i * EPN_per_row + j] <= 160 * FLP_sending_rate:
                border_color = 'lime green'
                border_line = 3
            canvas.create_rectangle(850 + j * 2 * size_EPN, i * size_EPN * 2 + 10, 850 + j * 2 * size_EPN + size_EPN,
                                    i * size_EPN * 2 + 10 + size_EPN, fill=color, outline=border_color,
                                    width=border_line)

#draw connections (links)
def drawConnections():
    for i in range(num_FLPLeaf):
        for j in range(int(num_FLP/num_FLPLeaf)):
            color = 'black'
            lineWeight = 1
            if FLP_to_FLPLeaf[i*int(num_FLP/num_FLPLeaf) +j] >= 25 and FLP_to_FLPLeaf[i*int(num_FLP/num_FLPLeaf) +j] <= 100:
                color = 'lime green'
                lineWeight = 1
            elif FLP_to_FLPLeaf[i*int(num_FLP/num_FLPLeaf) +j] > 100 and FLP_to_FLPLeaf[i*int(num_FLP/num_FLPLeaf) +j] <= 200:
                color = 'yellow'
                lineWeight = 5
            elif FLP_to_FLPLeaf[i*int(num_FLP/num_FLPLeaf) +j] > 200:
                color = 'red'
                lineWeight = 5
            canvas.create_line(size_FLP+10, (i*(num_FLP/num_FLPLeaf)+j)*size_FLP+(size_FLP/2)+10, 200, i*size_FLPLeaf*2+(10+size_FLPLeaf/2)+size_FLPLeaf/2, fill=color, width=lineWeight)

    for i in range(num_FLPLeaf):
        for j in range(num_Core):
            color = 'black'
            lineWeight = 1
            if FLPLeaf_to_Core[i*num_Core*3+j*3] >= 25 or FLPLeaf_to_Core[i*num_Core*3+j*3+1] >= 25 or FLPLeaf_to_Core[i*num_Core*3+j*3+2] >= 25:
                color = 'lime green'
                lineWeight = 3
            if FLPLeaf_to_Core[i*num_Core*3+j*3] > 200/2 or FLPLeaf_to_Core[i*num_Core*3+j*3+1] > 200/2 or FLPLeaf_to_Core[i*num_Core*3+j*3+1] > 200/2:
                color = 'yellow'
                lineWeight = 3
            if FLPLeaf_to_Core[i*num_Core*3+j*3] > 200 or FLPLeaf_to_Core[i*num_Core*3+j*3+1] > 200 or FLPLeaf_to_Core[i*num_Core*3+j*3+2] > 200:
                color = 'red'
                lineWeight = 3
                global overflow_rounds_FLPLeaf_Core
                overflow_rounds_FLPLeaf_Core[round] = 1
            canvas.create_line(size_FLPLeaf/2+200, i*size_FLPLeaf*2+(10+size_FLPLeaf/2)+size_FLPLeaf/2, 450, j*size_Core*2+(10+size_Core/2)+size_Core/2, fill=color, width=lineWeight)

    for i in range(num_Core):
        for j in range(num_EPNLeaf):
            color = 'black'
            lineWeight = 1
            if Core_to_EPNLeaf[i * num_EPNLeaf + j] >= 25 and Core_to_EPNLeaf[i * num_EPNLeaf + j] <= 1*200/2:
                color = 'lime green'
                lineWeight = 3
            elif Core_to_EPNLeaf[i * num_EPNLeaf + j] > 1*200/2 and Core_to_EPNLeaf[i * num_EPNLeaf + j] <= 1*200:
                color = 'yellow'
                lineWeight = 3
            elif Core_to_EPNLeaf[i * num_EPNLeaf + j] > 1*200:
                color = 'red'
                lineWeight = 3
                global overflow_rounds_Core_EPNLeaf
                overflow_rounds_Core_EPNLeaf[round] = 1
            canvas.create_line(size_Core/2+450, i*size_Core*2+(10+size_Core/2)+size_Core/2, 750, j*size_EPNLeaf*2+(10+size_EPNLeaf/2)+size_EPNLeaf/2, fill=color, width=lineWeight)

    for i in range(num_EPNLeaf):
        for j in range(int(num_EPN/num_EPNLeaf)):
            color = ''
            lineWeight = 1
            if EPNLeaf_to_EPN[i * int(num_EPN/num_EPNLeaf) + j] > 0 and EPNLeaf_to_EPN[i * int(num_EPN/num_EPNLeaf) + j] <= 50:
                color = 'lime green'
                lineWeight = 2
            elif EPNLeaf_to_EPN[i * int(num_EPN/num_EPNLeaf) + j] > 50 and EPNLeaf_to_EPN[i * int(num_EPN/num_EPNLeaf) + j] <= 100:
                color = 'yellow'
                lineWeight = 2
            elif EPNLeaf_to_EPN[i * int(num_EPN/num_EPNLeaf) + j] > 100:
                color = 'red'
                lineWeight = 2
                global overflow_rounds_EPNLeaf_EPN
                overflow_rounds_EPNLeaf_EPN[round] = 1
                print(EPN_array)
            canvas.create_line(size_EPNLeaf/2+750, i*size_EPNLeaf*2+size_EPNLeaf/2+(10+size_EPNLeaf/2), 850+((i*int(num_EPN/num_EPNLeaf)+j)%EPN_per_row)*2*size_EPN, math.floor((i*int(num_EPN/num_EPNLeaf)+j)/EPN_per_row)*size_EPN*2 + size_EPN/2+10, fill=color, width=lineWeight)


##### --------------------------- RUNNING NETWORK ---------------------------

for i in range(rounds_displayed):
    #reset all switches and links for every round
    resetDevices()

    #If random EPN Choosing
    if FindEPN == 0:
        calculateEPNs()

    #add the new subtimes to the FLP twodimensional array
    addSubTimes()

    #calculate sliding sending_frame
    chooseSendingFLP()

    #calculate the connection from FLP to EPN
    findNodes()

    #pop sent subtimeframes from FLP-array
    deleteSubsFromFLPs()


    #calculate new position of the sending frame
    subTimeFrame_index += 1
    if sendFrame<int(num_FLP/num_send_frames):
        sendFrame += 1
    else:
        if startIndex1==159:
            startIndex1=0
        else:
            startIndex1+=1

        if startIndex2==159:
            startIndex2=0
        else:
            startIndex2+=1

        if startIndex3==159:
            startIndex3=0
        else:
            startIndex3+=1

        if startIndex4==159:
            startIndex4=0
        else:
            startIndex4+=1

        if startIndex31==159:
            startIndex31=0
        else:
            startIndex31+=1

        if startIndex32==159:
            startIndex32=0
        else:
            startIndex32+=1

        if startIndex33==159:
            startIndex33=0
        else:
            startIndex33+=1

        if startIndex34==159:
            startIndex34=0
        else:
            startIndex34+=1

    #Calculate plotting array
    if(plottingMode==1):
        for j in range(num_FLPLeaf * num_Core * cap_FLPLeaf_to_Core):
            plottingArray[j,i] = FLPLeaf_to_Core[j]
    if(plottingMode==2):
        for j in range(num_Core * num_EPNLeaf * cap_Core_to_EPNLeaf):
            plottingArray[j,i] = Core_to_EPNLeaf[j]
    if(plottingMode==3):
        for j in range(num_EPN):
            plottingArray[j, i] = EPN[j]
    if(plottingMode==4):
        for x in range(len(FLPLeaf_to_Core)):
            if FLPLeaf_to_Core[x]>200:
                for y in range(len(EPN_buffer_FLPLeaf_Core)):
                    if(EPN_buffer_FLPLeaf_Core[y] == x):
                        EPN_ovf_involved[y] = EPN[y]

        for x in range(len(Core_to_EPNLeaf)):
            if Core_to_EPNLeaf[x]>200:
                for y in range(len(EPN_buffer_Core_EPNLeaf)):
                    if(EPN_buffer_Core_EPNLeaf[y] == x):
                        EPN_ovf_involved[y] = EPN[y]

        for j in range(num_EPN):
            plottingArray[j, i] = EPN_ovf_involved[j]

        for j in range(num_Core * num_EPNLeaf * cap_Core_to_EPNLeaf):
            plottingArray_cr_EPN[j, i] = Core_to_EPNLeaf[j]

        for j in range(num_FLPLeaf * num_Core * cap_FLPLeaf_to_Core):
            plottingArray_FLP_cr[j, i] = FLPLeaf_to_Core[j]

    for j in range(len(Core_to_EPNLeaf)):
        plottingArray_amounts[int(Core_to_EPNLeaf[j]/25)] += 1


    #draw the calculated variables
    drawDevices()
    drawConnections()
    root.update()
    if(speed > 0):
        time.sleep(speed)
    canvas.delete(ALL)

    round += 1


##### --------------------------- DEBUGGING AND CALCULATIONS (after simulation is finished) ---------------------------

print(plottingArray_amounts)

if(plottingMode>0):

    #adjust the plotting array if onlyOverflow is chosen
    if(onlyOverflow==1):
        for i in range(rounds_displayed):
            if(overflow_rounds_FLPLeaf_Core[i]==1 or overflow_rounds_Core_EPNLeaf[i]==1 or overflow_rounds_EPNLeaf_EPN[i]==1):
                overflow_rounds_total.append(i)
    plottingArray_overflow = np.zeros((fdim, len(overflow_rounds_total)))
    if(onlyOverflow==1):
        count = 0
        for i in range(len(plottingArray)):
            plottingArray_overflow[i] = np.take(plottingArray[i], overflow_rounds_total)

    #Adjust plottingArrays
    with np.nditer(plottingArray, op_flags=['readwrite']) as it:
        for x in it:
            if x>0:
                x[...] = 1

    with np.nditer(plottingArray_cr_EPN, op_flags=['readwrite']) as it:
        for x in it:
            if x<200:
                x[...] = 0

    with np.nditer(plottingArray_FLP_cr, op_flags=['readwrite']) as it:
        for x in it:
            if x<200:
                x[...] = 0


    #show the plot after the simulation is finished
    fig, ax = plt.subplots()
    if(onlyOverflow==1):
        im = ax.imshow(plottingArray_overflow)
    else:
        im = ax.imshow(plottingArray)

    ax.set_yticks([0,54,108,162,216,270,324,378,432,486,540,594,648,702,756])
    ax.set_yticklabels([0,54,108,162,216,270,324,378,432,486,540,594,648,702,756])

    ax.set_title(plotName + "| for " + str(rounds_displayed) + " rounds.")
    fig.tight_layout()
    cmap = plt.get_cmap('Blues')
    plt.imshow(plottingArray, interpolation='none', cmap=cmap)
    #plt.colorbar()

    plt.show()

    #Plot for Connections between Core and EPNLeafs
    fig2, ax2 = plt.subplots()
    ax2.set_title("Connections Core to EPNLeaf")
    im2 = ax2.imshow(plottingArray_cr_EPN)
    fig2.tight_layout()
    cmap2 = plt.get_cmap('Blues')
    plt.imshow(plottingArray_cr_EPN, interpolation='none', cmap=cmap2)
    #plt.colorbar()

    plt.show()

    #Plot for Connections between FLPLeafs and Core
    fig3, ax3 = plt.subplots()
    ax3.set_title("Connections FLPLeaf to Core")
    im3 = ax3.imshow(plottingArray_FLP_cr)
    fig3.tight_layout()
    cmap3 = plt.get_cmap('Blues')
    plt.imshow(plottingArray_FLP_cr, interpolation='none', cmap=cmap3)
    #plt.colorbar()

    plt.show()


    #Plot for histogram
    N = len(plottingArray_amounts)
    x = [0,25,50,75,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500]
    width = 20
    plt.bar(x, plottingArray_amounts, width, color="blue")
    plt.show()