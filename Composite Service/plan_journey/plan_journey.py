from flask import Flask, request, jsonify
import asyncio
import aiohttp  # Async HTTP requests
from flask_cors import CORS  # Import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Change from localhost references
DIRECTIONS_API = "http://directions:5001/directions"  # Instead of localhost:5001
BUS_STOP_LOOKUP_API = "http://bus_stop_lookup:5002/bus_stop_lookup"  # Instead of localhost:5002
CALCULATE_FARE_API = "http://calculate_fare:5032/calculate-fare"  # Instead of localhost:5032
BUS_TRACKING_API = "http://bus_tracking:5030/bus-tracking"  # Instead of localhost:5030
EMISSIONS_API = "http://emission:5005/emission"  # Instead of 127.0.0.1:5005

@app.route('/plan_journey', methods=['GET'])
def plan_journey():
    """API Endpoint for journey planning - orchestrates multiple service calls"""
    # Extract all required parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    passenger_type = request.args.get('passengerType', 'adult')  # Default to adult if not specified
    peak_hour = request.args.get('peakHour', 'false').lower() == 'true'  # Convert to boolean, default false
    
    logger.debug(f"Planning journey - Origin: {origin}, Destination: {destination}, Type: {passenger_type}, Peak: {peak_hour}")
    
    # Validate required parameters
    if not origin or not destination:
        return jsonify({"error": "Both origin and destination parameters are required"}), 400
    
    # Since we're using async functions in a Flask app, we need to run the async function in the event loop
    return asyncio.run(orchestrate_journey_planning(origin, destination, passenger_type, peak_hour))

async def orchestrate_journey_planning(origin, destination, passenger_type, peak_hour):
    """Orchestrate the calls to various APIs to plan a complete journey"""
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Get directions (this must complete first)
            directions_response = await get_directions(session, origin, destination)
            if "error" in directions_response:
                return jsonify(directions_response), 500
            
            # Step 2: Create three parallel tasks:
            # - Task 1: Get bus stops and then immediately get bus tracking (in sequence)
            # - Task 2: Calculate fare
            # - Task 3: Calculate emissions
            
            # Task 1: Bus stops lookup followed immediately by bus tracking
            bus_chain_task = asyncio.create_task(
                get_bus_stops_and_tracking(session, directions_response)
            )
            
            # Task 2: Fare calculation
            fare_calc_task = asyncio.create_task(
                calculate_fare(session, directions_response, passenger_type, peak_hour)
            )
            
            # Task 3: Emissions calculation
            emissions_task = asyncio.create_task(
                get_route_emissions(session, directions_response)
            )
            
            # Await all three parallel tasks
            (bus_stops_response, bus_tracking_response), fare_response, emissions_response = await asyncio.gather(
                bus_chain_task, fare_calc_task, emissions_task
            )
            
            # Check for errors in responses
            if "error" in bus_stops_response:
                return jsonify(bus_stops_response), 500
            if "error" in bus_tracking_response:
                return jsonify(bus_tracking_response), 500
            if "error" in fare_response:
                return jsonify(fare_response), 500
            if "error" in emissions_response:
                return jsonify(emissions_response), 500
            
            # Combine all responses
            combined_response = {
                "directions": directions_response,
                # "busStops": bus_stops_response,  # Uncomment if needed in the response
                "fareCosts": fare_response,
                "emissions": emissions_response,
                "busTracking": bus_tracking_response
            }
            
            return jsonify(combined_response)
            
        except Exception as e:
            return jsonify({"error": f"Error in journey planning: {str(e)}"}), 500

async def get_bus_stops_and_tracking(session, directions_response):
    """
    Chain the bus stop lookup and bus tracking calls.
    Bus tracking starts immediately after bus stop lookup completes.
    Returns both responses.
    """
    # First get bus stops
    bus_stops_response = await lookup_bus_stops(session, directions_response)
    
    # If bus stops lookup failed, don't attempt bus tracking
    if "error" in bus_stops_response:
        return bus_stops_response, {"error": "Bus tracking skipped due to bus stop lookup failure"}
    
    # Immediately proceed to bus tracking with the bus stops data
    bus_tracking_response = await get_bus_tracking(session, bus_stops_response)
    
    # Return both responses
    return bus_stops_response, bus_tracking_response

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

async def get_route_emissions(session, directions_data):
    """Get emissions data for routes by passing directions data to the emissions service"""
    try:
        async with session.post(EMISSIONS_API, json=directions_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {"error": f"Route Emissions API error: {error_text}"}
    except Exception as e:
        return {"error": f"Error connecting to emissions service: {str(e)}"}

async def get_emissions(session, mode, distance):
    """Call the emissions API for a specific mode and distance"""
    # Ensure distance is a positive number
    try:
        distance_float = float(distance)
        if distance_float <= 0:
            return {"error": "Distance must be positive"}
    except (ValueError, TypeError):
        return {"error": "Invalid distance value"}
    
    # Ensure mode is supported by the emissions API
    supported_modes = ["car", "bus", "train"]
    if mode not in supported_modes:
        return {"error": f"Unsupported transport mode: {mode}"}
    
    params = {
        'mode': mode,
        'distance': str(distance_float)
    }
    
    try:
        async with session.get(EMISSIONS_API, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {"error": f"Emissions API error: {error_text}"}
    except Exception as e:
        return {"error": f"Error connecting to emissions service: {str(e)}"}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5031, debug=True)