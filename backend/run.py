
from server import server
from controller import executeController
import threading

def startServer():
    server.start()
    print("Server started")

def closeServer():
    server.shutdown()
    print("Server closed")


if __name__ == '__main__':
    startServer()
    try:
        endfeels_process = threading.Thread(target=executeController())
        endfeels_process.start()

        while endfeels_process.is_alive():
            endfeels_process.join(timeout=1)
        closeServer()
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        closeServer()
