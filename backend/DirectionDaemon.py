import daemon
import multiprocessing
from Constants import UP, DOWN

def directionDaemon(dir_queue_in, dir_queue_out):
    dxl_previous_position = None
    while True:
        dxl_present_position = dir_queue_in.get()  # Recibe datos del proceso principal

        # Calcular direccion
        if (dxl_present_position == None): break
        if (dxl_previous_position != None):
            if (dxl_present_position >= dxl_previous_position): direction = UP
            elif (dxl_present_position < dxl_previous_position): direction = DOWN
        else: dxl_previous_position = dxl_present_position

        dir_queue_out.put(direction)  # Envía el resultado de vuelta

# def directionDaemon(dir_queue_in, dir_queue_out):
#     prev_id = 0
#     while True:
#         directionData = dir_queue_in.get()  # Recibe datos del proceso principal
#         if(directionData[1] != prev_id): dxl_previous_position = None

#         # Calcular direccion
#         if (directionData[0] == None): break # Condición para terminar el daemon
#         if (dxl_previous_position != None):
#             if (directionData[0] >= dxl_previous_position): direction = UP
#             elif (directionData[0] < dxl_previous_position): direction = DOWN
#         else: dxl_previous_position = directionData[0]

#         dir_queue_out.put(direction)  # Envia el resultado de vuelta

if __name__ == "__main__":
    dir_queue_in = multiprocessing.Queue()
    dir_queue_out = multiprocessing.Queue()

    with daemon.DaemonContext():
        directionDaemon(dir_queue_in, dir_queue_out)