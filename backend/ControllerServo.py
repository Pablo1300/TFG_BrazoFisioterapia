import os
import streamlit as st

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

from dynamixel_sdk import *                   # Uses Dynamixel SDK library

# Control table address
ADDR_MX_TORQUE_ENABLE      = 24               # Control table address is different in Dynamixel model
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque

# Protocol version
PROTOCOL_VERSION            = 1.0             # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 4                                 # Dynamixel ID : 1
BAUDRATE                    = 57600                             # Dynamixel default baudrate : 57600
DEVICENAME                  = '/dev/tty.usbserial-FT6S4F80'     # Check which port is being used on your controller
                                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

DXL_MINIMUM_POSITION_VALUE  = 10                # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 300                # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
DXL_MOVING_STATUS_THRESHOLD = 10                # Dynamixel moving status threshold

# Función que pasa de grado a decimal
def angleToRaw(angle):
    if (angle == 360): return (int) (0)
    else: return (int) (round(angle/0.087891))

# Función que pasa de decimal a grado
def rawToAngle(raw):
    return (float) (raw*0.087891)

# Controlar torque
def torqueControl(id, portHandler, packetHandler, torqueByteControl):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, id, ADDR_MX_TORQUE_ENABLE, torqueByteControl)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

def moveServoToAngle(id, portHandler, packetHandler, angle):
    ## COMPROBAR SI TENGO QUE ASEGURARME DE QUE NO SEA <360 y >0
    if (angle <= 360) and (angle >= 0):
        # Enable Dynamixel Torque
        torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
        # Write goal position
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, id, ADDR_MX_GOAL_POSITION, angleToRaw(angle))
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
    
        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, ADDR_MX_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (id, angleToRaw(angle), dxl_present_position))

            if not abs(angleToRaw(angle) - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                break

        # Disable Dynamixel Torque
        torqueControl(id, portHandler, packetHandler, TORQUE_DISABLE)
    else:
        print("ERROR Out of range")

def moveServoAddAngle(id, portHandler, packetHandler, angle):
    ## COMPROBAR SI SE PUEDEN SUMAR ANGULOS EJEMPLO 60+360 Y MOVERLO HASTA AHI
    # Read present position
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, id, ADDR_MX_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    
    goalAngle = rawToAngle(dxl_present_position) + angle
    print(rawToAngle(dxl_present_position))
    print(angle)
    print(goalAngle)

    if (goalAngle <= 360) and (goalAngle >= 0):
        moveServoToAngle(id, portHandler, goalAngle)
    else:
        print("ERROR Out of range")

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

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

st.title("PRUEBAS SERVO")
      
degree = st.slider("Ángulo de movimiento", 0, 360)

torqueByteControl, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    if (torqueByteControl == TORQUE_ENABLE): torqueValue = True
    else : torqueByteControl = torqueValue = False

    torqueByteControl = st.toggle("Torque activado", value = torqueValue)
    torqueControl(DXL_ID, portHandler, packetHandler, torqueByteControl)

moveServoToAngle(DXL_ID, portHandler, packetHandler, degree)



#moveServoToAngle(DXL_ID, portHandler, 0)
#moveServoToAngle(DXL_ID, portHandler, 90)
#moveServoToAngle(DXL_ID, portHandler, 45)
#moveServoToAngle(DXL_ID, portHandler, 180)
#moveServoToAngle(DXL_ID, portHandler, 270)
#moveServoToAngle(DXL_ID, portHandler, 359)
#moveServoToAngle(DXL_ID, portHandler, 0)
#moveServoAddAngle(DXL_ID, portHandler, 180)
#moveServoAddAngle(DXL_ID, portHandler, 90)
#moveServoAddAngle(DXL_ID, portHandler, 90)


# Close port
portHandler.closePort()