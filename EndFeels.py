from Utils import *
from time import sleep

def endFeelDuro(portHandler, packetHandler, id, angle, activo):
    angleAdapted = adaptAngleToId(id, angle)

    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id)):
        if (activo): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
        else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

        moveFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)
        while not moveFinished:
            moveFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)

        if(not activo): torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)

def endFeelBlando(portHandler, packetHandler, id, angle, activo):
    angleAdapted = adaptAngleToId(id, angle)

    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id)):
        posInicial = readPresentPosition(portHandler, packetHandler, id)
        if (activo): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
        else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

        moveFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)
        while not moveFinished:        
            moveFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)

        # 85 equivale a 7.5 grados en raw
        # Se usan las medidas en raw para que no haya errores de inexactitud por los grados
        # Si la posicion final es menor que la posicion inicial, se suman los correspondientes grados a la final para simular el end feel blando
        # Si la posicion final es mayor que la posicion inicial, se restan los correspondientes grados a la final para simular el end feel blando
        if (angleToRaw(angleAdapted) - posInicial < 0): angleBlando = (angleToRaw(angleAdapted) + 171)
        elif (angleToRaw(angleAdapted) - posInicial > 0): angleBlando = angleToRaw(angleAdapted) - 171

        speedControl(id, portHandler, packetHandler, 50)
        moveServoToAngle(id, portHandler, packetHandler, rawToAngle(angleBlando))
        moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(angleBlando), DXL_MOVING_STATUS_THRESHOLD_ESPAS)
        while not moveFinished:
            moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(angleBlando), DXL_MOVING_STATUS_THRESHOLD_ESPAS)

        speedControl(id, portHandler, packetHandler, 100)

        if (not activo):
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posInicial))
            torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
            moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posInicial), DXL_MOVING_STATUS_THRESHOLD)
            while not moveFinished:
                moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posInicial), DXL_MOVING_STATUS_THRESHOLD)


def endFeelSemiRig(portHandler, packetHandler, id, angle, activo):
    angleAdapted = adaptAngleToId(id, angle)
    mult = 0.75
    if (activo): firstSpeed = SPEED_DEFAULT - 30
    else: percentTorque = 0

    if not isinstance(angleAdapted, str):
        posInicial = readPresentPosition(portHandler, packetHandler, id)
        movementeRange = abs(angleToRaw(angleAdapted) - posInicial)
        if (movementeRange == 0): print("El brazo ya se encuentra en la posición indicada")
        else: 
            if (activo): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
            else : 
                torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
                torqueLimitControl(id, portHandler, packetHandler, 0)

            moveFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)
            while not moveFinished:
                dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
                actualRange = abs(dxl_present_position - posInicial)

                if (actualRange >= movementeRange * mult and actualRange < movementeRange * (mult + 0.05) and round(mult + 0.05, 2) <= 1):
                    if (actualRange >= movementeRange * 0.75 and mult == 0.75): 
                        angleEndFeel = rawToAngle(readPresentPosition(portHandler, packetHandler, id))
                        torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                    mult += 0.05
                    if (activo): 
                        firstSpeed -= 13
                        print(firstSpeed)
                        speedControl(id, portHandler, packetHandler, firstSpeed)
                    else: 
                        torqueLimitControl(id, portHandler, packetHandler, int(MAX_TORQUE_LIMIT_ENDFEEL * percentTorque))
                        dxl_torque_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, ADDR_MX_TORQUE_LIMIT)
                        percentTorque += 0.25
                        
                        if dxl_comm_result != COMM_SUCCESS:
                            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
                        elif dxl_error != 0:
                            print("%s" % packetHandler.getRxPacketError(dxl_error))
                        print(dxl_torque_position)

                moveFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)

            if (activo): 
                sleep(2)
                speedControl(id, portHandler, packetHandler, SPEED_DEFAULT)
                print(rawToAngle(posInicial))
                moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posInicial))
                moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posInicial), DXL_MOVING_STATUS_THRESHOLD)
                while not moveFinished:
                    moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posInicial), DXL_MOVING_STATUS_THRESHOLD)
            else: 
                torqueLimitControl(id, portHandler, packetHandler, 400)
                moveFinished = moveIsFinished(portHandler, packetHandler, id, angleEndFeel, DXL_MOVING_STATUS_THRESHOLD_ESPAS)
                while not moveFinished:
                    moveFinished = moveIsFinished(portHandler, packetHandler, id, angleEndFeel, DXL_MOVING_STATUS_THRESHOLD_ESPAS)

                torqueLimitControl(id, portHandler, packetHandler, 50)
                moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posInicial))
                moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posInicial), DXL_MOVING_STATUS_THRESHOLD)
                while not moveFinished:
                    moveFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posInicial), DXL_MOVING_STATUS_THRESHOLD)
                
    else: print(angleAdapted)