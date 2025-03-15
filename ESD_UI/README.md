# Singapore Journey Planner

## Overview
The Singapore Journey Planner is a modern web application designed to help users plan their journeys across Singapore. It features user authentication, journey planning, and the ability to save and view journeys. The application is built using Vue.js, Bootstrap, HTML, and CSS, ensuring a responsive and intuitive user experience.

## Features
- **User Authentication**: Users can create accounts, log in, and manage their profiles.
- **Journey Planning Interface**: Users can input start and end points with auto-suggestions for landmarks and MRT stations.
- **Results Display**: Journey options are displayed in responsive cards, showing transport modes, estimated travel time, and cost.
- **Saved Journeys**: Users can save their journeys and view them in a dashboard with options to edit or delete.
- **Responsive Design**: The application is fully responsive and mobile-friendly.

## Project Structure
```
singapore-journey-planner
├── public
│   ├── index.html
│   └── favicon.ico
├── src
│   ├── assets
│   │   └── logo.png
│   ├── components
│   │   ├── AuthComponents
│   │   │   ├── LoginForm.vue
│   │   │   └── RegisterForm.vue
│   │   ├── JourneyComponents
│   │   │   ├── JourneyForm.vue
│   │   │   ├── JourneyResults.vue
│   │   │   └── JourneyCard.vue
│   │   ├── SavedJourneyComponents
│   │   │   ├── SavedJourneyList.vue
│   │   │   └── SavedJourneyItem.vue
│   │   └── Common
│   │       ├── Navbar.vue
│   │       └── Footer.vue
│   ├── views
│   │   ├── Home.vue
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   ├── JourneyPlanner.vue
│   │   ├── SavedJourneys.vue
│   │   └── Profile.vue
│   ├── router
│   │   └── index.js
│   ├── store
│   │   ├── index.js
│   │   └── modules
│   │       ├── auth.js
│   │       └── journeys.js
│   ├── services
│   │   ├── api.js
│   │   ├── firebase.js
│   │   └── journeyService.js
│   ├── App.vue
│   └── main.js
├── .gitignore
├── babel.config.js
├── package.json
├── README.md
└── vue.config.js
```

## Setup Instructions
1. **Install Dependencies**: 
   ```
   npm install
   ```

2. **Run the Application**: 
   ```
   npm run serve
   ```

3. **Open in Browser**: Navigate to `http://localhost:8080` to view the application.

## Technologies Used
- **Vue.js**: For building the user interface.
- **Bootstrap**: For responsive design and styling.
- **Vue Router**: For managing application routes.
- **Vuex**: For state management.

