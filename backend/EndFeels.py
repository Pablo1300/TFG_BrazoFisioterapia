from Utils import *
from array import array
from time import sleep

# Funcion para simular end feel duros
def endFeelDuro(portHandler, packetHandler, id, angle, activo):
    # Inicializacion de variables necesarias para la ejecucion
    angleAdapted = adaptAngleToId(id, angle)
    defaultPosByID = getDefaultPosById(id)
    actualDirection = UP
    dirArray = array("i")
    directionFlag = 0

    # Comprobacion sobre el angulo de movimiento obtenido y la posicion por defecto obtenida
    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id) and defaultPosByID != 0):
        # Diferenciacion para ejecucion de simulacion activa y pasiva
        if (activo): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
        else: 
            torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
            way = calculateWay(angleAdapted, defaultPosByID)
            comparator = (lambda x, y: x > y) if way == POS else (lambda x, y: x < y) # Definicion del comparator
            dxl_previous_position = None

        # Comprobacion de movimiento terminado
        isFinished = False
        while not isFinished:
            if activo: # Si es simulacion activa
                isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD)
            else:  # Si es simulacion pasiva
                dxl_present_position = readPresentPosition(portHandler, packetHandler, id)

                if (dxl_present_position != None and dxl_previous_position != None): # Si es simulacion pasiva y se ha registrado alguna posicion anterior
                    # Calculo de direccion de movimiento
                    dirArray.append(calculateDirection(dxl_present_position, dxl_previous_position, actualDirection))
                    if (directionFlag == 2): 
                        if(dirArray[0] == dirArray[1] == dirArray[2] == UP): actualDirection = UP
                        elif(dirArray[0] == dirArray[1] == dirArray[2] == DOWN): actualDirection = DOWN
                        dirArray = array("i")
                        directionFlag = 0
                    else: directionFlag += 1

                    # Comprobacion si la posicion del servomotor es superior al angulo indicado diferenciando el sentido
                    if (comparator(rawToAngle(dxl_present_position), angleAdapted)): 
                        if(actualDirection == UP * way): 
                            torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                        else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
                    else: torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

                # Asignacion de posicion leida a posicion anterior para poder calcular la direccion en la siguiente ejecucion
                dxl_previous_position = dxl_present_position
                # Comprobacion de movimiento terminado
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)

        if activo: # Si la simulacion es activa ejecutar la ultima etapa del movimiento
            sleep(5)
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)

# Funcion para simular end feel blandos
def endFeelBlando(portHandler, packetHandler, id, angle, isActive):
    # Inicializacion de variables necesarias para la ejecucion
    angleAdapted = adaptAngleToId(id, angle)
    defaultPosByID = getDefaultPosById(id)
    actualDirection = UP
    dirArray = array("i")
    directionFlag = 0
    limitRangeFlag = 0

    # Comprobacion sobre el angulo de movimiento obtenido y la posicion por defecto obtenida
    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id) and defaultPosByID != 0):
        # 171 equivale a 10 grados en raw. Se usan las medidas en raw para que no haya errores de inexactitud por los grados
        # Calculo del sentido de movimiento para poder definir la posicion de ejecucion del end feel
        way = calculateWay(angleAdapted, defaultPosByID)
        if (way == NEG): posEndFeelBlando = angleToRaw(angleAdapted) + 171
        elif ( way == POS): posEndFeelBlando = angleToRaw(angleAdapted) - 171
        
        # Definicion del comparator
        comparator = (lambda x, y: x >= y) if way == POS else (lambda x, y: x <= y)

        # Diferenciacion para ejecucion de simulacion activa y pasiva
        if (isActive): moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
        else: 
            torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
            dxl_previous_position = None

        # Comprobacion de movimiento terminado
        isFinished = False
        while not isFinished:
            dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
            if (dxl_present_position != None): # Comprobacion lectura correcta de posicion actual
                if (not isActive and dxl_previous_position != None): # Si es simulacion pasiva y se ha registrado alguna posicion anterior
                    # Calculo de direccion de movimiento
                    dirArray.append(calculateDirection(dxl_present_position, dxl_previous_position, actualDirection))
                    if (directionFlag == 2): 
                        if(dirArray[0] == dirArray[1] == dirArray[2] == UP): actualDirection = UP
                        elif(dirArray[0] == dirArray[1] == dirArray[2] == DOWN): actualDirection = DOWN
                        elif(dirArray[0] == dirArray[1] == dirArray[2] == STOPPED): actualDirection = STOPPED
                        dirArray = array("i")
                        directionFlag = 0
                    else: directionFlag += 1

                if (comparator(dxl_present_position, posEndFeelBlando)): # Comprobacion si el servomotor ha superado la posicion del end feel
                    if(isActive): # Si es simulacion activa
                        speedControl(id, portHandler, packetHandler, 75)
                    else: # Si es simulacion pasiva
                        if (not comparator(rawToAngle(dxl_present_position), angleAdapted)): # Si la posicion actual NO es superior al angulo obtenido
                            limitRangeFlag = 0 # Flag para ejecutar solo una vez la activacion del torque maximo en el limite exacto del movimiento
                            if(actualDirection == UP * way): 
                                torqueLimitControl(id, portHandler, packetHandler, 0)
                                torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                        else: # Si la posicion actual es superior al angulo obtenido
                            if (actualDirection == UP * way): # Si la direccion es hacia arriba
                                if (limitRangeFlag == 0):
                                    torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE) # Se desactiva el torque para volverlo a activar en el limite con el valor maximo
                                    limitRangeFlag += 1
                                torqueLimitControl(id, portHandler, packetHandler, MAX_TORQUE_LIMIT)
                                torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                            else: # Si la direccion es hacia abajo
                                speedControl(id, portHandler, packetHandler, 200)
                                torqueLimitControl(id, portHandler, packetHandler, 120)
                                moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posEndFeelBlando))
                else: 
                    # Si es simulacion pasiva
                    if(not isActive): torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

            if (isActive): # Si es simulacion activa
                isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            else: # Si es simulacion pasiva
                dxl_previous_position = dxl_present_position
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            
        if (isActive): # Si la simulacion es activa ejecutar la ultima etapa del movimiento
            # Mover servomotor hacia el punto de ejecucion del end feel
            speedControl(id, portHandler, packetHandler, 150)
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(posEndFeelBlando))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posEndFeelBlando), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(posEndFeelBlando), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)

            sleep(5)
            # Mover servomotor hacia el punto de inicio
            speedControl(id, portHandler, packetHandler, SPEED_DEFAULT)
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)

