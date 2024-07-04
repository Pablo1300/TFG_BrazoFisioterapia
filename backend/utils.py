from constants import *
import queue

# Colas para almacenar los datos
data_queue = queue.Queue()
stop_queue = queue.Queue()
simulating_queue = queue.Queue()


## FUNCIONES DE CONVERSION

# Función que pasa de grado a decimal
def angleToRaw(angle):
    if (angle == 360): return (int) (0)
    else: return (int) (round(angle/0.087891))

# Función que pasa de decimal a grado
def rawToAngle(raw):
    return (float) (raw*0.087891)

# Configura el angulo de entrada a la posicion especifica del servomotor
def adaptAngleToId(id, angle):
    if id == DXL1_ID:
        if -60 <= angle <= 180:
            angleAdapted = angle + 90
        else: angleAdapted = "ERROR al insertar el ángulo del hombro, el valor tiene que estar entre -60 y 180"
    elif id == DXL2_ID:
        if 0 <= angle <= 180:
            angleAdapted = angle + 90
        else: angleAdapted = "ERROR al insertar el ángulo del hombro, el valor tiene que estar entre 0 y 180"
    elif id == DXL3_ID:
        if -90 <= angle <= 90:
            angleAdapted = angle + 180
        else: angleAdapted = "ERROR al insertar el ángulo del hombro, el valor tiene que estar entre -90 y 90"
    elif id == DXL4_ID:
        if -5 <= angle <= 140:
            angleAdapted = 130 - angle
        else: angleAdapted = "ERROR al insertar el ángulo del codo, el valor tiene que estar entre -7 y 140"
    else: angleAdapted = ("ERROR id desconocido")

    return angleAdapted

# Obtener posicion inicial por defecto de cada servomotor
def getDefaultPosById(id):
    if (id == DXL1_ID): defaultPos = ID1_POSITION
    elif (id == DXL2_ID): defaultPos = ID2_POSITION
    elif (id == DXL3_ID): defaultPos = ID3_POSITION
    elif (id == DXL4_ID): defaultPos = ID4_POSITION
    else: raise Exception("ERROR ID desconocido")
    return defaultPos


## FUNCIONES DE CONTROL

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


## FUNCIONES DE LECTURA

# Leer posición actual
def readPresentPosition(portHandler, packetHandler, id):
    try:
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, ADDR_MX_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            dxl_present_position = None
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
            dxl_present_position = None

        if dxl_present_position != None:
            # Ajustar para valores que indican un desbordamiento solo codo unico con mov negativo
            if dxl_present_position > 28672:  # Rango maximo para el positivo
                dxl_present_position -= 65536
            
        return dxl_present_position
    except Exception as e: print("ERROR: No se ha podido leer la posicion actual\n", e)

# Leer torque actual
def readPresentTorque(portHandler, packetHandler, id):
    dxl_present_torque, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, ADDR_MX_TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        
    return dxl_present_torque


## FUNCIONES DE MOVIMIENTO

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

# Añadir parametro a un grupo de sincronizacion de servos
def addParamGroupSync(groupSyncWrite, id, param):
    dxl_addparam_result = groupSyncWrite.addParam(id, param)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % id)
        quit()

# Calcular direccion de movimiento del servomotor
def calculateDirection(actualPosition, previousPosition):
    if (previousPosition != None):
        if (actualPosition > previousPosition): direction = UP
        elif(actualPosition < previousPosition): direction = DOWN
        else: direction = STOPPED
    else: direction = UP

    return direction

# Calcular sentido de movimiento del servo (de mayor a menor = NEG, de menor a mayor = POS)
def calculateWay(angleAdapted, posInicial):
    # Si la posicion final es menor que la posicion inicial, se suman los correspondientes grados a la final para simular el end feel
    # Si la posicion final es mayor que la posicion inicial, se restan los correspondientes grados a la final para simular el end feel
    if (angleToRaw(angleAdapted) - posInicial < 0): way = NEG
    elif (angleToRaw(angleAdapted) - posInicial > 0): way = POS
    return way

# Configurar servo en modo multivuelta
def setMultiturnMode(portHandler, packetHandler, id):
    error = COMM_SUCCESS

    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_CW_ANGLE_LIMIT, 4095)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        error = COMM_ERROR
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        error = COMM_ERROR
        
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_CCW_ANGLE_LIMIT, 4095)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        error = COMM_ERROR
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
        error = COMM_ERROR
    return error

## FUNCIONES DE VALIDACION

# Comprobar si el angulo adaptado es valido 
def angleAdaptedIsValid(angleAdapted, portHandler, packetHandler, id):
    if not isinstance(angleAdapted, str):
        posInicial = readPresentPosition(portHandler, packetHandler, id)
        while posInicial == None: posInicial = readPresentPosition(portHandler, packetHandler, id)
        if (angleToRaw(angleAdapted) - posInicial == 0): raise Exception("El brazo ya se encuentra en la posición indicada")
        else: 
            return True
    else: raise Exception(angleAdapted)

# Comprobar que el movimiento se ha realizado
def moveIsFinished(portHandler, packetHandler, id, goalAngle, statusThreshold):
        dxl_present_position = readPresentPosition(portHandler, packetHandler, id)
        while dxl_present_position == None: dxl_present_position = readPresentPosition(portHandler, packetHandler, id)

        # Ajustar para valores que indican un desbordamiento solo codo unico con mov negativo
        if dxl_present_position > 28672:  # Rango maximo para el positivo
            dxl_present_position -= 65536
        if not abs(angleToRaw(goalAngle) - dxl_present_position) > statusThreshold:
            return True
        return False

def isMotorOff(portHandler, packetHandler):
    presentTorqueValues = array('i')
    for DXL_ID in DXL_IDS: presentTorqueValues.append(readPresentTorque(portHandler, packetHandler, DXL_ID))

    if (presentTorqueValues[0] == presentTorqueValues[1] == presentTorqueValues[2] == presentTorqueValues[3] == 0): return True
    else: return False
