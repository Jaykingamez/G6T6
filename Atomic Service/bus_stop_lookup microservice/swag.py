@swag_from({
    "tags": ["Bus Stop"],
    "summary": "Find the nearest bus stop",
    "description": (
        "Extracts the first transit step from a Google Maps Directions API response "
        "and maps it to a nearby bus stop, returning the bus stop code, description, "
        "and bus number."
    ),
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["routes"],
                "properties": {
                    "routes": {
                        "type": "array",
                        "description": "List of route options from Google Maps Directions API",
                        "items": {
                            "type": "object",
                            "properties": {
                                "legs": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "steps": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "travel_mode": {
                                                            "type": "string",
                                                            "description": "Mode of transport (must be 'TRANSIT')",
                                                            "example": "TRANSIT"
                                                        },
                                                        "transit_details": {
                                                            "type": "object",
                                                            "required": ["departure_stop", "line"],
                                                            "properties": {
                                                                "departure_stop": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                        "location": {
                                                                            "type": "object",
                                                                            "required": ["lat", "lng"],
                                                                            "properties": {
                                                                                "lat": {
                                                                                    "type": "number",
                                                                                    "description": "Latitude of the departure bus stop",
                                                                                    "example": 1.290270
                                                                                },
                                                                                "lng": {
                                                                                    "type": "number",
                                                                                    "description": "Longitude of the departure bus stop",
                                                                                    "example": 103.851959
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "line": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                        "name": {
                                                                            "type": "string",
                                                                            "description": "Bus route name or number",
                                                                            "example": "Bus 36"
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "required": ["travel_mode", "transit_details"]
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "example": {
                    "routes": [
                        {
                            "legs": [
                                {
                                    "steps": [
                                        {
                                            "travel_mode": "TRANSIT",
                                            "transit_details": {
                                                "departure_stop": {
                                                    "location": {
                                                        "lat": 1.290270,
                                                        "lng": 103.851959
                                                    }
                                                },
                                                "line": {
                                                    "name": "Bus 36"
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Nearest bus stop found",
            "schema": {
                "type": "object",
                "properties": {
                    "BusStopCode": {
                        "type": "string",
                        "description": "Unique identifier for the bus stop",
                        "example": "01012"
                    },
                    "Description": {
                        "type": "string",
                        "description": "Name of the bus stop",
                        "example": "Hotel Grand Pacific"
                    },
                    "BusNumber": {
                        "type": "string",
                        "description": "Bus route number",
                        "example": "Bus 36"
                    },
                    "DistanceToBusStop": {
                        "type": "number",
                        "description": "Distance in meters from the detected location to the nearest bus stop",
                        "example": 15.2
                    }
                }
            }
        },
        "400": {
            "description": "Invalid request - no public transport step found",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "No public transport step found in provided route data."
                    }
                }
            }
        },
        "422": {
            "description": "Invalid data format",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Missing required fields: routes. Expected Google Maps Directions API format."
                    }
                }
            }
        }
    }
})
