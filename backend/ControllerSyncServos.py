import os
from Utils import *
from EndFeels import *
from time import sleep
from Chorradas import *
from dynamixel_sdk import *     # Uses Dynamixel SDK library

# Definicion de funcion getch() para obtener la tecla que se pulsa dependiendo del SSOO
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def setDefaultConfiguration(portHandler, packetHandler):
    # Servo del codo a modo multivuelta para poder ejecutar movimientos sin restricción del eje
    setMultiturnMode(portHandler, packetHandler, DXL4_ID)

    # Configuramos todos los id con sus parametros predefinidos
    for DXL_ID in DXL_IDS:
        torqueControl(DXL_ID, portHandler, packetHandler, TORQUE_ENABLE)
        torqueLimitControl(DXL_ID, portHandler, packetHandler, MAX_TORQUE_LIMIT)
        speedControl(DXL_ID, portHandler, packetHandler, SPEED_DEFAULT)
        pidControl(DXL_ID, portHandler, packetHandler, P, I, D)

def movPosInicial(portHandler, packetHandler, groupSyncWritePos):
    # Descomponemos valor int de 32 bits en bytes individuales para que puedan ser procesados
    id1_goal_position = [DXL_LOBYTE(ID1_POSITION), DXL_HIBYTE(ID1_POSITION)]
    id2_goal_position = [DXL_LOBYTE(ID2_POSITION), DXL_HIBYTE(ID2_POSITION)]
    id3_goal_position = [DXL_LOBYTE(ID3_POSITION), DXL_HIBYTE(ID3_POSITION)]
    id4_goal_position = [DXL_LOBYTE(ID4_POSITION), DXL_HIBYTE(ID4_POSITION)]
    
    # Se añaden las goal position a los param group sync
    addParamGroupSync(groupSyncWritePos, DXL1_ID, id1_goal_position)
    addParamGroupSync(groupSyncWritePos, DXL2_ID, id2_goal_position)
    addParamGroupSync(groupSyncWritePos, DXL3_ID, id3_goal_position)
    addParamGroupSync(groupSyncWritePos, DXL4_ID, id4_goal_position)
        
    # Syncwrite goal position
    dxl_comm_result = groupSyncWritePos.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    # Clear syncwrite parameter storage
    groupSyncWritePos.clearParam()

    while 1:
        # Read Dynamixels present position
        dxl1_present_position = readPresentPosition(portHandler, packetHandler, DXL1_ID)
        dxl2_present_position = readPresentPosition(portHandler, packetHandler, DXL2_ID)
        dxl3_present_position = readPresentPosition(portHandler, packetHandler, DXL3_ID)
        dxl4_present_position = readPresentPosition(portHandler, packetHandler, DXL4_ID)

        # Ajustar para valores que indican un desbordamiento
        if dxl4_present_position > 28672:  # Rango maximo para el positivo
            dxl4_present_position -= 65536

        # Comprobar si se han posicionado correctamente
        if not ((abs(ID1_POSITION - dxl1_present_position) > DXL_MOVING_STATUS_THRESHOLD) or 
                (abs(ID2_POSITION - dxl2_present_position) > DXL_MOVING_STATUS_THRESHOLD) or
                (abs(ID3_POSITION - dxl3_present_position) > DXL_MOVING_STATUS_THRESHOLD) or
                (abs(ID4_POSITION - dxl4_present_position) > DXL_MOVING_STATUS_THRESHOLD)):
            print("Brazo posicionado y listo")
            break          

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Initialize GroupSyncWrite instance
groupSyncWritePos = GroupSyncWrite(portHandler, packetHandler, ADDR_MX_GOAL_POSITION, LEN_MX_GOAL_POSITION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

setDefaultConfiguration(portHandler, packetHandler)
movPosInicial(portHandler, packetHandler, groupSyncWritePos)

while 1:
    endFeelDuro(portHandler, packetHandler, DXL4_ID, 100, ACT)

# saludo(portHandler, packetHandler)

# saludo(portHandler, packetHandler)

# Close port
portHandler.closePort()