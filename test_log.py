#!/usr/bin/env python3

import sys
import time
import array
import cereal.messaging as messaging


arguments = len(sys.argv) - 1
position = 1
desktop_testing = False

print_info_slowdown = 128 # increase to reduce update frequency

class GlobalData:
    enabled = False
    valid   = False
    angleSteers  = 0.0
    angleSteersDes = 0.0
    speed = 0.0
    iStopCount = 0           # timeout if data is not valid for a long time
    iValidCount = 0
    iLastPrintCount = -1;
    aiBucket = array.array('l',[0,0,0,0,0,0,0,0,0,0, 0, 0,0,0,0,0,0,0,0,0,0])

gGlobalData = GlobalData()

def print_data_log ():
    sum_count = gGlobalData.aiBucket[0];
    print ( "Steer error < 1 = ", sum_count, "/", gGlobalData.iValidCount, "=",
            "{0:8.4f}".format ( (sum_count / gGlobalData.iValidCount)*100.0), "%" )

    sum_count = sum_count + gGlobalData.aiBucket[1] + gGlobalData.aiBucket[11];
    print ( "Steer error < 2 = ", sum_count, "/", gGlobalData.iValidCount, "=",
            "{0:8.4f}".format ( (sum_count / gGlobalData.iValidCount)*100.0), "%" )

    sum_count = sum_count + gGlobalData.aiBucket[2] + gGlobalData.aiBucket[12];
    print ( "Steer error < 3 = ", sum_count, "/", gGlobalData.iValidCount, "=",
            "{0:8.4f}".format ( (sum_count / gGlobalData.iValidCount)*100.0), "%" )
    largest_count = 0;
    for x in range(21):
        if (gGlobalData.aiBucket[x]>largest_count):
            largest_count = gGlobalData.aiBucket[x];
    for x in range(20, 10, -1):
        bar_string ="";
        for y in range (int((gGlobalData.aiBucket[x] / largest_count) * 30.0)):
            bar_string = bar_string + "*"
        print ("{0:3d}".format(10- x), ':', "{0:7d}".format(gGlobalData.aiBucket[x]), ':', bar_string)
    for x in range(0, 11):
        bar_string ="";
        for y in range(int((gGlobalData.aiBucket[x] / largest_count) * 30.0)):
            bar_string = bar_string + "*"
        print ( "{0:3d}".format(x), ':', "{0:7d}".format(gGlobalData.aiBucket[x]), ':', bar_string)

# prevent_overflow = div 2 everything to prevent overflow
def prevent_overflow ():
    if (gGlobalData.iValidCount <= 100000000):
        return  
    gGlobalData.iValidCount = 0;
    for x in range(21):
        gGlobalData.aiBucket[x] = gGlobalData.aiBucket[x] / 2;
        gGlobalData.iValidCount = gGlobalData.iValidCount + gGlobalData.aiBucket[x];
    return

while (arguments >= position):
    #print ("parameter %i: %s" % (position, sys.argv[position]))
    if (sys.argv[position] == "-TEST"):
        desktop_testing = True      
        print ("desktop_testing is enabled")
    position = position + 1

if (desktop_testing):
    import random
    # fake controlsState messaging data to check for runtime errors 
    class test_data_cs ():
        enabled = True
        angleSteers = 0.0
        angleSteersDes = 0.0
        vEgo = 0.0

    class test_data():
        valid = True;
        controlsState = test_data_cs();

    class fake_messaging():
        icallcount = 0
        def recv_one (self, soc):
            fake_messaging.icallcount = fake_messaging.icallcount + 1
            data = test_data()
            data.controlsState.angleSteers = random.random() * 11.0;
            data.controlsState.angleSteersDes = random.random() * 11.0;
            data.controlsState.vEgo  = random.random() * 60.0 + 10.0;
            if fake_messaging.icallcount > 10000:
                data.valid = random.random() > -0.01;
            time.sleep(0.001)
            return data

    messaging = fake_messaging()
    sm_socket = True
    sm = True
else:
    sm = messaging.SubMaster(['controlsState'])
    sm_socket = sm.sock['controlsState'];

