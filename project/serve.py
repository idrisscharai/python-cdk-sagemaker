from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

@app.route('/invocations', methods=['POST'])
def invoke():
    return jsonify({"result": "dummy prediction"}), 200

app.run(host='0.0.0.0', port=8080)
