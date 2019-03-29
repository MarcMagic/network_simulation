from tkinter import *
import math
import time
import random


##### --------------------------- VARIABLES ---------------------------

#important constants
screenWidth = 1280
screenHeight = 720

num_FLP = 160
num_HDR = 4
num_Core = 5
num_EPNSwitch = 14
num_EPN = 756
EPN_per_row = 18

cap_FLP_to_HDR = 1
cap_HDR_to_Core = 8
cap_Core_to_EPNSwitch = 2
cap_EPNSWitch_to_EPN = 1

size_FLP = (screenHeight-20)/num_FLP
size_HDR = (screenHeight-20)/num_HDR/2
size_Core = (screenHeight-20)/num_Core/2
size_EPNSwitch = (screenHeight-20)/num_EPNSwitch/2
size_EPN = (screenHeight-20)/num_EPN*EPN_per_row/2

#every second is one round
round = 1

#variables for sliding sending_frame
subTimeFrame_index = 0
sendFrame = 0
startIndex1 = 0
startIndex2 = 40
startIndex3 = 80
startIndex4 = 120

#counts overflow_errors
overflow_HDR_Core = 0
overflow_Core_EPNSwitch = 0
overflow_EPNSwitch_EPN = 0


###### --------------------------- SWITCHES AND LINKS ---------------------------

#Initialize devices/switches
FLP = [] #two-dimensional array contains subtimeframes as numbers
FLP_send = [] #contains values if FLP is sending
HDR = []
Core = []
EPNSwitch = []
EPN = []

for i in range(num_FLP):
    FLP.append([])
    FLP_send.append(0)
for i in range(num_HDR):
    HDR.append(0)
for i in range(num_Core):
    Core.append(0)
for i in range(num_EPNSwitch):
    EPNSwitch.append(0)
for i in range(num_EPN):
    EPN.append(0)

#Initialize connections between devices/switches
FLP_to_HDR = []
for i in range(num_FLP):
    FLP_to_HDR.append(0)

HDR_to_Core = []
for i in range(num_HDR*num_Core):
    HDR_to_Core.append(0)

Core_to_EPNSwitch = []
for i in range(num_Core*num_EPNSwitch):
    Core_to_EPNSwitch.append(0)

EPNSwitch_to_EPN = []
for i in range(num_EPN):
    EPNSwitch_to_EPN.append(0)

#following arrays count the total usage
FLP_to_HDR_total = []
for i in range(num_FLP):
    FLP_to_HDR_total.append(0)

HDR_to_Core_total = []
for i in range(num_HDR*num_Core):
    HDR_to_Core_total.append(0)

Core_to_EPNSwitch_total = []
for i in range(num_Core*num_EPNSwitch):
    Core_to_EPNSwitch_total.append(0)

EPNSwitch_to_EPN_total = []
for i in range(num_EPN):
    EPNSwitch_to_EPN_total.append(0)


##### --------------------------- MAPPING IN NETWORK ---------------------------

#Calculate EPN_Array
EPN_array = []
x=0
y=0
for i in range(num_EPN):
    EPN_array.append(x)
    if x+14 < num_EPN:
        x += 14
    else:
        y+=1
        x=y

#Calculate EPNwitch Array
EPNSwitch_array = []
x=0
for i in range(num_EPN):
    EPNSwitch_array.append(x)
    if(x>0 and x%4 == 0):
        x = 0
    else:
        x += 1


##### --------------------------- CREATE CANVAS FOR DRAWING FUNCTIONS ---------------------------

root = Tk()
canvas = Canvas(root, width=screenWidth, height=screenHeight, bg='white')
canvas.pack()


##### --------------------------- FUNCTIONS (CALCULATION) ---------------------------

def resetDevices():
    for i in range(num_FLP):
        FLP_send[i]=0
        FLP_to_HDR[i]=0
    for i in range(num_HDR):
        HDR[i]=0
    for i in range(num_Core):
        Core[i]=0
    for i in range(num_EPNSwitch):
        EPNSwitch[i]=0
    for i in range(num_EPN):
        EPNSwitch_to_EPN[i]=0
    for i in range(num_HDR*num_Core):
        HDR_to_Core[i]=0
    for i in range(num_Core*num_EPNSwitch):
        Core_to_EPNSwitch[i]=0

