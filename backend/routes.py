from flask import Flask, request, jsonify
from flask_cors import CORS
import queue

app = Flask(__name__)
CORS(app)

# Colas para almacenar los datos
data_queue = queue.Queue()
stop_queue = queue.Queue()

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

    return jsonify({"status": "success", "message": "Signal received"})

def create_app():
    return app