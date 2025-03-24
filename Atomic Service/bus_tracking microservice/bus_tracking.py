from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
from pathlib import Path
from werkzeug.exceptions import BadRequest
import requests
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# API endpoint
LTA_API_URL = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"

LTA_API_KEY = os.environ.get('LTA_API_KEY')
print(LTA_API_KEY)

if not LTA_API_KEY:
    raise ValueError("LTA API Key not found. Please set the LTA_API_KEY environment variable.")

# API key loaded from environment variables
HEADERS = {
    "AccountKey": LTA_API_KEY,
    "accept": "application/json"
}

async def fetch_bus_arrival_async(bus_number, bus_stop_code):
    """Fetch bus arrival information asynchronously"""
    async with aiohttp.ClientSession() as session:
        params = {
            "BusStopCode": bus_stop_code,
            "ServiceNo": bus_number
        }
        
        async with session.get(LTA_API_URL, headers=HEADERS, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "error": f"Failed to fetch data for bus {bus_number} at stop {bus_stop_code}",
                    "status_code": response.status
                }

def run_async_tasks(transit_details):
    """Run async tasks in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    results = []
    bus_tasks = []
    
    # Create tasks for each bus detail
    for detail in transit_details:
        if "BusNumber" in detail and "BusStopCode" in detail:
            bus_number = detail["BusNumber"]
            bus_stop_code = detail["BusStopCode"]
            
            task = asyncio.ensure_future(fetch_bus_arrival_async(bus_number, bus_stop_code))
            bus_tasks.append({
                "task": task,
                "detail": detail
            })
        elif "TrainLine" in detail:
            results.append({
                "transit_type": "train",
                "train_line": detail["TrainLine"],
                "message": "Train information not available from bus API"
            })
    
    # Wait for all tasks to complete
    if bus_tasks:
        task_group = asyncio.gather(*[task_info["task"] for task_info in bus_tasks])
        task_results = loop.run_until_complete(task_group)
        
        for i, task_result in enumerate(task_results):
            detail = bus_tasks[i]["detail"]
            results.append({
                "transit_type": "bus",
                "bus_number": detail["BusNumber"],
                "bus_stop_code": detail["BusStopCode"],
                "description": detail.get("Description", ""),
                "arrival_data": task_result
            })
    
    loop.close()
    return results

@app.route('/bus-tracking', methods=['GET'])
def get_bus_arrival():
    """
    Get bus arrival information for a specific bus stop and service number.
    ---
    parameters:
      - name: BusStopCode
        in: query
        type: string
        required: true
        description: LTA Bus Stop Code
      - name: ServiceNo
        in: query
        type: string
        required: true
        description: Bus Service Number
    responses:
      200:
        description: Successful response with bus arrival information
      400:
        description: Bad request (invalid input)
      500:
        description: Server error
    """
    try:
        bus_stop_code = request.args.get("BusStopCode")
        service_no = request.args.get("ServiceNo")
        
        # Validate inputs
        if not bus_stop_code:
            return jsonify({"error": "Missing BusStopCode parameter"}), 400
            
        if not service_no:
            return jsonify({"error": "Missing ServiceNo parameter"}), 400
        
        # Call the LTA API
        response = requests.get(
            LTA_API_URL,
            headers=HEADERS,
            params={"BusStopCode": bus_stop_code, "ServiceNo": service_no}
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": f"API request failed with status {response.status_code}",
                "response": response.text
            }), response.status_code
            
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@app.route('/bus-tracking', methods=['POST'])
def post_bus_arrival():
    """
    Get bus arrival information for multiple bus stops and service numbers.
    ---
    parameters:
      - name: transit_details
        in: body
        required: true
        schema:
          type: object
          properties:
            transit_details:
              type: array
              items:
                type: object
                properties:
                  BusNumber:
                    type: string
                  BusStopCode:
                    type: string
                  Description:
                    type: string
                  TrainLine:
                    type: string
    responses:
      200:
        description: Successful response with multiple bus arrival information
      400:
        description: Bad request (invalid input)
      500:
        description: Server error
    """
    try:
        data = request.json
        
        if not data or "transit_details" not in data:
            return jsonify({"error": "Missing transit_details in request body"}), 400
        
        transit_details = data["transit_details"]
        
        # Use ThreadPoolExecutor to run async code in a separate thread
        with ThreadPoolExecutor() as executor:
            results = executor.submit(run_async_tasks, transit_details).result()
        
        return jsonify({"results": results})
            
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5030, debug=True)