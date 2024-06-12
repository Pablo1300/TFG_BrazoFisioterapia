from array import array

# Control table address
## Control table address is different in Dynamixel model
ADDR_MX_CW_ANGLE_LIMIT              = 6
ADDR_MX_CCW_ANGLE_LIMIT             = 8
ADDR_MX_TORQUE_ENABLE               = 24               
ADDR_MX_P_GAIN                      = 28
ADDR_MX_I_GAIN                      = 27
ADDR_MX_D_GAIN                      = 26
ADDR_MX_GOAL_POSITION               = 30
ADDR_MX_MOVING_SPEED                = 32
ADDR_MX_TORQUE_LIMIT                = 34
ADDR_MX_PRESENT_POSITION            = 36

# Default setting   
DXL1_ID                             = 1                                 # Dynamixel#1 ID : 1 (Hombro vertical)
DXL2_ID                             = 2                                 # Dynamixel#2 ID : 2 (Hombro horizontal)
DXL3_ID                             = 3                                 # Dynamixel#3 ID : 3 (Hombro)
DXL4_ID                             = 4                                 # Dynamixel#4 ID : 4 (Codo)  
DXL_IDS                             = array('i', [DXL1_ID, DXL2_ID, DXL3_ID, DXL4_ID])
ACT                                 = True
PAS                                 = False
POS                                 = 1
NEG                                 = -1
UP                                  = 2
DOWN                                = -2
STOPPED                             = 0    

# Default parameters 
TORQUE_ENABLE                       = 1                                 # Value for enabling the torque
TORQUE_DISABLE                      = 0                                 # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD         = 5                                # Dynamixel moving status threshold
DXL_MOVING_STATUS_THRESHOLD_ENDFEEL = 20
SPEED_DEFAULT                       = 100
MAX_TORQUE_LIMIT                    = 1023
MAX_TORQUE_LIMIT_ENDFEEL            = 200
BAUDRATE                            = 2000000                             # Dynamixel default baudrate : 57600
DEVICENAME                          = '/dev/tty.usbserial-FT6S4F80'     # Check which port is being used on your controller
                                                                        # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
P                                   = 35
I                                   = 5
D                                   = 10
ID1_POSITION                        = 1024
ID2_POSITION                        = 1024
ID3_POSITION                        = 2048
ID4_POSITION                        = 1479
COMM_SUCCESS                        = 0

# Data Byte Length
LEN_MX_GOAL_POSITION                = 2
LEN_MX_MOVING_SPEED                 = 2

# Protocol version
PROTOCOL_VERSION                    = 1.0                               # See which protocol version is used in the Dynamixel