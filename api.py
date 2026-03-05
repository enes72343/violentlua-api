from flask import Flask, request, jsonify
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False  # ÖNEMLİ!

db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASS'),
    'database': os.environ.get('DB_NAME')
}

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'API çalışıyor'})

@app.route('/api', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/', methods=['GET', 'POST', 'OPTIONS'])  # Her iki yolu da kabul et
def api():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.args if request.method == 'GET' else request.form
        action = data.get('action')
        
        if action == 'check':
            license_key = data.get('license_key')
            
            # Test bağlantısı
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM licenses WHERE license_key = %s AND status = 'active'", (license_key,))
            license = cursor.fetchone()
            
            if license:
                cursor.execute("""
                    UPDATE licenses SET 
                    last_check = NOW(), 
                    discord_id = %s, 
                    discord_username = %s, 
                    sunucu_id = %s, 
                    sunucu_adi = %s 
                    WHERE license_key = %s
                """, (data.get('discord_id'), data.get('discord_username'), 
                      data.get('sunucu_id'), data.get('sunucu_adi'), license_key))
                conn.commit()
                
                return jsonify({'valid': True})
            else:
                return jsonify({'valid': False, 'reason': 'Geçersiz lisans'})
                
    except mysql.connector.Error as err:
        return jsonify({'valid': False, 'reason': f'DB hatası: {err}'})
    except Exception as e:
        return jsonify({'valid': False, 'reason': f'Hata: {str(e)}'})
