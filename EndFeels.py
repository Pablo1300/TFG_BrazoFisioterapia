from Utils import *
from time import sleep
from array import array

def endFeelDuro(portHandler, packetHandler, id, angle, activo):
    angleAdapted = adaptAngleToId(id, angle)
    defaultPosByID = getDefaultPosById(id)
    actualDirection = UP
    dirArray = array("i")
    directionFlag = 0

    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id) and defaultPosByID != 0):
        if (activo): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
        else: 
            torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
            way = calculateWay(angleAdapted, defaultPosByID)
            comparator = (lambda x, y: x > y) if way == POS else (lambda x, y: x < y)
            dxl_previous_position = None

        isFinished = False
        while not isFinished:
            if activo:
                isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)
            else:
                dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
                print(dxl_present_position)

                if (dxl_present_position != None and dxl_previous_position != None):
                    dirArray.append(calculateDirection(dxl_present_position, dxl_previous_position, actualDirection))
                    if (directionFlag == 2): 
                        if(dirArray[0] == dirArray[1] == dirArray[2] == UP): actualDirection = UP
                        elif(dirArray[0] == dirArray[1] == dirArray[2] == DOWN): actualDirection = DOWN
                        dirArray = array("i")
                        directionFlag = 0
                    else: directionFlag += 1

                    if (comparator(rawToAngle(dxl_present_position), angleAdapted)): 
                        if(actualDirection == UP * way): 
                            torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                        else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
                    else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

                dxl_previous_position = dxl_present_position
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
        
        if activo: 
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)


            
def endFeelBlando(portHandler, packetHandler, id, angle, activo):
    angleAdapted = adaptAngleToId(id, angle)
    defaultPosByID = getDefaultPosById(id)

    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id) and defaultPosByID != 0):   
        # 171 equivale a 10 grados en raw
        # Se usan las medidas en raw para que no haya errores de inexactitud por los grados
        # Si la posicion final es menor que la posicion inicial, se suman los correspondientes grados a la final para simular el end feel blando
        # Si la posicion final es mayor que la posicion inicial, se restan los correspondientes grados a la final para simular el end feel blando
        way = calculateWay(angleAdapted, defaultPosByID)
        if (way == NEG): posEndFeelBlando = angleToRaw(angleAdapted) + 171
        elif ( way == POS): posEndFeelBlando = angleToRaw(angleAdapted) - 171

        if (activo): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
        else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

        isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
        while not isFinished:  
            if (not activo):
                comparator = (lambda x, y: x >= y) if way == POS else (lambda x, y: x <= y)
                dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
                if (comparator(dxl_present_position, posEndFeelBlando)): 
                    print("ENTRO")
                    torqueLimitControl(id, portHandler, packetHandler, 20)
                    torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
            isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)

        speedControl(id, portHandler, packetHandler, 50)
        torqueLimitControl(id, portHandler, packetHandler, 150)
        moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posEndFeelBlando))
        isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posEndFeelBlando), DXL_MOVING_STATUS_THRESHOLD)
        while not isFinished:
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posEndFeelBlando), DXL_MOVING_STATUS_THRESHOLD)

        speedControl(id, portHandler, packetHandler, SPEED_DEFAULT)
        torqueLimitControl(id, portHandler, packetHandler, MAX_TORQUE_LIMIT)

        if (activo): 
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
        else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

