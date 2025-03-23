import axios from 'axios';

// Replace with your actual API base URLs - adjust based on your deployment configuration
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5004'; // Composite service
const SAVED_ROUTES_SERVICE_URL = process.env.VUE_APP_SAVED_ROUTES_URL || 'http://localhost:5006'; // Atomic service

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
    try {
        // Call the composite service first (preferred way)
        const response = await axios.get(`${API_BASE_URL}/routes/user/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching saved journeys from composite service:', error);
        
        // Fallback to direct atomic service call if composite fails
        try {
            const directResponse = await axios.get(`${SAVED_ROUTES_SERVICE_URL}/saved_routes/user/${userId}`);
            return directResponse.data;
        } catch (fallbackError) {
            console.error('Error fetching saved journeys from atomic service:', fallbackError);
            throw fallbackError;
        }
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