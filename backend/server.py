
from flask import Flask, request, jsonify
from flask_cors import CORS
import queue
import threading
from werkzeug.serving import make_server

app = Flask(__name__)
CORS(app)

# Colas para almacenar los datos
data_queue = queue.Queue()
stop_queue = queue.Queue()

class ServerEndFeels(threading.Thread):
    def __init__(self, app, host='0.0.0.0', port=5000):
        threading.Thread.__init__(self)
        self.server = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print("Starting server...")
        self.server.serve_forever()

    def shutdown(self):
        print('Stopping server...')
        self.server.shutdown()

@app.route('/submit', methods=['POST'])
def submitEndFeelData():
    articulation = request.form["articulation"]
    movement = request.form["movement"]
    endfeel = request.form["endfeel"]
    mobilization = request.form["mobilization"]
    executionPoint = request.form["executionPoint"]

    # Poner los datos en la cola
    data_queue.put({
        "articulation": articulation,
        "movement": movement,
        "endfeel": endfeel,
        "mobilization": mobilization,
        "executionPoint": executionPoint
    })

    return jsonify({"status": "success", "articulation": articulation, "movement": movement, "endfeel": endfeel, "mobilization": mobilization, "executionPoint": executionPoint}) 

@app.route('/stop', methods=['POST'])
def stopSimulation():
    data = request.get_json()
    isSimulating = data.get("simulating")

    stop_queue.put(isSimulating)

    return jsonify({"status": "success", "message": "stopped received"})

server = ServerEndFeels(app)

