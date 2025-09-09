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
    Get account balance via MobiTech API
    Expected JSON payload:
    {
        "api_key": "your_api_key",
        "response_type": "json"
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
        if 'api_key' not in data or not data['api_key']:
            return jsonify({
                "error": "Missing required field: api_key"
            }), 400
        
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
        response = requests.get(
            f"{MOBITECH_BASE_URL}/getbalance",
            headers=headers,
            json=mobitech_payload,
            timeout=15
        )
        
        # Return the response from MobiTech
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "Balance API request failed",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Request timeout - Balance service took too long to respond"
        }), 408
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Failed to connect to balance service",
            "details": str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500