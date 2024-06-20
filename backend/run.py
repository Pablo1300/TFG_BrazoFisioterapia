
from server import server
from ControllerSyncServos import executeController
import threading

def closeServer():
    server.shutdown()
    print("Server closed")


if __name__ == '__main__':
    server.start()

    try:
        endfeels_process = threading.Thread(target=executeController())
        endfeels_process.start()

        while endfeels_process.is_alive():
            endfeels_process.join(timeout=1)
        closeServer()
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        closeServer()

# MAÑANA: que se ejecute el shutdown en todo caso, que cuando apagues el robot termine el programa y que se guarden datos de ejecucion y parar
    
