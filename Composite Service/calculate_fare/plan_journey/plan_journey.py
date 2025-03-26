from flask import Flask, request, jsonify
import asyncio
import aiohttp  # Async HTTP requests

app = Flask(__name__)

# Mock API Endpoints (Replace with actual API URLs)
DIRECTIONS_API = "http://localhost:5001/directions"
BUS_STOP_LOOKUP_API = "http://localhost:5002/bus_stop_lookup"
CALCULATE_FARE_API = "http://localhost:5032/calculate-fare"
BUS_TRACKING_API = "http://localhost:5030/bus-tracking"

@app.route('/plan_journey', methods=['GET'])
def plan_journey():
    """API Endpoint for journey planning - orchestrates multiple service calls"""
    # Extract all required parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    passenger_type = request.args.get('passengerType', 'adult')  # Default to adult if not specified
    peak_hour = request.args.get('peakHour', 'false').lower() == 'true'  # Convert to boolean, default false
    
    # Validate required parameters
    if not origin or not destination:
        return jsonify({"error": "Both origin and destination parameters are required"}), 400
    
    # Since we're using async functions in a Flask app, we need to run the async function in the event loop
    return asyncio.run(orchestrate_journey_planning(origin, destination, passenger_type, peak_hour))

async def orchestrate_journey_planning(origin, destination, passenger_type, peak_hour):
    """Orchestrate the calls to various APIs to plan a complete journey"""
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Get directions
            directions_response = await get_directions(session, origin, destination)
            if "error" in directions_response:
                return jsonify(directions_response), 500
            
            # Step 2 & 3: Look up bus stops and calculate fare in parallel
            # Both only depend on directions_response
            bus_stops_task = asyncio.create_task(lookup_bus_stops(session, directions_response))
            fare_calc_task = asyncio.create_task(calculate_fare(session, directions_response, passenger_type, peak_hour))
            
            # Await both tasks to complete
            bus_stops_response, fare_response = await asyncio.gather(bus_stops_task, fare_calc_task)
            
            # Check for errors in parallel responses
            if "error" in bus_stops_response:
                return jsonify(bus_stops_response), 500
            if "error" in fare_response:
                return jsonify(fare_response), 500
            
            # Step 4: Get bus tracking info (depends on bus_stops_response)
            bus_tracking_response = await get_bus_tracking(session, bus_stops_response)
            if "error" in bus_tracking_response:
                return jsonify(bus_tracking_response), 500
            
            # Step 5: Combine all responses
            combined_response = {
                "directions": directions_response,
                # "busStops": bus_stops_response,
                "fareCosts": fare_response,
                "busTracking": bus_tracking_response
            }
            
            return jsonify(combined_response)
            
        except Exception as e:
            return jsonify({"error": f"Error in journey planning: {str(e)}"}), 500

async def get_directions(session, origin, destination):
    """Get directions from the directions API"""
    params = {
        'origin': origin,
        'destination': destination
    }
    
    try:
        async with session.get(DIRECTIONS_API, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {"error": f"Directions API error: {error_text}"}
    except Exception as e:
        return {"error": f"Error connecting to directions service: {str(e)}"}

async def lookup_bus_stops(session, directions_data):
    """Look up bus stops using the bus stop lookup API"""
    try:
        async with session.post(BUS_STOP_LOOKUP_API, json=directions_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {"error": f"Bus Stop Lookup API error: {error_text}"}
    except Exception as e:
        return {"error": f"Error connecting to bus stop lookup service: {str(e)}"}

async def calculate_fare(session, directions_data, passenger_type, peak_hour):
    """Calculate fare using the fare calculation API"""
    # Add passenger-specific parameters to the directions data
    payload = {
        **directions_data,  # Include all directions data
        "passengerType": passenger_type,
        "peakHour": peak_hour
    }
    
    try:
        async with session.post(CALCULATE_FARE_API, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {"error": f"Calculate Fare API error: {error_text}"}
    except Exception as e:
        return {"error": f"Error connecting to fare calculation service: {str(e)}"}

async def get_bus_tracking(session, bus_stops_data):
    """Get bus tracking information"""
    try:
        async with session.post(BUS_TRACKING_API, json=bus_stops_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {"error": f"Bus Tracking API error: {error_text}"}
    except Exception as e:
        return {"error": f"Error connecting to bus tracking service: {str(e)}"}

if __name__ == '__main__':
    app.run(debug=True, port=5031)