###
###
###
###
#### TEEERRRRRMIIIIIINNNNAAAAAAARRRRR
###
###
###
###
def endFeelBlando2(portHandler, packetHandler, id, angle, isActive):
    angleAdapted = adaptAngleToId(id, angle)
    defaultPosByID = getDefaultPosById(id)
    actualDirection = UP
    dirArray = array("i")
    directionFlag = 0

    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id) and defaultPosByID != 0):
        # 171 equivale a 10 grados en raw
        # Se usan las medidas en raw para que no haya errores de inexactitud por los grados
        # Si la posicion final es menor que la posicion inicial, se suman los correspondientes grados a la final para simular el end feel blando
        # Si la posicion final es mayor que la posicion inicial, se restan los correspondientes grados a la final para simular el end feel blando
        way = calculateWay(angleAdapted, defaultPosByID)
        if (way == NEG): posEndFeelBlando = angleToRaw(angleAdapted) + 171
        elif ( way == POS): posEndFeelBlando = angleToRaw(angleAdapted) - 171
        
        comparator = (lambda x, y: x >= y) if way == POS else (lambda x, y: x <= y)

        if (isActive): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
        else: 
            torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
            dxl_previous_position = None

        isFinished = False
        while not isFinished:
            dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
            if (dxl_present_position != None):
                if (not isActive and dxl_previous_position != None):
                    dirArray.append(calculateDirection(dxl_present_position, dxl_previous_position, actualDirection))
                    if (directionFlag == 2): 
                        if(dirArray[0] == dirArray[1] == dirArray[2] == UP): actualDirection = UP
                        elif(dirArray[0] == dirArray[1] == dirArray[2] == DOWN): actualDirection = DOWN
                        dirArray = array("i")
                        directionFlag = 0
                    else: directionFlag += 1

                if (comparator(dxl_present_position, posEndFeelBlando)):
                    if(isActive): 
                        speedControl(id, portHandler, packetHandler, 75)
                    else:
                        if (not comparator(rawToAngle(dxl_present_position), angleAdapted)): 
                            limitRangeFlag = 0
                            if(actualDirection == UP * way): 
                                torqueLimitControl(id, portHandler, packetHandler, 20)
                                torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                        else: 
                            if (limitRangeFlag == 0):
                                torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
                                limitRangeFlag += 1
                            if (actualDirection == DOWN * way):
                                speedControl(id, portHandler, packetHandler, 50)
                                torqueLimitControl(id, portHandler, packetHandler, 170)
                                moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posEndFeelBlando))
                            torqueLimitControl(id, portHandler, packetHandler, MAX_TORQUE_LIMIT)
                            torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                else: 
                    if(not isActive): torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

            if (isActive):
                isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            else:
                dxl_previous_position = dxl_present_position
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            
        if (isActive):
            speedControl(id, portHandler, packetHandler, 50)
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posEndFeelBlando))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posEndFeelBlando), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posEndFeelBlando), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            
            speedControl(id, portHandler, packetHandler, SPEED_DEFAULT)
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)


def endFeelSemiRig(portHandler, packetHandler, id, angle, isActive):
    angleAdapted = adaptAngleToId(id, angle)
    defaultPosByID = getDefaultPosById(id)
    endFeelPoints = array("i")
    mults = array("f", [0.75, 0.8, 0.85, 0.9, 0.95])

    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id) and defaultPosByID != 0):   
        for i in range(5): endFeelPoints.append(int(defaultPosByID + mults[i] * (angleToRaw(angleAdapted) - defaultPosByID)))
        endFeelPoints.append(angleToRaw(angleAdapted))
            
        if (isActive): 
            speedsEndFeel = array("i", [70, 57, 44, 31, 18, 5]) 
            moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(endFeelPoints[0]), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(endFeelPoints[0]), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
        else : 
            percentsTorque = array("f", [0.15, 0.25, 0.5, 0.75, 1])

        way = calculateWay(angleAdapted, defaultPosByID)

        comparator1 = (lambda x, y: x < y) if way == POS else (lambda x, y: x > y)
        comparator2 = (lambda x, y: x <= y) if way == POS else (lambda x, y: x >= y)

        isFinished = False
        while not isFinished:
            dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
            
            if (dxl_present_position != None):
                if(comparator1(dxl_present_position, endFeelPoints[0])): 
                    if(isActive): speedControl(id, portHandler, packetHandler, speedsEndFeel[0])
                    else: 
                        torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

                for i in range(5):
                    if(comparator2(endFeelPoints[i], dxl_present_position) and comparator1(dxl_present_position, endFeelPoints[i+1])): 
                        if (isActive): speedControl(id, portHandler, packetHandler, speedsEndFeel[i+1])
                        else:
                            if (i == 0): torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                            torqueLimitControl(id, portHandler, packetHandler, int(MAX_TORQUE_LIMIT_ENDFEEL * percentsTorque[i]))
                            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, ADDR_MX_GOAL_POSITION)
                            print(dxl_present_position)
                            print(int(MAX_TORQUE_LIMIT_ENDFEEL * percentsTorque[i]))
                        break
                
                if (comparator2(endFeelPoints[5], dxl_present_position)): 
                    if (not isActive): 
                        moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
                        torqueLimitControl(id, portHandler, packetHandler, 800)

            if (isActive):
                isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            else:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
        
        if (isActive):
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
            speedControl(id, portHandler, packetHandler, SPEED_DEFAULT)
            torqueLimitControl(id, portHandler, packetHandler, MAX_TORQUE_LIMIT)

            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)