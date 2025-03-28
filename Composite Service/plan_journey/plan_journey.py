# TODO Handling erroneous inputs and exceptions
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
            # Step 1: Get directions
            directions_response = await get_directions(session, origin, destination)
            if "error" in directions_response:
                return jsonify(directions_response), 500
            
            # Step 2, 3, & 4: Look up bus stops, calculate fare, and get emissions in parallel
            # All depend on directions_response
            bus_stops_task = asyncio.create_task(lookup_bus_stops(session, directions_response))
            fare_calc_task = asyncio.create_task(calculate_fare(session, directions_response, passenger_type, peak_hour))
            emissions_task = asyncio.create_task(get_emissions_for_routes(session, directions_response))
            
            # Await all tasks to complete
            bus_stops_response, fare_response, emissions_response = await asyncio.gather(
                bus_stops_task, fare_calc_task, emissions_task
            )
            
            # Check for errors in parallel responses
            if "error" in bus_stops_response:
                return jsonify(bus_stops_response), 500
            if "error" in fare_response:
                return jsonify(fare_response), 500
            if "error" in emissions_response:
                return jsonify(emissions_response), 500
            
            # Step 5: Get bus tracking info (depends on bus_stops_response)
            bus_tracking_response = await get_bus_tracking(session, bus_stops_response)
            if "error" in bus_tracking_response:
                return jsonify(bus_tracking_response), 500
            
            # Step 6: Combine all responses
            combined_response = {
                "directions": directions_response,
                # "busStops": bus_stops_response,
                "fareCosts": fare_response,
                "emissions": emissions_response,
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

async def get_emissions_for_routes(session, directions_data):
    """Get emissions data for all routes in the directions response"""
    try:
        # Extract routes from the directions data
        routes = directions_data.get('routes', [])
        if not routes:
            return {"error": "No routes found in directions data"}
        
        # Process each route to get emissions
        emissions_results = []
        for route_index, route in enumerate(routes):
            route_emissions = []
            total_emissions = 0
            
            # Process each leg and step in the route
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    # Get travel mode and distance
                    travel_mode = step.get("travel_mode", "").lower()
                    
                    # Extract distance in meters and convert to kilometers
                    distance_m = step.get("distance", {}).get("value", 0)
                    distance_km = distance_m / 1000
                    
                    # Skip steps with zero distance
                    if distance_km <= 0:
                        continue
                    
                    # Determine the actual mode of transport
                    if travel_mode == "transit":
                        transit_details = step.get("transit_details", {})
                        line_info = transit_details.get("line", {})
                        vehicle_type = line_info.get("vehicle", {}).get("type", "").lower()
                        
                        # Map Google's vehicle types to your emissions API's supported modes
                        if vehicle_type in ["bus", "bus_service"]:
                            mode = "bus"
                        elif vehicle_type in ["subway", "train", "heavy_rail", "commuter_train", "rail"]:
                            mode = "train"
                        else:
                            # Default to bus for other transit types
                            mode = "bus"
                    else:
                        # Map non-transit modes to supported emission modes
                        if travel_mode == "driving":
                            mode = "car"
                        elif travel_mode == "walking" or travel_mode == "bicycling":
                            # Skip walking/cycling as they have zero emissions
                            continue
                        else:
                            # Default to bus for unknown modes
                            mode = "bus"
                    
                    # Call emissions API for this segment
                    emissions_data = await get_emissions(session, mode, distance_km)
                    
                    if "error" in emissions_data:
                        return emissions_data
                    
                    # Add step details to the emissions data
                    emissions_data['mode'] = mode
                    emissions_data['distance_km'] = distance_km
                    route_emissions.append(emissions_data)
                    
                    # Add to total emissions (using the 'emission_kg_co2' field)
                    total_emissions += emissions_data.get('emission_kg_co2', 0)
            
            # Create a summary for this route
            route_summary = {
                'routeIndex': route_index,
                'totalEmissions': total_emissions,
                'segments': route_emissions
            }
            
            emissions_results.append(route_summary)
        
        return {"routeEmissions": emissions_results}
            
    except Exception as e:
        return {"error": f"Error processing emissions data: {str(e)}"}

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