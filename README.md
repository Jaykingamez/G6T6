# G6T6

## Idea 1

A microservices-based public transport journey planning system that provides route planning, real-time bus arrivals, fare estimation, and carbon footprint calculation.

## Architecture

Project consists of the following microservices:

1. **Plan Journey Orchestrator** - Coordinates calls to all other services and aggregates responses
2. **Estimate Journey Costs** - Orchestrator that calculates total journey costs  
3. **Direction Service** - Interacts with Google Maps Directions API to fetch route information ✅
4. **Bus Stop Lookup Service** - Retrieves bus stop details from Redis ✅
5. **Bus Tracking Service** - Fetches real-time transport timing from the LTA API
6. **Fare Calculation Service** - Computes the fare for journeys
7. **Emission Service** - Calculates carbon footprint for journeys



## Prerequisites

- Docker
- Google Maps API key

## Environment Variables

Add your API keys in `.env` file in the root directory:

```
GOOGLE_MAPS_API_KEY='YOUR_GOOGLE_MAPS_API_KEY'
```

## Running the System

1. Clone the repository
2. Set up environment variables
3. Start all services:

```bash
docker-compose up
```


## API Endpoints

The system exposes the following API endpoints:

- **Directions**: `GET http://localhost:5001/directions`
- **Bus Stop Lookup**: `POST http://localhost:5002/bus_stop_lookup`

API documentation is available at:
- Directions service: `http://localhost:5001/apidocs`
- Bus Stop service: `http://localhost:5002/apidocs`