def addSubTimes():
    for i in range(num_FLP):
        FLP[i].append(subTimeFrame_index)

def chooseSendingFLP():
    for i in range(num_FLP):
        if(sendFrame == 40):
            FLP_send[i] = 1
        else:
            if i>=startIndex1 and i<startIndex1+sendFrame:
                FLP_send[i]=1
            if i>=startIndex2 and i<startIndex2+sendFrame:
                FLP_send[i]=1
            if i>=startIndex3 and i<startIndex3+sendFrame:
                FLP_send[i]=1
            if i>=startIndex4 and i<startIndex4+sendFrame:
                FLP_send[i]=1

def findNodes():
    node_HDR=0
    node_Core=0
    node_EPNSwitch=0
    node_EPN = 0

    #check which FLPs are sending this round and then calculate their route
    for i in range(num_FLP):
        if FLP_send[i] == 1:

            #calculate which HDR-Node is used
            if i<40:
                HDR[0] +=25
                node_HDR=0
            elif i>=40 and i<80:
                HDR[1] += 25
                node_HDR=1
            elif i>=80 and i<120:
                HDR[2] += 25
                node_HDR=2
            else:
                HDR[3] += 25
                node_HDR=3

            #calculate depending on the value of the subtimeframe -> target EPN
            buffer = FLP[i]
            node_EPN = EPN_array.index(buffer[0]%756)
            EPN[node_EPN] += 25

            #calculate the EPNSwitch to connect to EPN
            if node_EPN<54:
                EPNSwitch[0] += 25
                node_EPNSwitch=0
            elif node_EPN>=54 and node_EPN<54*2:
                EPNSwitch[1] += 25
                node_EPNSwitch=1
            elif node_EPN>=54*2 and node_EPN<54*3:
                EPNSwitch[2] += 25
                node_EPNSwitch=2
            elif node_EPN>=54*3 and node_EPN<54*4:
                EPNSwitch[3] += 25
                node_EPNSwitch=3
            elif node_EPN>=54*4 and node_EPN<54*5:
                EPNSwitch[4] += 25
                node_EPNSwitch=4
            elif node_EPN>=54*5 and node_EPN<54*6:
                EPNSwitch[5] += 25
                node_EPNSwitch=5
            elif node_EPN>=54*6 and node_EPN<54*7:
                EPNSwitch[6] += 25
                node_EPNSwitch=6
            elif node_EPN>=54*7 and node_EPN<54*8:
                EPNSwitch[7] += 25
                node_EPNSwitch=7
            elif node_EPN>=54*8 and node_EPN<54*9:
                EPNSwitch[8] += 25
                node_EPNSwitch=8
            elif node_EPN>=54*9 and node_EPN<54*10:
                EPNSwitch[9] += 25
                node_EPNSwitch=9
            elif node_EPN>=54*10 and node_EPN<54*11:
                EPNSwitch[10] += 25
                node_EPNSwitch=10
            elif node_EPN>=54*11 and node_EPN<54*12:
                EPNSwitch[11] += 25
                node_EPNSwitch=11
            elif node_EPN>=54*12 and node_EPN<54*13:
                EPNSwitch[12] += 25
                node_EPNSwitch=12
            else:
                EPNSwitch[13] += 25
                node_EPNSwitch=13

            #calculate the Core to connect between EPNSwitch and HDR
            node_Core = EPNSwitch_array[node_EPN]
            Core[node_Core] += 25

            #calculate the links between the chosen Switches
            FLP_to_HDR[i] += 25
            HDR_to_Core[node_HDR*num_Core+node_Core] += 25
            Core_to_EPNSwitch[node_Core*num_EPNSwitch+node_EPNSwitch] += 25
            EPNSwitch_to_EPN[node_EPN] += 25

            FLP_to_HDR_total[i] += 25
            HDR_to_Core_total[node_HDR * num_Core + node_Core] += 25
            Core_to_EPNSwitch_total[node_Core * num_EPNSwitch + node_EPNSwitch] += 25
            EPNSwitch_to_EPN_total[node_EPN] += 25

    #calculate if EPN is inactive, loading timeframe or processing timeframe
    for i in range(num_EPN):
        if(EPN[i]>=4000 and EPN[i]<4030):
            EPN[i] +=1
        elif(EPN[i]==4030):
            EPN[i] = 0

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

    for i in range(num_HDR):
        color = ''
        if HDR[i] >= 25 and HDR[i] <= 600:
            color='lime green'
        elif HDR[i] > 600 and HDR[i] <= 600*5:
            color='yellow'
        elif HDR[i] > 600*5:
            color='red'
        canvas.create_rectangle(200, i*size_HDR*2+(10+size_HDR/2), size_HDR/2+200, i*size_HDR*2+size_HDR+(10+size_HDR/2), fill=color)

    for i in range(num_Core):
        color = ''
        if Core[i] >= 25 and Core[i] <= 200:
            color = 'lime green'
        elif Core[i] > 200 and Core[i] <= 200*14:
            color = 'yellow'
        elif Core[i] > 200*14:
            color = 'red'
        canvas.create_rectangle(450, i*size_Core*2+(10+size_Core/2), size_Core/2+450, i*size_Core*2+size_Core+(10+size_Core/2), fill=color)

    for i in range(num_EPNSwitch):
        color = ''
        if EPNSwitch[i] >= 25 and EPNSwitch[i] <= 2700:
            color = 'lime green'
        elif EPNSwitch[i] > 2700 and EPNSwitch[i] <= 5400:
            color = 'yellow'
        elif EPNSwitch[i] > 5400:
            color = 'red'
        canvas.create_rectangle(750, i*size_EPNSwitch*2+(10+size_EPNSwitch/2), size_EPNSwitch/2+750, i*size_EPNSwitch*2+size_EPNSwitch+(10+size_EPNSwitch/2), fill=color)

    for i in range(int(num_EPN/EPN_per_row)):
        for j in range(EPN_per_row):
            color = ''
            if EPN[i*EPN_per_row+j] >= 25 and EPN[i*EPN_per_row+j] <= 4000:
                color = 'lime green'
            elif EPN[i*EPN_per_row+j] > 4000 and EPN[i*EPN_per_row+j] <= 4030:
                color = 'yellow'
            elif EPN[i*EPN_per_row+j] > 4030:
                color = 'red'
            canvas.create_rectangle(850+j*2*size_EPN,   i*size_EPN*2+10,   850+j*2*size_EPN+size_EPN, i*size_EPN*2+10+size_EPN, fill=color)

