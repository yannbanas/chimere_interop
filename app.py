from flask import Flask, request, jsonify

from chimere.core import convert
from chimere.types import JSONData, PythonDictData
from chimere.types_interop import CppStructData, RustStructData, GoStructData

app = Flask(__name__)

@app.route('/to_cpp', methods=['POST'])
def to_cpp():
    data = request.get_json(force=True)
    source_obj = PythonDictData(data)
    try:
        cpp_obj = convert(source_obj, CppStructData)
        return jsonify({"message": "Conversion vers C++ réussie"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/from_cpp', methods=['POST'])
def from_cpp():
    data = request.get_json(force=True)
    dict_obj = PythonDictData(data)
    try:
        cpp_obj = convert(dict_obj, CppStructData)
        json_obj = convert(cpp_obj, JSONData)
        return jsonify({"cpp_to_json": json_obj.content}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/to_rust', methods=['POST'])
def to_rust():
    data = request.get_json(force=True)
    source_obj = PythonDictData(data)
    try:
        rust_obj = convert(source_obj, RustStructData)
        print(rust_obj)
        return jsonify({"message": "Conversion vers Rust réussie"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/from_rust', methods=['POST'])
def from_rust():
    data = request.get_json(force=True)
    dict_obj = PythonDictData(data)
    try:
        rust_obj = convert(dict_obj, RustStructData)
        json_obj = convert(rust_obj, JSONData)
        return jsonify({"rust_to_json": json_obj.content}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/to_go', methods=['POST'])
def to_go():
    data = request.get_json(force=True)
    source_obj = PythonDictData(data)
    try:
        go_obj = convert(source_obj, GoStructData)
        return jsonify({"message": "Conversion vers Go réussie"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/from_go', methods=['POST'])
def from_go():
    data = request.get_json(force=True)
    dict_obj = PythonDictData(data)
    try:
        go_obj = convert(dict_obj, GoStructData)
        json_obj = convert(go_obj, JSONData)
        return jsonify({"go_to_json": json_obj.content}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
if __name__ == '__main__':
    # Lancer le serveur : python app.py
    app.run(debug=True)
