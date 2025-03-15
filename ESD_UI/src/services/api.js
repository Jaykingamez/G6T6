import axios from 'axios';

const API_BASE_URL = 'https://api.example.com'; // Replace with your actual API base URL

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
        const response = await axios.post(`${API_BASE_URL}/journeys`, journeyData);
        return response.data;
    } catch (error) {
        console.error('Error saving journey:', error);
        throw error;
    }
};

// Function to get saved journeys for a user
export const getSavedJourneys = async (userId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/users/${userId}/journeys`);
        return response.data;
    } catch (error) {
        console.error('Error fetching saved journeys:', error);
        throw error;
    }
};

// Function to delete a saved journey
export const deleteJourney = async (journeyId) => {
    try {
        const response = await axios.delete(`${API_BASE_URL}/journeys/${journeyId}`);
        return response.data;
    } catch (error) {
        console.error('Error deleting journey:', error);
        throw error;
    }
};