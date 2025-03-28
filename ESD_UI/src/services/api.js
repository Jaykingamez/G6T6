import axios from 'axios';

// Replace with your actual API base URLs - adjust based on your deployment configuration
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5004'; // Composite service
const SAVED_ROUTES_SERVICE_URL = process.env.VUE_APP_SAVED_ROUTES_URL || 'http://localhost:5006'; // Atomic service
const PLAN_JOURNEY_API = process.env.VUE_APP_PLAN_JOURNEY_API || 'http://localhost:5031'; // Plan Journey service

// Function to get journey options based on start and end points
export const getJourneyOptions = async (startPoint, endPoint) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/journeys`, {
            params: {
                start: startPoint,
                end: endPoint
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching journey options:', error);
        throw error;
    }
};

// Function to call the plan_journey composite service
export const planJourney = async (origin, destination, passengerType = 'adult', peakHour = true) => {
    try {
        console.log(`Calling plan_journey API with origin: ${origin}, destination: ${destination}`);
        const response = await axios.get(`${PLAN_JOURNEY_API}/plan_journey`, {
            params: {
                origin,
                destination,
                peakHour,
                passengerType,
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error planning journey:', error);
        throw error;
    }
};

// Function to save a journey
export const saveJourney = async (journeyData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/routes/save`, journeyData);
        return response.data;
    } catch (error) {
        console.error('Error saving journey:', error);
        throw error;
    }
};

// Function to get saved journeys for a user
export const getSavedJourneys = async (userId) => {
    console.log('Fetching journeys for user ID:', userId); // Debug log
    
    if (!userId) {
        console.error('Missing userId in getSavedJourneys call');
        throw new Error('User ID is required');
    }
    
    try {
        // Direct call to the selectedRoute microservice
        const directResponse = await axios.get(`http://localhost:5301/selectedroute/user/${userId}`, {
            // Add timeout and additional headers
            timeout: 10000,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        return directResponse.data;
    } catch (error) {
        console.error('Error fetching saved journeys:', error);
        
        // Return a default response for development
        if (process.env.NODE_ENV === 'development') {
            console.log('Returning mock data in development mode');
            return {
                code: 200,
                data: {
                    routes: [],
                    count: 0
                }
            };
        }
        
        throw error;
    }
};

// Function to delete a saved journey
export const deleteJourney = async (routeId) => {
    try {
        // Call the composite service first (preferred way)
        const response = await axios.delete(`${API_BASE_URL}/routes/${routeId}`);
        return response.data;
    } catch (error) {
        console.error('Error deleting journey from composite service:', error);
        
        // Fallback to direct atomic service call if composite fails
        try {
            const directResponse = await axios.delete(`${SAVED_ROUTES_SERVICE_URL}/saved_routes/${routeId}`);
            return directResponse.data;
        } catch (fallbackError) {
            console.error('Error deleting journey from atomic service:', fallbackError);
            throw fallbackError;
        }
    }
};