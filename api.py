from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
app.url_map.strict_slashes = False

INFINITY_API = "https://violentdevelopment.free.nf/api.php"

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'Proxy API çalışıyor', 'message': 'Infinityfree API'ye yönlendiriyor'})

@app.route('/api', methods=['GET', 'POST', 'OPTIONS'])
def api():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Gelen veriyi al
        if request.method == 'GET':
            data = request.args
        else:
            data = request.form
        
        # Infinityfree API'ye istek at
        response = requests.post(
            INFINITY_API,
            data=data,
            timeout=10
        )
        
        return response.text, response.status_code, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({'valid': False, 'reason': f'Proxy hatası: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
