from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore

app = Flask(__name__)
CORS(app)
app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});
@app.route('/api/predict', methods=['POST'])  # Ensure the method is POST
def predict():
    data = request.get_json()  # Get the JSON data from the request
    input_text = data.get('input_text')  # Extract input_text
    # Add your logic to process input_text
    output = f"Processed: {input_text}"  # Example processing
    return jsonify({"output": output})  # Return the result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
