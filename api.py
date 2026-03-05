from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False

# SQLite veritabanı
DB_FILE = 'licenses.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  license_key TEXT UNIQUE NOT NULL,
                  bot_name TEXT,
                  status TEXT DEFAULT 'active',
                  discord_id TEXT,
                  discord_username TEXT,
                  sunucu_id TEXT,
                  sunucu_adi TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  expires_at TIMESTAMP,
                  last_check TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Test lisansı ekle (yoksa)
    c.execute("SELECT * FROM licenses WHERE license_key = 'TEST-123'")
    if not c.fetchone():
        c.execute("INSERT INTO licenses (license_key, bot_name, status) VALUES (?, ?, ?)",
                  ('TEST-123', 'WispByte Bot 1', 'active'))
    
    # Admin ekle (violentadb1 / violentadb1)
    c.execute("SELECT * FROM admins WHERE username = 'violentadb1'")
    if not c.fetchone():
        c.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                  ('violentadb1', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi'))
    
    conn.commit()
    conn.close()

# Veritabanını başlat
init_db()

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'API çalışıyor', 'message': 'SQLite Lisans Sistemi'})

@app.route('/api', methods=['GET', 'POST', 'OPTIONS'])
def api():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.args if request.method == 'GET' else request.form
        action = data.get('action')
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        if action == 'check':
            license_key = data.get('license_key')
            
            c.execute("SELECT * FROM licenses WHERE license_key = ? AND status = 'active'", (license_key,))
            license = c.fetchone()
            
            if license:
                # Güncelle
                c.execute("""
                    UPDATE licenses SET 
                    last_check = CURRENT_TIMESTAMP, 
                    discord_id = ?, 
                    discord_username = ?, 
                    sunucu_id = ?, 
                    sunucu_adi = ? 
                    WHERE license_key = ?
                """, (
                    data.get('discord_id', ''),
                    data.get('discord_username', ''),
                    data.get('sunucu_id', ''),
                    data.get('sunucu_adi', ''),
                    license_key
                ))
                conn.commit()
                
                return jsonify({
                    'valid': True,
                    'bot_name': license['bot_name'],
                    'expires_at': license['expires_at'] or 'Sınırsız'
                })
            else:
                return jsonify({'valid': False, 'reason': '❌ Geçersiz lisans kodu'})
        
        elif action == 'add':
            # Admin panel için lisans ekleme
            c.execute("INSERT INTO licenses (license_key, bot_name, status) VALUES (?, ?, 'active')",
                     (data.get('license_key'), data.get('bot_name')))
            conn.commit()
            return jsonify({'success': True})
        
        elif action == 'list':
            # Admin panel için lisans listesi
            c.execute("SELECT * FROM licenses ORDER BY created_at DESC")
            licenses = [dict(row) for row in c.fetchall()]
            return jsonify({'success': True, 'data': licenses})
        
        elif action == 'delete':
            c.execute("DELETE FROM licenses WHERE id = ?", (data.get('id'),))
            conn.commit()
            return jsonify({'success': True})
        
        conn.close()
        return jsonify({'valid': False, 'reason': 'Geçersiz action'})
        
    except Exception as e:
        return jsonify({'valid': False, 'reason': f'DB hatası: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
