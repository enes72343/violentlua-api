from flask import Flask, request, jsonify
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)

# Environment variables'tan al
db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASS'),
    'database': os.environ.get('DB_NAME')
}

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'API çalışıyor', 'message': 'ViolentLua Lisans API'})

@app.route('/api', methods=['GET', 'POST'])  # İKİSİNİ DE KABUL ET!
def api():
    try:
        # GET veya POST'tan verileri al
        if request.method == 'GET':
            data = request.args
        else:
            data = request.form
            
        action = data.get('action')
        
        if not action:
            return jsonify({'valid': False, 'reason': 'Action parametresi gerekli'})
        
        if action == 'check':
            license_key = data.get('license_key')
            
            if not license_key:
                return jsonify({'valid': False, 'reason': 'Lisans kodu gerekli'})
            
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM licenses WHERE license_key = %s AND status = 'active'", (license_key,))
            license = cursor.fetchone()
            
            if license:
                # Son kontrolü güncelle
                cursor.execute("""
                    UPDATE licenses SET 
                    last_check = NOW(), 
                    discord_id = %s, 
                    discord_username = %s, 
                    sunucu_id = %s, 
                    sunucu_adi = %s 
                    WHERE license_key = %s
                """, (
                    data.get('discord_id'), 
                    data.get('discord_username'), 
                    data.get('sunucu_id'), 
                    data.get('sunucu_adi'), 
                    license_key
                ))
                conn.commit()
                
                cursor.close()
                conn.close()
                
                return jsonify({
                    'valid': True,
                    'bot_name': license['bot_name'],
                    'expires_at': license['expires_at'] or 'Sınırsız'
                })
            else:
                cursor.close()
                conn.close()
                return jsonify({'valid': False, 'reason': '❌ Geçersiz lisans kodu'})
        
        return jsonify({'valid': False, 'reason': 'Geçersiz action'})
        
    except Exception as e:
        return jsonify({'valid': False, 'reason': f'Sunucu hatası: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
