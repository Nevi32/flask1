from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    # Handle CORS preflight
    response = jsonify({
        "status": "healthy",
        "message": "BulkSMS API is running on Vercel",
        "endpoints": [
            "/api/send-sms",
            "/api/get-balance",
            "/api/health"
        ]
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# For Vercel serverless functions
def handler(request):
    with app.test_request_context(request.path, method=request.method, headers=dict(request.headers), data=request.data):
        return app.dispatch_request()
