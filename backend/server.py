
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import threading
from werkzeug.serving import make_server
from utils import simulating_queue, stop_queue, data_queue

app = Flask(__name__)
CORS(app)

simulation = {
    'articulation': None,
    'movement': None,
    'endfeel': None,
    'mobilization': None,
    'executionPoint': None,
    'simulating': "false"
}

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

@app.route('/simulating', methods=['GET'])
def isSimulating():
    global simulating
    try: 
        data = simulating_queue.get_nowait()

        simulation["articulation"] = data["articulation"]
        simulation["movement"] = data["movement"]
        simulation["endfeel"] = data["endfeel"]
        simulation["mobilization"] = data["mobilization"]
        simulation["executionPoint"] = data["executionPoint"]
        simulation["simulating"] = data["simulating"]
    except: pass
    return jsonify({"status": "success", "articulation": simulation['articulation'], "movement": simulation['movement'], "endfeel": simulation['endfeel'], "mobilization": simulation['mobilization'], "executionPoint": simulation['executionPoint'], "simulating": simulation['simulating']}) 

server = ServerEndFeels(app)