# Funcion para simular end feel semirrigidos
def endFeelSemiRig(portHandler, packetHandler, id, angle, isActive):
    # Inicializacion de variables necesarias para la ejecucion
    angleAdapted = adaptAngleToId(id, angle)
    defaultPosByID = getDefaultPosById(id)
    endFeelPoints = array("i")
    mults = array("f", [0.75, 0.8, 0.85, 0.9, 0.95])

    # Comprobacion sobre el angulo de movimiento obtenido y la posicion por defecto obtenida
    if (angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id) and defaultPosByID != 0): 
        # Calculo de los puntos especificos del end feel a partir del 75% del angulo final  
        for i in range(5): endFeelPoints.append(int(defaultPosByID + mults[i] * (angleToRaw(angleAdapted) - defaultPosByID)))
        endFeelPoints.append(angleToRaw(angleAdapted))
            
        if (isActive): # Si es simulacion activa
            speedsEndFeel = array("i", [70, 57, 44, 31, 18, 5]) # Se inicializan las velocidades para cada rango calculado del end feel
            moveServoToAngle(id, portHandler, packetHandler, angleAdapted)
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(endFeelPoints[0]), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(endFeelPoints[0]), DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
        else: # Si es simulacion pasiva
            percentsTorque = array("f", [0.15, 0.25, 0.5, 0.75, 1]) # Se inicializan los porcentajes que se aplican del torque total para cada rango calculado del end feel

        # Calculo del sentido de movimiento para poder definir la posicion de ejecucion del end feel
        way = calculateWay(angleAdapted, defaultPosByID)
        # Definicion de los comparator
        comparator1 = (lambda x, y: x < y) if way == POS else (lambda x, y: x > y)
        comparator2 = (lambda x, y: x <= y) if way == POS else (lambda x, y: x >= y)

        # Comprobacion de movimiento terminado
        isFinished = False
        while not isFinished:
            dxl_present_position = readPresentPosition(portHandler, packetHandler, id) 
            if (dxl_present_position != None): # Comprobacion lectura correcta de posicion actual
                if(comparator1(dxl_present_position, endFeelPoints[0])): # Si la posicion actual es inferior al primer punto del end feel
                    # Si es simulacion activa
                    if(isActive): speedControl(id, portHandler, packetHandler, speedsEndFeel[0])
                    else: # Si es simulacion pasiva
                        torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)

                # Comprobacion si la posicion actual se encuentra entre alguno de los rangos calculados del end feel
                for i in range(5):
                    if(comparator2(endFeelPoints[i], dxl_present_position) and comparator1(dxl_present_position, endFeelPoints[i+1])): 
                        # Si es simulacion activa
                        if (isActive): speedControl(id, portHandler, packetHandler, speedsEndFeel[i+1])
                        else: # Si es simulacion pasiva
                            if (i == 0): torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
                            torqueLimitControl(id, portHandler, packetHandler, int(MAX_TORQUE_LIMIT_ENDFEEL * percentsTorque[i]))
                        break
                
                # Comprobacion si la posicion actual supera el limite final
                if (comparator2(endFeelPoints[5], dxl_present_position)): 
                    if (not isActive): # Si es simulacion pasiva
                        moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
                        torqueLimitControl(id, portHandler, packetHandler, 800)

            if (isActive): # Si es simulacion activa
                isFinished = moveIsFinished(portHandler, packetHandler, id, angleAdapted, DXL_MOVING_STATUS_THRESHOLD_ENDFEEL)
            else: # Si es simulacion pasiva
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
        
        if (isActive): # Si la simulacion es activa ejecutar la ultima etapa del movimiento
            speedControl(id, portHandler, packetHandler, SPEED_DEFAULT)
            torqueLimitControl(id, portHandler, packetHandler, MAX_TORQUE_LIMIT)
            # Mover servomotor hacia el punto de inicio
            moveServoToAngle(id, portHandler, packetHandler, rawToAngle(defaultPosByID))
            isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)
            while not isFinished:
                isFinished = moveIsFinished(portHandler, packetHandler, id, rawToAngle(defaultPosByID), DXL_MOVING_STATUS_THRESHOLD)