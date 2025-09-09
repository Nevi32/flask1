from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# MobiTech API base URL
MOBITECH_BASE_URL = "https://app.mobitechtechnologies.com/sms"

def handler(request):
    """
    Send SMS via MobiTech API
    Expected JSON payload:
    {
        "api_key": "your_api_key",
        "mobile": "+254712345678",
        "message": "Your message",
        "sender_name": "BULK_SMS",
        "service_id": 0
    }
    """
    if request.method != 'POST':
        return jsonify({
            "error": "Method not allowed",
            "message": "Only POST requests are allowed"
        }), 405
    
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['api_key', 'mobile', 'message', 'sender_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
        
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
        response = requests.post(
            f"{MOBITECH_BASE_URL}/sendsms",
            headers=headers,
            json=mobitech_payload,
            timeout=15
        )
        
        # Return the response from MobiTech
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "SMS API request failed",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Request timeout - SMS service took too long to respond"
        }), 408
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Failed to connect to SMS service",
            "details": str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500