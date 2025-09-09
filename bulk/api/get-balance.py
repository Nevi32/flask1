from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# MobiTech API base URL
MOBITECH_BASE_URL = "https://app.mobitechtechnologies.com/sms"

@app.route('/api/get-balance', methods=['POST', 'OPTIONS'])
def get_balance():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            response = jsonify({"error": "No JSON data provided"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Validate required fields
        if 'api_key' not in data or not data['api_key']:
            response = jsonify({"error": "Missing required field: api_key"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Prepare payload for MobiTech API
        mobitech_payload = {
            "response_type": data.get('response_type', 'json')
        }
        
        # Set up headers
        headers = {
            'h_api_key': data['api_key'],
            'Content-Type': 'application/json'
        }
        
        # Make request to MobiTech API
        response_data = requests.get(
            f"{MOBITECH_BASE_URL}/getbalance",
            headers=headers,
            json=mobitech_payload,
            timeout=15
        )
        
        # Return the response from MobiTech
        response = jsonify(response_data.json())
        response.headers.add('Access-Control-Allow-Origin', '*')
        
        if response_data.status_code == 200:
            return response
        else:
            error_response = jsonify({
                "error": "Balance API request failed",
                "status_code": response_data.status_code,
                "response": response_data.text
            })
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            return error_response, response_data.status_code
            
    except requests.exceptions.Timeout:
        response = jsonify({"error": "Request timeout - Balance service took too long to respond"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 408
    
    except requests.exceptions.RequestException as e:
        response = jsonify({"error": "Failed to connect to balance service", "details": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500
    
    except Exception as e:
        response = jsonify({"error": "Internal server error", "details": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# For Vercel serverless functions
def handler(request):
    with app.test_request_context(request.path, method=request.method, headers=dict(request.headers), data=request.data):
        return app.dispatch_request()
