#!/usr/bin/env python3

import sys
import time
# import cereal.messaging as messaging

arguments = len(sys.argv) - 1
position = 1
desktop_testing = False

class GlobalData:
    enabled = False
    valid   = False
    angleSteers  = 0.0
    angleSteersDes = 0.0
    iStopCount = 0           # timeout if data is not valid for a long time
    iValidCount = 0
    iGoodCount = 0

gGlobalData = GlobalData()

def print_data_log ():
    print (gGlobalData.iGoodCount, "/", gGlobalData.iValidCount, "=",
          "{0:8.4f}".format ( (gGlobalData.iGoodCount / gGlobalData.iValidCount)*100.0), "%" )

def normalize_count ():
    if (gGlobalData.iValidCount <= 100000000) or (gGlobalData.iGoodCount <= 0):
        return  
    if (gGlobalData.iValidCount%2 != 0) or (gGlobalData.iGoodCount%2 != 0):
        return
    gGlobalData.iValidCount = gGlobalData.iValidCount / 2
    gGlobalData.iGoodCount  = gGlobalData.iGoodCount / 2
    return

while (arguments >= position):
    #print ("parameter %i: %s" % (position, sys.argv[position]))
    if (sys.argv[position] == "-TEST"):
        desktop_testing = True      
        print ("desktop_testing is enabled")
    else:
        import cereal.messaging as messaging
    position = position + 1

if (desktop_testing):
    import random
    # fake controlsState messaging data to check for runtime errors 
    class test_data_cs ():
        enabled = True
        angleSteers = 0.0
        angleSteersDes = 0.0

    class test_data():
        valid = True;
        controlsState = test_data_cs();

    class fake_messaging():
        icallcount = 0
        def recv_one (self, soc):
            fake_messaging.icallcount = fake_messaging.icallcount + 1
            data = test_data()
            data.controlsState.angleSteers = random.random() * 5.0;
            data.controlsState.angleSteersDes = random.random() * 5.0;
            if fake_messaging.icallcount > 1000:
                data.valid = False;
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
        print ( 'CS not ready. ', gGlobalData.iStopCount )
        time.sleep(0.1)
    else:
        gGlobalData.valid   = cs.valid
        gGlobalData.enabled = cs.controlsState.enabled
        if (gGlobalData.valid and gGlobalData.enabled):
            gGlobalData.iStopCount = 0
            gGlobalData.iValidCount = gGlobalData.iValidCount + 1
            gGlobalData.angleSteers = cs.controlsState.angleSteers
            gGlobalData.angleSteersDes = cs.controlsState.angleSteersDes
            data_diffSteer = gGlobalData.angleSteers - gGlobalData.angleSteersDes
            if (abs(data_diffSteer)<= 3):
                gGlobalData.iGoodCount = gGlobalData.iGoodCount + 1
            print_data_log()
            normalize_count()
        else:
            print ( 'CS Ready, but Data not valid. ', gGlobalData.iStopCount )
            gGlobalData.iStopCount = gGlobalData.iStopCount + 1
            time.sleep(0.1)
    if (gGlobalData.iStopCount > 9000):
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