#draw connections (links)
def drawConnections():
    for i in range(num_HDR):
        for j in range(int(num_FLP/num_HDR)):
            color = 'black'
            lineWeight = 1
            if FLP_to_HDR[i*int(num_FLP/num_HDR) +j] >= 25 and FLP_to_HDR[i*int(num_FLP/num_HDR) +j] <= 100:
                color = 'lime green'
                lineWeight = 1
            elif FLP_to_HDR[i*int(num_FLP/num_HDR) +j] > 100 and FLP_to_HDR[i*int(num_FLP/num_HDR) +j] <= 200:
                color = 'yellow'
                lineWeight = 5
            elif FLP_to_HDR[i*int(num_FLP/num_HDR) +j] > 200:
                color = 'red'
                lineWeight = 5
            canvas.create_line(size_FLP+10, (i*(num_FLP/num_HDR)+j)*size_FLP+(size_FLP/2)+10, 200, i*size_HDR*2+(10+size_HDR/2)+size_HDR/2, fill=color, width=lineWeight)

    for i in range(num_HDR):
        for j in range(num_Core):
            color = 'black'
            lineWeight = 1
            if HDR_to_Core[i*num_Core+j] >= 25 and HDR_to_Core[i*num_Core+j] <= 3*200/2:
                color = 'lime green'
                lineWeight = 3
            elif HDR_to_Core[i*num_Core+j] > 3*200/2 and HDR_to_Core[i*num_Core+j] <= 3*200:
                color = 'yellow'
                lineWeight = 3
            elif HDR_to_Core[i*num_Core+j] > 3*200:
                color = 'red'
                lineWeight = 3
                print("HDR to Core Overflow in round " + str(round))
                global overflow_HDR_Core
                overflow_HDR_Core += 1
            canvas.create_line(size_HDR/2+200, i*size_HDR*2+(10+size_HDR/2)+size_HDR/2, 450, j*size_Core*2+(10+size_Core/2)+size_Core/2, fill=color, width=lineWeight)

    for i in range(num_Core):
        for j in range(num_EPNSwitch):
            color = 'black'
            lineWeight = 1
            if Core_to_EPNSwitch[i * num_EPNSwitch + j] >= 25 and Core_to_EPNSwitch[i * num_EPNSwitch + j] <= 1*200/2:
                color = 'lime green'
                lineWeight = 3
            elif Core_to_EPNSwitch[i * num_EPNSwitch + j] > 1*200/2 and Core_to_EPNSwitch[i * num_EPNSwitch + j] <= 1*200:
                color = 'yellow'
                lineWeight = 3
            elif Core_to_EPNSwitch[i * num_EPNSwitch + j] > 1*200:
                color = 'red'
                lineWeight = 3
                print("Core to EPNSwitch Overflow in round " + str(round))
                global overflow_Core_EPNSwitch
                overflow_Core_EPNSwitch += 1
            canvas.create_line(size_Core/2+450, i*size_Core*2+(10+size_Core/2)+size_Core/2, 750, j*size_EPNSwitch*2+(10+size_EPNSwitch/2)+size_EPNSwitch/2, fill=color, width=lineWeight)

    for i in range(num_EPNSwitch):
        for j in range(int(num_EPN/num_EPNSwitch)):
            color = 'black'
            lineWeight = 1
            if EPNSwitch_to_EPN[i * int(num_EPN/num_EPNSwitch) + j] == 25 or EPNSwitch_to_EPN[i * int(num_EPN/num_EPNSwitch) + j] == 50:
                color = 'lime green'
                lineWeight = 2
            elif EPNSwitch_to_EPN[i * int(num_EPN/num_EPNSwitch) + j] == 75 or EPNSwitch_to_EPN[i * int(num_EPN/num_EPNSwitch) + j] == 100:
                color = 'yellow'
                lineWeight = 2
            elif EPNSwitch_to_EPN[i * int(num_EPN/num_EPNSwitch) + j] > 100:
                color = 'red'
                lineWeight = 2
                print("EPNSwitch to EPN Overflow in round " + str(round))
                global overflow_EPNSwitch_EPN
                overflow_EPNSwitch_EPN += 1
            canvas.create_line(size_EPNSwitch/2+750, i*size_EPNSwitch*2+size_EPNSwitch/2+(10+size_EPNSwitch/2), 850+((i*int(num_EPN/num_EPNSwitch)+j)%EPN_per_row)*2*size_EPN, math.floor((i*int(num_EPN/num_EPNSwitch)+j)/EPN_per_row)*size_EPN*2 + size_EPN/2+10, fill=color, width=lineWeight)


##### --------------------------- RUNNING NETWORK ---------------------------

for i in range(10000):
    #reset all switches and links for every round
    resetDevices()

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
    if sendFrame<40:
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

    #draw the calculated variables
    drawDevices()
    drawConnections()
    root.update()

    time.sleep(0.1)
    canvas.delete(ALL)

    round += 1


##### --------------------------- DEBUGGING AND CALCULATIONS ---------------------------

print(FLP_to_HDR_total)
print(HDR_to_Core_total)
print(Core_to_EPNSwitch_total)
print(EPNSwitch_to_EPN_total)

print("Overflows in HDR to Core: " + str(overflow_HDR_Core))
print("overflows in Core to EPNSwitch: " + str(overflow_Core_EPNSwitch))
print("Overflows in EPNSwitch to EPN: " + str(overflow_EPNSwitch_EPN))