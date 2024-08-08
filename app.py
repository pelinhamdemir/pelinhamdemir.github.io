from flask import Flask, request, jsonify, make_response 
from flask_cors import 
CORS app = Flask(__name__) 
CORS(app, resources={r"/api/*": {"origins": "https://pelinhamdemir.github.io"}}) 
@app.route('/api/predict', methods=['POST', 'OPTIONS']) 
def predict(): 
  if request.method == 'OPTIONS': 
    return _build_cors_preflight_response() 
  else: 
    return _corsify_actual_response() 

def _build_cors_preflight_response(): 
  response = make_response() 
  response.headers.add("Access-Control-Allow-Origin", "https://pelinhamdemir.github.io") 
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type') 
  response.headers.add('Access-Control-Allow-Methods', 'POST') 
  return response 

def _corsify_actual_response(): 
  data = request.get_json() 
  input_text = data.get('input_text') if data else None 
  
  output = f"Processed: {input_text}"  if input_text else "No input provided" 
  
  response = jsonify({"output": output}) 
  response.headers.add("Access-Control-Allow-Origin", "https://pelinhamdemir.github.io") 
  return response 

if __name__ == '__main__': app.run(host='0.0.0.0', port=5500)
