from routes import create_app
from ControllerSyncServos import executeController
import threading

app = create_app()

if __name__ == '__main__':
    endfeels_thread = threading.Thread(target=executeController)
    endfeels_thread.start()

    routes_thread = threading.Thread(app.run(debug=True, host='0.0.0.0'))

    endfeels_thread.join()