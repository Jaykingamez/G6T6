<template>
  <div class="journey-card">
    <div class="card h-100 shadow-sm border-0">
      <div :class="['card-header', getTransportClass(transportMode)]">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">
            <span class="transport-icon me-2">
              <i :class="getTransportIcon(transportMode)"></i>
            </span>
            <h5 class="mb-0 fw-bold">{{ transportMode }}</h5>
          </div>
          <div v-if="departureTime && arrivalTime" class="time-badge">
            <small>{{ departureTime }} - {{ arrivalTime }}</small>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div class="journey-details">
          <div class="journey-summary mb-3">
            <div class="summary-grid">
              <div class="summary-item">
                <div class="summary-label">Time</div>
                <div class="summary-value">{{ travelTime }} mins</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">Cost</div>
                <div class="summary-value">${{ parseFloat(cost).toFixed(2) }}</div>
              </div>
              <div v-if="emission" class="summary-item">
                <div class="summary-label">CO₂</div>
                <div class="summary-value">{{ emission }} kg</div>
              </div>
            </div>
            <div v-if="distance" class="mt-2">
              <small class="text-muted">Total distance: {{ distance }}</small>
            </div>
          </div>
          
          <div v-if="emission" class="journey-emissions mb-3">
            <div class="emission-bar-container">
              <div class="progress" style="height: 6px;">
                <div 
                  class="emission-progress-bar" 
                  role="progressbar" 
                  :style="{width: getEmissionIndicator(emission) + '%'}" 
                  :class="getEmissionClass(emission)">
                </div>
              </div>
              <div class="emission-label mt-1 d-flex justify-content-between">
                <small class="text-muted">Low Impact</small>
                <small class="text-muted">High Impact</small>
              </div>
            </div>
          </div>
          
          <hr class="my-3">
          
          <div v-if="steps && steps.length" class="journey-steps">
            <h6 class="mb-2">Journey Details</h6>
            <ul class="step-timeline mt-3">
              <li v-for="(step, index) in formatSteps(steps)" :key="index" class="step-item">
                <div class="step-content">
                  <div class="step-icon">
                    <i :class="getStepIcon(step.text)"></i>
                  </div>
                  <div class="step-info">
                    <span>{{ step.text }}</span>
                    <span v-if="step.busLoad" :class="getBusLoadClass(step.busLoad)" class="bus-load-badge ms-2">
                      {{ step.busLoad }}
                    </span>
                  </div>
                </div>
              </li>
            </ul>
          </div>
          
          <!-- Bus Notification Button - Only show for bus routes -->
          <div v-if="hasBusTransit" class="bus-notification-container mt-4">
            <button 
              class="btn w-100" 
              :class="notificationEnabled ? 'btn-success' : 'btn-outline-primary'"
              @click="toggleBusNotification"
              :disabled="notificationLoading"
            >
              <i class="bi" :class="notificationIcon"></i>
              {{ notificationButtonText }}
              <span v-if="notificationLoading" class="spinner-border spinner-border-sm ms-1" role="status" aria-hidden="true"></span>
            </button>
            <small v-if="notificationError" class="text-danger d-block mt-1">
              {{ notificationError }}
            </small>
          </div>
        </div>
      </div>
      <div class="card-footer bg-white border-0">
        <div class="d-flex justify-content-between">
          <button 
            class="btn btn-outline-primary btn-sm" 
            @click="viewOnMap"
            title="View this route on the map">
            <i class="bi bi-map"></i> View Map
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="showNotificationToast" class="notification-toast" :class="{ 'fade-out': isNotificationFading }">
      <div class="notification-content">
        <div class="notification-icon">
          <i class="bi bi-bell-fill"></i>
        </div>
        <div class="notification-text">
          <h4>Notifications Enabled</h4>
          <p style="font-weight: bold;">You will receive notifications when Bus {{ notificationBusId }} arrives!</p>
        </div>
      </div>
      <div class="notification-progress">
        <div class="notification-timer-bar"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    transportMode: {
      type: String,
      required: true
    },
    travelTime: {
      type: Number,
      required: true
    },
    cost: {
      type: [Number, String],
      required: true
    },
    emission: {
      type: [Number, String],
      default: 0
    },
    distance: {
      type: String,
      default: ''
    },
    departureTime: {
      type: String,
      default: ''
    },
    arrivalTime: {
      type: String,
      default: ''
    },
    steps: {
      type: Array,
      default: () => []
    },
    routeIndex: {
      type: Number,
      default: 0
    },
    startPoint: {
      type: String,
      required: true
    },
    endPoint: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      notificationEnabled: false,
      notificationLoading: false,
      notificationError: null,
      routeID: null,
      showNotificationToast: false,
      isNotificationFading: false,
      notificationBusId: null
    };
  },
  computed: {
    // Add this new computed property before your existing computed properties
    currentUserId() {
      // Add debugging to see exactly what's in your store and localStorage
      console.log('Store user object:', this.$store?.state?.auth?.user);
      
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          console.log('LocalStorage user object:', user);
          return user.UserId || user.id || user.userId || user.UserID;
        } catch (e) {
          console.error('Error parsing user from localStorage:', e);
        }
      }
      
      if (this.$store && this.$store.state.auth && this.$store.state.auth.user) {
        return this.$store.state.auth.user.UserId || 
               this.$store.state.auth.user.id || 
               this.$store.state.auth.user.userId || 
               this.$store.state.auth.user.UserID;
      }
      
      console.warn('Could not find user ID in localStorage or store. Using default value.');
    },
    
    hasBusTransit() {
      // Check if this journey has any bus transit steps
      if (!this.steps || this.steps.length === 0) return false;
      
      return this.steps.some(step => 
        step.travel_mode === 'TRANSIT' && 
        step.transit_details && 
        step.transit_details.line && 
        step.transit_details.line.vehicle && 
        step.transit_details.line.vehicle.name === 'Bus'
      );
    },
    busTransitDetails() {
      // Get details of the first bus transit step
      if (!this.hasBusTransit) return null;
      
      const busStep = this.steps.find(step => 
        step.travel_mode === 'TRANSIT' && 
        step.transit_details && 
        step.transit_details.line && 
        step.transit_details.line.vehicle && 
        step.transit_details.line.vehicle.name === 'Bus'
      );
      
      if (!busStep) return null;
      
      return {
        busID: busStep.transit_details.line.short_name || busStep.transit_details.line.name,
        busStopCode: this.getBusStopCode(busStep),
        userID: this.currentUserId // Use the computed property instead of hardcoded value
      };
    },
    // Add a new computed property to get all bus services in the journey
    allBusTransitDetails() {
      if (!this.hasBusTransit) return [];
      
      const busSteps = this.steps.filter(step => 
        step.travel_mode === 'TRANSIT' && 
        step.transit_details && 
        step.transit_details.line && 
        step.transit_details.line.vehicle && 
        step.transit_details.line.vehicle.name === 'Bus'
      );
      
      // Since we can't use async in computed properties, we'll just return the basic info
      // The bus stop codes will be fetched when needed in toggleBusNotification
      return busSteps.map(busStep => ({
        busID: busStep.transit_details.line.short_name || busStep.transit_details.line.name,
        transitDetails: busStep.transit_details, // Store full transit details for later use
        userID: this.currentUserId // Use the computed property instead of hardcoded value
      }));
    },
    notificationButtonText() {
      if (this.notificationEnabled) {
        return 'Bus Notifications Enabled';
      }
      return 'Enable Bus Notifications';
    },
    notificationIcon() {
      if (this.notificationEnabled) {
        return 'bi-bell-fill';
      }
      return 'bi-bell';
    }
  },
  methods: {
    getTransportClass(mode) {
      const modeMap = {
        'Bus': 'bg-primary text-white',
        'MRT': 'bg-success text-white',
        'Walking': 'bg-info text-white',
        'Taxi': 'bg-warning text-dark',
        'Mixed': 'bg-secondary text-white'
      };
      return modeMap[mode] || 'bg-secondary text-white';
    },
    getTransportIcon(mode) {
      const iconMap = {
        'Bus': 'bi bi-bus-front',
        'MRT': 'bi bi-train-front',
        'Walking': 'bi bi-person-walking',
        'Taxi': 'bi bi-taxi-front',
        'Mixed': 'bi bi-arrow-repeat'
      };
      return iconMap[mode] || 'bi bi-signpost-2';
    },
    getStepIcon(step) {
      if (step.includes('Bus')) return 'bi bi-bus-front';
      if (step.includes('MRT') || step.includes('train') || step.includes('subway')) return 'bi bi-train-front';
      if (step.includes('Walk')) return 'bi bi-person-walking';
      return 'bi bi-arrow-right';
    },
    formatSteps(steps) {
      // Extract key information from steps to display a summary
      const formattedSteps = [];
      
      for (const step of steps) {
        if (step.travel_mode === 'TRANSIT') {
          const transit = step.transit_details;
          if (transit) {
            let vehicleType = transit.line?.vehicle?.name || 'Transit';
            
            // Standardize subway references to MRT
            if (vehicleType.toLowerCase() === 'subway') {
              vehicleType = 'MRT';
            }
            
            const routeName = transit.line?.short_name || transit.line?.name || '';
            const stops = transit.num_stops || 0;
            
            // Get departure and arrival stop information
            const departureStop = transit.departure_stop?.name || '';
            const arrivalStop = transit.arrival_stop?.name || '';
            const destination = transit.headsign || transit.arrival_stop?.name || '';
            
            // Create step text based on the type of transit
            let stepText;
            if (vehicleType === 'MRT') {
              stepText = `${vehicleType} ${routeName} to ${destination} (${stops} stops)`;
            } else if (vehicleType === 'Bus') {
              // For buses, show both departure and arrival stops
              stepText = `${vehicleType} ${routeName}: ${departureStop} to ${arrivalStop} (${stops} stops)`;
            } else {
              stepText = `${vehicleType} ${routeName} (${stops} stops)`;
            }
            
            // Add bus load info if available and it's a bus
            let busLoad = null;
            if (vehicleType === 'Bus' && step.bus_load_description) {
              busLoad = step.bus_load_description;
            }
            
            formattedSteps.push({
              text: stepText,
              busLoad: busLoad
            });
          }
        } else if (step.travel_mode === 'WALKING') {
          // Only include walking steps that are substantial
          if (step.distance && step.distance.value > 100) {
            formattedSteps.push({
              text: `Walk ${step.distance.text}`,
              busLoad: null
            });
          }
        }
      }
      
      // Limit to 3 key steps maximum
      return formattedSteps.slice(0, 3);
    },
    getBusLoadClass(loadDescription) {
      // Style different load levels with different colors
      if (loadDescription === 'Seats Available') return 'bg-success text-white';
      if (loadDescription === 'Standing Available') return 'bg-warning text-dark';
      if (loadDescription === 'Limited Standing') return 'bg-danger text-white';
      return 'bg-secondary text-white';
    },
    getEmissionIndicator(emission) {
      // Scale the emissions to a percentage (0-100) for the progress bar
      // Assuming 5kg is the max that would reach 100%
      const maxEmission = 5;
      return Math.min(parseFloat(emission) / maxEmission * 100, 100);
    },
    getEmissionClass(emission) {
      const value = parseFloat(emission);
      if (value < 1) return 'bg-success';
      if (value < 2) return 'bg-info';
      if (value < 3) return 'bg-warning';
      return 'bg-danger';
    },
    viewOnMap() {
      this.$emit('view-on-map', {
        transportMode: this.transportMode,
        travelTime: this.travelTime,
        cost: this.cost,
        emission: this.emission,
        routeIndex: this.routeIndex,
        steps: this.steps
      });
    },
    // New methods for bus notification functionality
    async getBusStopCode(busStep) {
      // Get coordinates from the departure stop in transit details
      if (busStep?.transit_details?.departure_stop?.location) {
        const { lat, lng } = busStep.transit_details.departure_stop.location;
        
        try {
          // Call the bus stop lookup microservice
          const response = await fetch('http://localhost:8000/bus_stop_lookup', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              routes: [{
                legs: [{
                  steps: [{
                    travel_mode: 'TRANSIT',
                    transit_details: {
                      departure_stop: {
                        location: { lat, lng },
                        name: busStep.transit_details.departure_stop.name
                      },
                      line: {
                        name: busStep.transit_details.line.short_name || busStep.transit_details.line.name,
                        vehicle: {
                          type: 'BUS'
                        }
                      }
                    }
                  }]
                }]
              }]
            })
          });

          const data = await response.json();
          
          if (data.transit_details && data.transit_details.length > 0) {
            const busStopCode = data.transit_details[0].BusStopCode;
            console.log(`Found bus stop code ${busStopCode} for coordinates (${lat}, ${lng})`);
            return busStopCode;
          }
        } catch (error) {
          console.error('Error looking up bus stop code:', error);
        }
      }
      
      console.warn('Could not determine bus stop code for bus step:', busStep);
      return null;
    },
    async toggleBusNotification() {
      if (this.notificationLoading) return;
      
      this.notificationLoading = true;
      this.notificationError = null;
      
      try {
        // Get all bus details for this journey
        const allBusDetails = this.allBusTransitDetails;
        
        // Check if we have any bus details
        if (!allBusDetails || allBusDetails.length === 0) {
          throw new Error('No bus services found in this journey');
        }
        
        // Fetch bus stop codes for all buses
        const busDetailsWithCodes = await Promise.all(
          allBusDetails.map(async detail => {
            const busStep = {
              transit_details: detail.transitDetails
            };
            const busStopCode = await this.getBusStopCode(busStep);
            return {
              ...detail,
              busStopCode
            };
          })
        );
        
        // Check if any bus services are missing bus stop codes
        const missingCodes = busDetailsWithCodes.filter(detail => !detail.busStopCode);
        if (missingCodes.length > 0) {
          const missingBuses = missingCodes.map(detail => detail.busID).join(', ');
          throw new Error(`Missing bus stop codes for bus services: ${missingBuses}`);
        }
        
        // Generate a route name
        const routeName = `Journey from ${this.startPoint} to ${this.endPoint}`;
        
        // Track created routes
        const createdRoutes = [];
        
        // Create routes for each bus service
        for (const [index, busDetail] of busDetailsWithCodes.entries()) {
          const isFirstBus = index === 0;
          
          console.log(`Creating route for bus ${busDetail.busID} at stop ${busDetail.busStopCode}`);
          
          // Create the route
          const response = await fetch('http://localhost:8000/selectedroute', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              BusStopCode: busDetail.busStopCode,
              BusID: busDetail.busID,
              UserID: busDetail.userID,
              RouteName: routeName
            })
          });
          
          const data = await response.json();
          
          if (!response.ok || data.code !== 201) {
            console.error(`Failed to create route for bus ${busDetail.busID}:`, data);
            throw new Error(data.message || `Failed to save route for bus ${busDetail.busID}`);
          }
          
          const routeID = data.data.RouteID;
          console.log(`Created route with ID ${routeID} for bus ${busDetail.busID}`);
          
          // Enable notification only for the first bus using the RouteID
          if (isFirstBus) {
            const notificationResponse = await fetch(`http://localhost:8000/notify-me/${routeID}`, {
              method: 'GET'
            });
            
            const notificationData = await notificationResponse.json();
            
            if (!notificationResponse.ok) {
              console.error(`Failed to enable notifications for route ${routeID}:`, notificationData);
              throw new Error(notificationData.message || `Failed to enable notifications for route ${routeID}`);
            }
            
            console.log(`Enabled notifications for route ${routeID}`);
          }
          
          // Store the created route
          createdRoutes.push({
            routeID: routeID,
            busID: busDetail.busID,
            busStopCode: busDetail.busStopCode
          });
        }
        
        // Success!
        this.notificationEnabled = true;
        
        // Show toast notification
        this.notificationBusId = createdRoutes[0].busID;
        this.showNotificationToast = true;
        this.isNotificationFading = false;
        
        // Set timer to start fade out
        setTimeout(() => {
          this.isNotificationFading = true;
        }, 2700);
        
        // Hide notification after fade out animation completes
        setTimeout(() => {
          this.showNotificationToast = false;
          this.notificationBusId = null;
          this.isNotificationFading = false;
        }, 3000);
        
        // Emit an event to inform parent components
        this.$emit('notification-enabled', {
          routeID: createdRoutes[0].routeID,
          busID: createdRoutes[0].busID,
          busStopCode: createdRoutes[0].busStopCode,
          routeName: routeName,
          additionalRoutes: createdRoutes.slice(1),
          totalBusCount: allBusDetails.length
        });
        
      } catch (error) {
        console.error('Error setting up notifications:', error);
        this.notificationError = error.message || 'Failed to set up notifications';
        this.notificationEnabled = false;
      } finally {
        this.notificationLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.journey-card {
  height: 100%;
}

.card {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
}

.card-header {
  padding: 1rem;
  border-bottom: none;
}

.transport-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-badge {
  background: rgba(255,255,255,0.3);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 500;
}

/* Summary section styling */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.summary-item {
  text-align: center;
  padding: 0.5rem;
}

.summary-label {
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #212529;
}

/* Emissions styling */
.emission-bar-container {
  width: 100%;
}

.emission-progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.emission-progress-bar.bg-success {
  background-color: #10B981;
}

.emission-progress-bar.bg-info {
  background-color: #3B82F6;
}

.emission-progress-bar.bg-warning {
  background-color: #F59E0B;
}

.emission-progress-bar.bg-danger {
  background-color: #EF4444;
}

/* Journey steps styling - timeline look */
.step-timeline {
  list-style: none;
  padding-left: 0;
  position: relative;
}

.step-timeline::before {
  content: '';
  position: absolute;
  top: 0;
  left: 10px;
  height: 100%;
  width: 2px;
  background: #e9ecef;
  z-index: 0;
}

.step-item {
  position: relative;
  padding-bottom: 1.25rem;
}

.step-item:last-child {
  padding-bottom: 0;
}

.step-content {
  padding-left: 35px;
  position: relative;
}

.step-icon {
  position: absolute;
  left: 0;
  top: 0;
  width: 22px;
  height: 22px;
  background: #f8f9fa;
  border-radius: 50%;
  border: 2px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  z-index: 1;
}

.step-info {
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.bus-load-badge {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 20px;
  font-weight: 600;
}

/* Button styling */
.bus-notification-container {
  margin-bottom: 0.5rem;
}

.card-footer {
  padding: 1rem;
}

.btn-outline-primary, .btn-outline-success {
  font-weight: 500;
}

/* SimplyGO inspired transport colors */
.bg-primary {
  background-color: #0056b3 !important;
}

.bg-success {
  background-color: #00a651 !important;
}

.bg-warning {
  background-color: #ffb81c !important;
}

.bg-info {
  background-color: #3498db !important;
}

/* Toast styling remains the same */
.notification-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 1rem;
  width: 320px;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
  display: flex;
  flex-direction: column;
}

.notification-toast.fade-out {
  animation: slideOut 0.3s ease-in forwards;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.notification-icon {
  background: #ecfdf5;
  color: #059669;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
}

.notification-text h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

.notification-text p {
  margin: 0.25rem 0 0;
  font-size: 0.813rem;
  color: #6b7280;
}

.notification-progress {
  height: 3px;
  background: #e5e7eb;
  border-radius: 1.5px;
  overflow: hidden;
}

.notification-timer-bar {
  height: 100%;
  background: #059669;
  border-radius: 1.5px;
  width: 100%;
  animation: progress 3s linear forwards;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

@keyframes progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}
</style>