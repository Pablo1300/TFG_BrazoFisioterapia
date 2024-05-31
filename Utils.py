from Constants import *

# Función que pasa de grado a decimal
def angleToRaw(angle):
    if (angle == 360): return (int) (0)
    else: return (int) (round(angle/0.087891))

# Función que pasa de decimal a grado
def rawToAngle(raw):
    return (float) (raw*0.087891)

# Controlar torque
def torqueControl(id, portHandler, packetHandler, torqueControl):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_MX_TORQUE_ENABLE, torqueControl)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Controlar velocidad
def speedControl(id, portHandler, packetHandler, speedControl):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_MOVING_SPEED, speedControl)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Controlar limite del torque 
def torqueLimitControl(id, portHandler, packetHandler, torqueLimitControl):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_TORQUE_LIMIT, torqueLimitControl)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Controlar parametros PID
def pidControl(id, portHandler, packetHandler, p, i, d):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_MX_P_GAIN, p)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_MX_I_GAIN, i)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_MX_D_GAIN, d)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Leer posición actual
def readPresentPosition(portHandler, packetHandler, id):
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, ADDR_MX_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    # Ajustar para valores que indican un desbordamiento solo codo unico con mov negativo
    if dxl_present_position > 28672:  # Rango maximo para el positivo
        dxl_present_position -= 65536
        
    return dxl_present_position

# Mover servo a un punto
def moveServoToAngle(id, portHandler, packetHandler, angle):
    torqueControl(id, portHandler, packetHandler, TORQUE_ENABLE)
    
    # Write goal position
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_GOAL_POSITION, angleToRaw(angle))
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Sumar angulo a la posicion del servo
def moveServoAddAngle(id, portHandler, packetHandler, angle):
    ## COMPROBAR SI SE PUEDEN SUMAR ANGULOS EJEMPLO 60+360 Y MOVERLO HASTA AHI
    dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
    
    goalAngle = rawToAngle(dxl_present_position) + angle

    if (goalAngle <= 360) and (goalAngle >= 0):
        moveServoToAngle(id, portHandler, packetHandler, goalAngle)
    else:
        print("ERROR Out of range")

# Comprobar que el movimiento se ha realizado
def moveIsFinished(portHandler, packetHandler, id, goalAngle, statusThreshold):
    dxl_present_position = readPresentPosition(portHandler, packetHandler, id)

    # Ajustar para valores que indican un desbordamiento solo codo unico con mov negativo
    if dxl_present_position > 28672:  # Rango maximo para el positivo
        dxl_present_position -= 65536
    if not abs(angleToRaw(goalAngle) - dxl_present_position) > statusThreshold:
        return True
    return False

# Añadir parametro a un grupo de sincronizacion de servos
def addParamGroupSync(groupSyncWrite, id, param):
    dxl_addparam_result = groupSyncWrite.addParam(id, param)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % id)
        quit()

# Configurar servo en modo multivuelta
def setMultiturnMode(portHandler, packetHandler, id):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_CW_ANGLE_LIMIT, 4095)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_CCW_ANGLE_LIMIT, 4095)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

# Configura el angulo de entrada a la posicion especifica del servomotor
def adaptAngleToId(id, angle):
    if id == DXL1_ID:
        if -60 <= angle <= 180:
            angleAdapted = angle + 90
        else: angleAdapted = "ERROR al insertar el ángulo del codo, el valor tiene que estar entre -60 y 180"
    elif id == DXL2_ID:
        if 0 <= angle <= 80: #NO VA A SER 90 COMPROBAR 
            angleAdapted = angle + 90
        else: angleAdapted = "NO ESTA TERMINADO"
    elif id == DXL3_ID:
        angleAdapted = "NO ESTA TERMINADO"
    elif id == DXL4_ID:
        if -6.5 <= angle <= 140:
            angleAdapted = 130 - angle
        else: angleAdapted = "ERROR al insertar el ángulo del codo, el valor tiene que estar entre -6,5 y 140"
    
    return angleAdapted

def angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id):
    valid = False
    if not isinstance(angleAdapted, str):
        posInicial = readPresentPosition(portHandler, packetHandler, id)
        if (angleToRaw(angleAdapted) - posInicial == 0): print("El brazo ya se encuentra en la posición indicada")
        else: 
            valid = True
    else: print(angleAdapted)

    return valid