while sm is not None:
    cs = messaging.recv_one(sm_socket);
    if cs is None:
        #exit if too many empty/invalid frames come in
        gGlobalData.iStopCount = gGlobalData.iStopCount + 1 
        if (gGlobalData.iStopCount%print_info_slowdown==0):
            print_data_log()
            print ( 'CS not ready. ', gGlobalData.iStopCount )
        time.sleep(0.1)
    else:
        gGlobalData.valid   = cs.valid
        gGlobalData.enabled = cs.controlsState.enabled
        gGlobalData.speed   = cs.controlsState.vEgo
        if (gGlobalData.valid and gGlobalData.enabled and (gGlobalData.speed > 10)):
            gGlobalData.iStopCount = 0
            gGlobalData.iValidCount = gGlobalData.iValidCount + 1
            gGlobalData.angleSteers = cs.controlsState.angleSteers
            gGlobalData.angleSteersDes = cs.controlsState.angleSteersDes
            data_diffSteer = gGlobalData.angleSteers - gGlobalData.angleSteersDes
            if (data_diffSteer > 0.0):
                if (data_diffSteer < 1.0):
                    gGlobalData.aiBucket[0] = gGlobalData.aiBucket[0] + 1
                elif (abs(data_diffSteer)< 2.0):
                    gGlobalData.aiBucket[1] = gGlobalData.aiBucket[1] + 1
                elif (abs(data_diffSteer)< 3.0):
                    gGlobalData.aiBucket[2] = gGlobalData.aiBucket[2] + 1
                elif (abs(data_diffSteer)< 4.0):
                    gGlobalData.aiBucket[3] = gGlobalData.aiBucket[3] + 1
                elif (abs(data_diffSteer)< 5.0):
                    gGlobalData.aiBucket[4] = gGlobalData.aiBucket[4] + 1
                elif (abs(data_diffSteer)< 6.0):
                    gGlobalData.aiBucket[5] = gGlobalData.aiBucket[5] + 1
                elif (abs(data_diffSteer)< 7.0):
                    gGlobalData.aiBucket[6] = gGlobalData.aiBucket[6] + 1
                elif (abs(data_diffSteer)< 8.0):
                    gGlobalData.aiBucket[7] = gGlobalData.aiBucket[7] + 1
                elif (abs(data_diffSteer)< 9.0):
                    gGlobalData.aiBucket[8] = gGlobalData.aiBucket[8] + 1
                elif (abs(data_diffSteer)< 10.0):
                    gGlobalData.aiBucket[9] = gGlobalData.aiBucket[9] + 1
                else:
                    gGlobalData.aiBucket[10] = gGlobalData.aiBucket[10] + 1
            else:
                if (data_diffSteer > -1.0):
                    gGlobalData.aiBucket[0] = gGlobalData.aiBucket[0] + 1
                elif (data_diffSteer > -2.0):
                    gGlobalData.aiBucket[11] = gGlobalData.aiBucket[11] + 1
                elif (data_diffSteer > -3.0):
                    gGlobalData.aiBucket[12] = gGlobalData.aiBucket[12] + 1
                elif (data_diffSteer > -4.0):
                    gGlobalData.aiBucket[13] = gGlobalData.aiBucket[13] + 1
                elif (data_diffSteer > -5.0):
                    gGlobalData.aiBucket[14] = gGlobalData.aiBucket[14] + 1
                elif (data_diffSteer > -6.0):
                    gGlobalData.aiBucket[15] = gGlobalData.aiBucket[15] + 1
                elif (data_diffSteer > -7.0):
                    gGlobalData.aiBucket[16] = gGlobalData.aiBucket[16] + 1
                elif (data_diffSteer > -8.0):
                    gGlobalData.aiBucket[17] = gGlobalData.aiBucket[17] + 1
                elif (data_diffSteer > -9.0):
                    gGlobalData.aiBucket[18] = gGlobalData.aiBucket[18] + 1
                elif (data_diffSteer > -10.0):
                    gGlobalData.aiBucket[19] = gGlobalData.aiBucket[19] + 1
                else:
                    gGlobalData.aiBucket[20] = gGlobalData.aiBucket[20] + 1
        else:
            if (gGlobalData.iStopCount%print_info_slowdown==0):
                print_data_log()
                print ( 'CS Ready, but Data not valid. ', gGlobalData.iStopCount, gGlobalData.valid, gGlobalData.enabled, gGlobalData.speed )
            gGlobalData.iStopCount = gGlobalData.iStopCount + 1
            time.sleep(0.1)
    if (gGlobalData.iValidCount%print_info_slowdown==0) and (gGlobalData.iStopCount == 0) and (gGlobalData.iLastPrintCount != gGlobalData.iValidCount):
        print ( 'CS Ready, Data Valid, Speed = ', gGlobalData.speed );
        gGlobalData.iLastPrintCount = gGlobalData.iValidCount;
        print_data_log()
        prevent_overflow()
    elif (gGlobalData.iStopCount > 1000000):
        break
    #end of while loop

print ("end of test_log.py")

# data from eon:
# ( logMonoTime = 1792979779158,
#   controlsState = (
#     vEgo = 0,
#     aEgoDEPRECATED = 0,
#     vPid = 0.3,
#     vTargetLead = 0,
#     upAccelCmd = 0,
#     uiAccelCmd = 0,
#     yActualDEPRECATED = 0,
#     yDesDEPRECATED = 0,
#     upSteerDEPRECATED = 0,
#     uiSteerDEPRECATED = 0,
#     aTargetMinDEPRECATED = 0,
#     aTargetMaxDEPRECATED = 0,
#     jerkFactor = 0,
#     angleSteers = -17.2,
#     hudLeadDEPRECATED = 0,
#     cumLagMs = 11.949181,
#     canMonoTimeDEPRECATED = 0,
#     radarStateMonoTimeDEPRECATED = 0,
#     mdMonoTimeDEPRECATED = 0,
#     enabled = false,
#     steerOverride = false,
#     canMonoTimes = [],
#     vCruise = 40,
#     rearViewCam = false,
#     alertText1 = "",
#     alertText2 = "",
#     awarenessStatus = 1,
#     angleModelBiasDEPRECATED = 0,
#     planMonoTime = 1792962097491,
#     angleSteersDes = 19.08531,
#     longControlState = off,
#     state = disabled,
#     vEgoRaw = 0,
#     ufAccelCmd = 0,
#     ufSteerDEPRECATED = 0,
#     aTarget = 0,
#     active = false,
#     curvature = -0.006738049,
#     alertStatus = normal,
#     alertSize = none,
#     gpsPlannerActive = false,
#     engageable = false,
#     alertBlinkingRate = 0,
#     driverMonitoringOn = false,
#     alertType = "",
#     vCurvature = 0,
#     decelForTurn = false,
#     startMonoTime = 1792969056346,
#     mapValid = false,
#     pathPlanMonoTime = 1792972112543,
#     forceDecel = false,
#     lateralControlState = (
#       pidState = (
#         active = false,
#         steerAngle = -17.2,
#         steerRate = 0,
#         angleError = 0,
#         p = 0,
#         i = 0,
#         f = 0,
#         output = 0,
#         saturated = false ) ),
#     decelForModel = false,
#     alertSound = none ),
#   valid = true )
