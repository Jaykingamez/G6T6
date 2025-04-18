# G6T6

## NavSmart SG

A microservices-based public transport journey planning system that provides route planning, real-time bus arrivals, fare estimation, and carbon footprint calculation.

## Architecture

Project consists of the following microservices:

1. **Plan Journey Orchestrator** - Coordinates calls to all other services and aggregates responses
2. **Estimate Journey Costs** - Orchestrator that calculates total journey costs
3. **Direction Service** - Interacts with Google Maps Directions API to fetch route information
4. **Bus Stop Lookup Service** - Retrieves bus stop details from Redis
5. **Bus Tracking Service** - Fetches real-time transport timing from the LTA API
6. **Bus Fare Calculation Service** - Computes the fare for bus ride
7. **Train Fare Calculation Service** - Computes the fare for train
8. **Emission Service** - Calculates carbon footprint for journeys
8. **User** - Stores User data with CRUD operation
9. **Card** - Stores Ez-Link Card data with CRUD operation
10. **Transcation** - Stores Transaction data with CR operation (Outsystems)
11. **Notification** - Calls external API to send notification
12. **Payment** - Calls external API to payment gateway
13. **Check Balance** - Orchestrator that retrieve user's card balance
14. **Top Up** - Orchestrator that top up user's card balance
15. **Make Payment** - Orchestrator that process payment and update card balance
16. **Notify Me Starter** - Orchestrator Starter for Notify Me service
17. **Notify Me** - Orchestrator that process notification request
18. **SelectedRoute** - Stores Routes data with CRUD operation




## Prerequisites

- Docker
- WAMP/MAMP
- Google Maps API key
- LTA API Key
- Twilio Credentials

## Environment Variables

Add your API keys in `.env` file in the root directory:

```
GOOGLE_MAPS_API_KEY='YOUR_GOOGLE_MAPS_API_KEY'
LTA_API_KEY="YOUR_LTA_API_KEY"
TWILIO_ACCOUNT_SID="YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER="YOUR_TWILIO_PHONE_NUMBER"
STRIPE_SECRET_KEY="YOUR_STRIPE_API_KEY"
```

## Running the System

1. Clone the repository
2. Set up environment variables
3. Start all services:

```bash
docker-compose up --build
```
4. cd into the ESD_UI directory and run npm install 

## API Endpoints

The system exposes the following API endpoints:

- **Directions**: `GET http://localhost:5001/directions`
- **Bus Stop Lookup**: `POST http://localhost:5002/bus_stop_lookup`
- **Bus Tracking**: `GET/POST http://localhost:5030/bus-tracking`
- **Bus Fare**: `GET http://localhost:5003/bus-fare`
- **Train Fare**: `GET http://localhost:5004/train-fare`
- **Emission**: `GET http://localhost:5005/emission`
- **User**: `GET http://localhost:5201/users`
- **Card**: `GET http://localhost:5203/cards`
- **Transaction**: `GET https://personal-tkjmxw54.outsystemscloud.com/TransactionManagement/rest/TransactionsAPI/#/TransactionsAPI/GetTransactionsByCardId`
- **Check Balance**: `GET http://localhost:5205/checkbalance`
- **Make Payment**: `GET http://localhost:5208/makepayment`
- **Route**: `http://localhost:5301/selectedroute`
- **start notify me**: `http://localhost:5302/notify-me`

API documentation is available at:
- All services: `http://localhost:5000/apidocs/`
- Directions service: `http://localhost:5001/apidocs`
- Bus Stop service: `http://localhost:5002/apidocs`

## Note for macOS Users
If you are using macOS, port 5000 might be used by AirDrop and Handoff.To disable these features, go to System Settings > General > AirDrop and Handoff, and disable both AirDrop and AirPlay Receiver.
