from flask import Flask, request, jsonify, render_template, render_template_string, redirect, url_for
import sys
import sqlite3
from waf_bypass import WAFBypassDetector, WAFBypassFeatureExtractor

# Fix for pickle loading: Ensure classes are available in __main__
sys.modules['__main__'].WAFBypassDetector = WAFBypassDetector
sys.modules['__main__'].WAFBypassFeatureExtractor = WAFBypassFeatureExtractor

from waf_bypass import predict_payload_kali, load_models

app = Flask(__name__)

# Ensure models are loaded at startup
load_models()

# --- WAF Middleware ---
@app.before_request
def waf_check():
    # Skip static files if any (though we don't have any right now)
    if request.path.startswith('/static') or request.path == '/favicon.ico':
        return

    # Construct payload for WAF analysis
    method = request.method
    full_path = request.full_path if request.query_string else request.path
    if not full_path.startswith('/'):
        full_path = '/' + full_path
        
    payload = f"{method} {full_path} HTTP/1.1\n"
    for header, value in request.headers:
        payload += f"{header}: {value}\n"
    payload += "\n"
    if request.data:
        try:
            body_str = request.data.decode('utf-8', errors='ignore')
            if body_str:
                payload += body_str
        except Exception:
            pass
    
    # Form data is also part of the body in a way, let's append it if present
    if request.form:
        for k, v in request.form.items():
            payload += f"{k}={v}&"

    print(f"\n{'='*60}")
    print(f"Incoming Request: {method} {full_path}")
    print(f"{'-'*60}")
    
    prediction_label, threat_probability = predict_payload_kali(payload)
    
    print(f"{'-'*60}")
    
    # CONFIDENCE THRESHOLD CHECK
    # The anomaly detector (IsolationForest) might return 1 (Attack) even if the 
    # ensemble probability is low. We only block if confidence is > 50%.
    if prediction_label == 1 and threat_probability > 0.5:
        print(f"🚫 ACTION: BLOCKED | Confidence: {threat_probability*100:.2f}%")
        print(f"{'='*60}\n")
        return jsonify({
            "status": "blocked",
            "reason": "WAF Detection",
            "confidence": f"{threat_probability*100:.2f}%",
            "details": "Request blocked by WAF."
        }), 403
    elif prediction_label == 1:
        print(f"⚠️ ACTION: ALLOWED (Low Confidence) | Confidence: {threat_probability*100:.2f}%")
        print(f"{'='*60}\n")
    else:
        print(f"✅ ACTION: ALLOWED | Confidence: {(1-threat_probability)*100:.2f}%")
        print(f"{'='*60}\n")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sqli', methods=['GET', 'POST'])
def sqli():
    message = None
    success = False
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # VULNERABLE SQL LOGIC
        # Simulating a database query
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"[App] Executing SQL: {query}")
        
        # Simple check for bypass
        # If the query contains ' OR '1'='1 it becomes true
        if "OR '1'='1" in query or "admin" in username and "OR" in query:
             # Simulated successful bypass
             message = f"Login Successful! Welcome, admin. (Query: {query})"
             success = True
        elif username == 'admin' and password == 'password123':
             message = "Login Successful! Welcome, admin."
             success = True
        else:
             message = "Invalid credentials."
             success = False
             
    return render_template('sqli.html', message=message, success=success)

@app.route('/xss', methods=['GET'])
def xss():
    query = request.args.get('q', '')
    return render_template('xss.html', query=query)

@app.route('/ssti', methods=['GET', 'POST'])
def ssti():
    result = None
    if request.method == 'POST':
        name = request.form.get('name', '')
        # VULNERABLE SSTI LOGIC
        template = f"Hello, {name}!"
        try:
            result = render_template_string(template)
        except Exception as e:
            result = f"Error: {e}"
            
    return render_template('ssti.html', result=result)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 VULNERABLE APP WITH WAF PROTECTION STARTED 🔥")
    print("Listening on http://0.0.0.0:5000")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
