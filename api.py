from flask import Flask, request, jsonify
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)

# MySQL bağlantısı (Infinityfree veritabanın)
db_config = {
    'host': 'sql103.infinityfree.com',
    'user': 'if0_41298601',
    'password': 'at0oigki2eR8d',
    'database': 'if0_41298601_baba'
}

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'API çalışıyor', 'message': 'ViolentLua Lisans API'})

@app.route('/api', methods=['POST'])
def api():
    try:
        data = request.form
        action = data.get('action')
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        if action == 'check':
            license_key = data.get('license_key')
            
            cursor.execute("SELECT * FROM licenses WHERE license_key = %s AND status = 'active'", (license_key,))
            license = cursor.fetchone()
            
            if license:
                # Son kontrolü güncelle
                cursor.execute("UPDATE licenses SET last_check = NOW(), discord_id = %s, discord_username = %s, sunucu_id = %s, sunucu_adi = %s WHERE license_key = %s",
                             (data.get('discord_id'), data.get('discord_username'), data.get('sunucu_id'), data.get('sunucu_adi'), license_key))
                conn.commit()
                
                return jsonify({
                    'valid': True,
                    'bot_name': license['bot_name'],
                    'expires_at': license['expires_at'] or 'Sınırsız'
                })
            else:
                return jsonify({'valid': False, 'reason': 'Geçersiz lisans kodu'})
        
        cursor.close()
        conn.close()
        return jsonify({'error': 'Geçersiz action'})
        
    except Exception as e:
        return jsonify({'valid': False, 'reason': f'Sunucu hatası: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
