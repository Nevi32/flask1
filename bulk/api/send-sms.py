from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# MobiTech API base URL
MOBITECH_BASE_URL = "https://app.mobitechtechnologies.com/sms"

@app.route('/api/send-sms', methods=['POST', 'OPTIONS'])
def send_sms():
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
        required_fields = ['api_key', 'mobile', 'message', 'sender_name']
        for field in required_fields:
            if field not in data or not data[field]:
                response = jsonify({"error": f"Missing required field: {field}"})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 400
        
        # Prepare payload for MobiTech API
        mobitech_payload = {
            "mobile": data['mobile'],
            "response_type": "json",
            "sender_name": data['sender_name'],
            "service_id": data.get('service_id', 0),
            "message": data['message']
        }
        
        # Set up headers
        headers = {
            'h_api_key': data['api_key'],
            'Content-Type': 'application/json'
        }
        
        # Make request to MobiTech API
        response_data = requests.post(
            f"{MOBITECH_BASE_URL}/sendsms",
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
                "error": "SMS API request failed",
                "status_code": response_data.status_code,
                "response": response_data.text
            })
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            return error_response, response_data.status_code
            
    except requests.exceptions.Timeout:
        response = jsonify({"error": "Request timeout - SMS service took too long to respond"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 408
    
    except requests.exceptions.RequestException as e:
        response = jsonify({"error": "Failed to connect to SMS service", "details": str(e)})
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
