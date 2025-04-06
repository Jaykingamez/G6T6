<template>
  <div class="simplified-route-view">
    <div class="route-header">
      <div class="route-summary">
        <div class="route-time-distance">
          <h4>Estimated time: {{ journey.travelTime }} min</h4>
          <p v-if="journey.distance">{{ journey.distance }}</p>
        </div>
        <div class="route-cost">
          <div class="cost-badge">${{ formattedCost }}</div>
          <div v-if="journey.emission" class="emission-badge">
            <i class="bi bi-leaf-fill"></i>
            {{ journey.emission }} kg CO₂
          </div>
        </div>
      </div>
      <div class="departure-time" v-if="journey.departureTime">
        <span class="time">{{ journey.departureTime }}</span>
        <span class="arrival">Arrive at {{ journey.arrivalTime }}</span>
      </div>
    </div>
    
    <div class="journey-container">
      <div class="journey-timeline">
        <div class="start-point">
          <div class="timeline-dot start-dot"></div>
          <div class="timeline-content">
            <div class="location-name">{{ journey.startPoint }}</div>
            <div class="time-label" v-if="journey.departureTime">
              {{ journey.departureTime }}
            </div>
          </div>
        </div>
        
        <div class="transit-steps">
          <div v-for="(step, index) in formattedSteps" :key="index" class="transit-step">
            <div class="step-line" :class="getStepLineClass(step.mode)"></div>
            
            <div class="step-icon-container">
              <div class="step-icon" :class="getStepIconClass(step.mode)">
                <i :class="getStepIcon(step.mode)"></i>
              </div>
            </div>
            
            <div class="step-details">
              <div class="step-main">
                <template v-if="step.mode === 'MRT'">
                  <span class="transit-badge mrt">MRT</span>
                  <span>{{ step.text.replace('MRT ', '') }}</span>
                </template>
                <template v-else-if="step.mode === 'Bus'">
                  <span class="transit-badge bus">BUS</span>
                  <span>{{ step.text.replace('Bus ', '') }}</span>
                </template>
                <template v-else>
                  <span>{{ step.text }}</span>
                </template>
              </div>
              
              <div v-if="step.from && step.to" class="step-stations">
                <div class="station">
                  <div class="station-marker"></div>
                  <div class="station-name">{{ step.from }}</div>
                </div>
                <div class="station">
                  <div class="station-marker"></div>
                  <div class="station-name">{{ step.to }}</div>
                </div>
              </div>
              
              <div class="step-info">
                {{ step.details }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="end-point">
          <div class="timeline-dot end-dot"></div>
          <div class="timeline-content">
            <div class="location-name">{{ journey.endPoint }}</div>
            <div class="time-label" v-if="journey.arrivalTime">
              {{ journey.arrivalTime }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    journey: {
      type: Object,
      required: true
    }
  },
  computed: {
    formattedSteps() {
      if (!this.journey.steps || !this.journey.steps.length) {
        return ['Direct route - No detailed steps available'];
      }
      
      return this.formatSteps(this.journey.steps);
    },
    formattedCost() {
      try {
        // Add debugging to check the structure
        console.log('Journey object:', this.journey);
        
        // Check if journey has fareCosts with all_routes
        if (this.journey.fareCosts && 
            this.journey.fareCosts.all_routes && 
            Array.isArray(this.journey.fareCosts.all_routes)) {
            
          console.log('Found fareCosts.all_routes:', this.journey.fareCosts.all_routes);
          
          // Get route index (default to 0 if not provided)
          const routeIndex = this.journey.routeIndex !== undefined ? 
            this.journey.routeIndex : 0;
          
          console.log('Using route index:', routeIndex);
            
          // Check if the route exists at that index
          if (this.journey.fareCosts.all_routes[routeIndex]) {
            const totalFare = this.journey.fareCosts.all_routes[routeIndex].total_fare;
            console.log('Found total_fare:', totalFare);
            
            // Convert cents to dollars (divide by 100)
            return (parseFloat(totalFare) / 100).toFixed(2);
          }
        }
        
        // Check if journey response has fareCosts
        if (this.journey.journeyResponse && 
            this.journey.journeyResponse.fareCosts && 
            this.journey.journeyResponse.fareCosts.all_routes) {
            
          console.log('Found in journeyResponse:', this.journey.journeyResponse.fareCosts.all_routes);
          
          const routeIndex = this.journey.routeIndex !== undefined ? 
            this.journey.routeIndex : 0;
            
          if (this.journey.journeyResponse.fareCosts.all_routes[routeIndex]) {
            const totalFare = this.journey.journeyResponse.fareCosts.all_routes[routeIndex].total_fare;
            console.log('Found total_fare in journeyResponse:', totalFare);
            
            return (parseFloat(totalFare) / 100).toFixed(2);
          }
        }
        
        // Fallback to direct cost property if available
        if (this.journey.cost !== undefined) {
          console.log('Using direct cost:', this.journey.cost);
          return (parseFloat(this.journey.cost) / 100).toFixed(2);
        }
        
        // Default fallback
        console.log('No fare data found, using default 0.00');
        return '0.00';
      } catch (error) {
        console.error('Error calculating fare:', error);
        return '0.00';
      }
    }
  },
  methods: {
    formatSteps(steps) {
      const formattedSteps = [];
      
      for (const step of steps) {
        if (step.travel_mode === 'TRANSIT') {
          const transit = step.transit_details;
          if (transit) {
            const vehicleType = transit.line?.vehicle?.name || 'Transit';
            // Rename "Subway" to "MRT" for Singapore context
            const localizedVehicleType = vehicleType === 'Subway' ? 'MRT' : vehicleType;
            const routeName = transit.line?.short_name || transit.line?.name || '';
            const stops = transit.num_stops || 0;
            const duration = step.duration ? ` (${Math.round(step.duration.value / 60)} mins)` : '';
            
            // Get departure and arrival stop names
            const departureStop = transit.departure_stop?.name || '';
            const arrivalStop = transit.arrival_stop?.name || '';
            
            // Different formatting based on transit type
            if (localizedVehicleType === 'MRT') {
              formattedSteps.push({
                type: 'transit',
                mode: 'MRT',
                text: `${localizedVehicleType} ${routeName} to ${arrivalStop}`,
                details: `${stops} stops${duration}`,
                from: departureStop,
                to: arrivalStop
              });
            } else if (localizedVehicleType === 'Bus') {
              formattedSteps.push({
                type: 'transit',
                mode: 'Bus',
                text: `${localizedVehicleType} ${routeName}`,
                details: `${stops} stops${duration}`,
                from: departureStop,
                to: arrivalStop
              });
            } else {
              formattedSteps.push({
                type: 'transit',
                mode: localizedVehicleType,
                text: `${localizedVehicleType} ${routeName}`,
                details: `${stops} stops${duration}`,
                from: departureStop,
                to: arrivalStop
              });
            }
          }
        } else if (step.travel_mode === 'WALKING') {
          if (step.distance && step.distance.value > 100) {
            const duration = step.duration ? ` (${Math.round(step.duration.value / 60)} mins)` : '';
            formattedSteps.push({
              type: 'walking',
              text: `Walk ${step.distance.text}`,
              details: duration.trim() ? duration.substring(2) : ''
            });
          }
        }
      }
      
      return formattedSteps.length ? formattedSteps : [{
        type: 'direct',
        text: 'Direct route',
        details: 'No detailed steps available'
      }];
    },
    getStepIcon(mode) {
      switch (mode) {
        case 'MRT': return 'bi bi-train-front';
        case 'Bus': return 'bi bi-bus-front';
        case 'walking': return 'bi bi-person-walking';
        default: return 'bi bi-arrow-right';
      }
    },
    getStepIconClass(mode) {
      switch (mode) {
        case 'Bus': return 'bus-icon';
        case 'MRT': return 'mrt-icon';
        case 'walking': return 'walk-icon';
        default: return 'default-icon';
      }
    },
    getStepLineClass(mode) {
      switch (mode) {
        case 'Bus': return 'bus-line';
        case 'MRT': return 'mrt-line';
        case 'walking': return 'walk-line';
        default: return '';
      }
    },
    renderRoute(route, color = '#4299E1', weight = 6) {
      // Clear any existing route
      if (this.routePolyline) {
        this.map.removeLayer(this.routePolyline);
      }
      
      // Create a new polyline with enhanced styling
      this.routePolyline = L.polyline(route, {
        color: color,
        weight: weight,
        opacity: 0.8,
        lineJoin: 'round',
        lineCap: 'round',
        dashArray: null
      }).addTo(this.map);
    
      // Add a white "glow" effect behind the route line for better visibility
      this.routeBackgroundPolyline = L.polyline(route, {
        color: '#ffffff',
        weight: weight + 4,
        opacity: 0.5,
        lineJoin: 'round',
        lineCap: 'round'
      }).addTo(this.map);
      
      // Ensure background line is added below the main route
      this.routeBackgroundPolyline.bringToBack();
      
      // Fit map to see the entire route with padding
      this.map.fitBounds(this.routePolyline.getBounds(), {
        padding: [50, 50],
        maxZoom: 16
      });
    },
    addTransitStops(steps) {
      // Clear any existing transit markers
      if (this.transitMarkers) {
        this.transitMarkers.forEach(marker => this.map.removeLayer(marker));
      }
      this.transitMarkers = [];
      
      steps.forEach(step => {
        if (step.travel_mode === 'TRANSIT' && step.transit_details) {
          const transit = step.transit_details;
          const isBus = transit.line?.vehicle?.name === 'Bus';
          const isMRT = transit.line?.vehicle?.name === 'Subway' || transit.line?.vehicle?.name === 'MRT';
          const routeName = transit.line?.short_name || transit.line?.name || '';
          
          // Add departure stop marker
          if (transit.departure_stop && transit.departure_stop.location) {
            const lat = transit.departure_stop.location.lat;
            const lng = transit.departure_stop.location.lng;
            const stopName = transit.departure_stop.name;
            
            const iconColor = isBus ? '#3182ce' : (isMRT ? '#38a169' : '#718096');
            const customIcon = L.divIcon({
              html: `
                <div class="custom-marker" style="background-color: ${iconColor}; box-shadow: 0 0 0 4px rgba(255,255,255,0.9);">
                  <span>${isBus ? routeName : 'M'}</span>
                </div>
              `,
              className: 'custom-transit-marker',
              iconSize: [24, 24],
              iconAnchor: [12, 12]
            });
            
            const marker = L.marker([lat, lng], { icon: customIcon })
              .bindPopup(`
                <div class="transit-popup">
                  <div class="transit-type">${isBus ? 'Bus Stop' : (isMRT ? 'MRT Station' : 'Transit Stop')}</div>
                  <div class="transit-name">${stopName}</div>
                  <div class="transit-route">${isBus ? `Bus ${routeName}` : (isMRT ? `MRT ${routeName}` : '')}</div>
                  <div class="transit-action">${isBus ? 'Board here' : 'Enter here'}</div>
                </div>
              `, { 
                closeButton: false,
                className: 'transit-custom-popup'
              });
            
            this.transitMarkers.push(marker);
            marker.addTo(this.map);
          }
          
          // Add arrival stop marker
          if (transit.arrival_stop && transit.arrival_stop.location) {
            const lat = transit.arrival_stop.location.lat;
            const lng = transit.arrival_stop.location.lng;
            const stopName = transit.arrival_stop.name;
            
            const iconColor = isBus ? '#3182ce' : (isMRT ? '#38a169' : '#718096');
            const customIcon = L.divIcon({
              html: `
                <div class="custom-marker" style="background-color: ${iconColor}; box-shadow: 0 0 0 4px rgba(255,255,255,0.9);">
                  <span>${isBus ? routeName : 'M'}</span>
                </div>
              `,
              className: 'custom-transit-marker',
              iconSize: [24, 24],
              iconAnchor: [12, 12]
            });
            
            const marker = L.marker([lat, lng], { icon: customIcon })
              .bindPopup(`
                <div class="transit-popup">
                  <div class="transit-type">${isBus ? 'Bus Stop' : (isMRT ? 'MRT Station' : 'Transit Stop')}</div>
                  <div class="transit-name">${stopName}</div>
                  <div class="transit-route">${isBus ? `Bus ${routeName}` : (isMRT ? `MRT ${routeName}` : '')}</div>
                  <div class="transit-action">${isBus ? 'Alight here' : 'Exit here'}</div>
                </div>
              `, { 
                closeButton: false,
                className: 'transit-custom-popup'
              });
            
            this.transitMarkers.push(marker);
            marker.addTo(this.map);
          }
        }
      });
    },
    renderCompleteRoute(steps) {
      // Clear previous routes
      this.clearRoutes();
      
      // Create a marker group to hold all the route segments
      this.routeSegments = [];
      
      steps.forEach((step, index) => {
        if (!step.polyline || !step.polyline.points) return;
        
        // Decode the polyline
        const points = this.decodePolyline(step.polyline.points);
        
        // Determine the styling based on travel mode
        let color, weight, dashArray = null;
        
        switch (step.travel_mode) {
          case 'TRANSIT':
            // Check if it's a bus or MRT
            if (step.transit_details && step.transit_details.line && step.transit_details.line.vehicle) {
              const vehicleType = step.transit_details.line.vehicle.name;
              if (vehicleType === 'Bus') {
                color = '#3182ce'; // Blue for buses
              } else if (vehicleType === 'Subway' || vehicleType === 'MRT') {
                color = '#38a169'; // Green for MRT
              } else {
                color = '#805AD5'; // Purple for other transit
              }
            } else {
              color = '#805AD5'; // Default purple for any transit
            }
            weight = 6;
            break;
          case 'WALKING':
            color = '#718096'; // Gray for walking
            weight = 4;
            dashArray = '6, 8'; // Dashed line for walking
            break;
          default:
            color = '#F56565'; // Red for other modes
            weight = 5;
        }
        
        // Create and add the polyline
        const routeSegment = L.polyline(points, {
          color: color,
          weight: weight,
          opacity: 0.8,
          dashArray: dashArray
        }).addTo(this.map);
        
        // Add white background for better visibility
        if (step.travel_mode === 'TRANSIT') {
          const background = L.polyline(points, {
            color: '#ffffff',
            weight: weight + 4,
            opacity: 0.5
          }).addTo(this.map);
          
          background.bringToBack();
          this.routeSegments.push(background);
        }
        
        this.routeSegments.push(routeSegment);
      });
      
      // Add transit stops
      this.addTransitStops(steps);
      
      // Fit the map to the bounds of all segments
      if (this.routeSegments.length > 0) {
        const bounds = L.featureGroup(this.routeSegments).getBounds();
        this.map.fitBounds(bounds, {
          padding: [50, 50],
          maxZoom: 16
        });
      }
    },
    addOriginDestinationMarkers(origin, destination) {
      // Clear existing markers
      if (this.startMarker) this.map.removeLayer(this.startMarker);
      if (this.endMarker) this.map.removeLayer(this.endMarker);
      
      // Custom start marker
      const startIcon = L.divIcon({
        html: `
          <div class="custom-marker origin-marker">
            <i class="bi bi-geo-alt-fill"></i>
          </div>
        `,
        className: '',
        iconSize: [36, 36],
        iconAnchor: [18, 36]
      });
      
      // Custom end marker
      const endIcon = L.divIcon({
        html: `
          <div class="custom-marker destination-marker">
            <i class="bi bi-flag-fill"></i>
          </div>
        `,
        className: '',
        iconSize: [36, 36],
        iconAnchor: [18, 36]
      });
      
      // Add markers to the map
      this.startMarker = L.marker([origin.lat, origin.lng], {icon: startIcon})
        .addTo(this.map)
        .bindPopup(`<strong>Start:</strong> ${origin.name || 'Origin'}`, {
          closeButton: false
        });
      
      this.endMarker = L.marker([destination.lat, destination.lng], {icon: endIcon})
        .addTo(this.map)
        .bindPopup(`<strong>End:</strong> ${destination.name || 'Destination'}`, {
          closeButton: false
        });
    }
  }
};
</script>

<style scoped>
.simplified-route-view {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.route-header {
  padding: 18px; /* Increased from 16px */
  background: #fff;
  border-bottom: 1px solid #e1e4e8;
}

.route-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.route-time-distance h4 {
  font-size: 22px; /* Increased from 20px */
  font-weight: 500;
  margin: 0;
  color: #202124;
}

.route-time-distance p {
  margin: 4px 0 0;
  color: #5f6368;
  font-size: 15px; /* Increased from 14px */
}

.route-cost {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.cost-badge {
  background: #f1f3f4;
  color: #202124;
  padding: 4px 12px; /* Slightly wider padding */
  border-radius: 4px;
  font-size: 15px; /* Increased from 14px */
  font-weight: 500;
}

.emission-badge {
  margin-top: 6px;
  color: #188038;
  font-size: 14px; /* Increased from 13px */
  display: flex;
  align-items: center;
  gap: 4px;
}

.emission-badge i {
  font-size: 13px; /* Increased from 12px */
}

.departure-time {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
}

.time {
  font-size: 15px; /* Increased from 14px */
  font-weight: 500;
  color: #202124;
}

.arrival {
  font-size: 14px; /* Increased from 13px */
  color: #5f6368;
  margin-top: 2px;
}

.journey-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 18px 18px; /* Increased from 16px */
}

.journey-timeline {
  position: relative;
  padding-top: 16px;
}

.start-point, .end-point {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
  min-height: 36px;
}

.end-point {
  margin-top: 16px;
  margin-bottom: 0;
}

.timeline-dot {
  width: 14px; /* Increased from 12px */
  height: 14px; /* Increased from 12px */
  border-radius: 50%;
  margin-right: 16px;
  position: relative;
  z-index: 2;
  border: 2px solid white;
}

.start-dot {
  background-color: #1a73e8;
}

.end-dot {
  background-color: #ea4335;
}

.timeline-content {
  flex: 1;
}

.location-name {
  font-size: 16px; /* Increased from 14px */
  font-weight: 500;
  color: #202124;
}

.time-label {
  font-size: 13px; /* Increased from 12px */
  color: #5f6368;
  margin-top: 2px;
}

.transit-steps {
  position: relative;
}

.transit-steps::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 7px; /* Adjusted from 6px to center with larger dots */
  width: 2px;
  background: #e1e4e8;
  z-index: 1;
}

.transit-step {
  position: relative;
  padding: 8px 0;
  display: flex;
}

.step-line {
  position: absolute;
  top: 0;
  left: 7px; /* Adjusted from 6px to match the timeline */
  bottom: 0;
  width: 2px;
  z-index: 1;
}

.bus-line {
  background-color: #4285f4;
}

.mrt-line {
  background-color: #34a853;
}

.walk-line {
  background-color: #9aa0a6;
  background-image: linear-gradient(to bottom, #9aa0a6 50%, transparent 50%);
  background-size: 2px 12px;
}

.step-icon-container {
  position: relative;
  z-index: 2;
  margin-right: 16px;
}

.step-icon {
  width: 26px; /* Increased from 24px */
  height: 26px; /* Increased from 24px */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background: #9aa0a6;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  font-size: 13px; /* Increased from 12px */
}

.bus-icon {
  background-color: #4285f4;
}

.mrt-icon {
  background-color: #34a853;
}

.walk-icon {
  background-color: #9aa0a6;
}

.step-details {
  flex: 1;
  padding: 0 0 12px;
}

.step-main {
  font-size: 16px; /* Increased from 14px */
  font-weight: 500;
  color: #202124;
  margin-bottom: 8px; /* Increased from 6px for better spacing */
  display: flex;
  align-items: center;
}

.transit-badge {
  font-size: 11px; /* Increased from 10px */
  padding: 2px 5px; /* Slightly more horizontal padding */
  border-radius: 2px;
  margin-right: 6px;
  font-weight: 700;
}

.mrt {
  background-color: #ceead6;
  color: #0d652d;
}

.bus {
  background-color: #d2e3fc;
  color: #1967d2;
}

.step-stations {
  margin: 8px 0;
  padding-left: 8px;
  border-left: 2px solid #f1f3f4;
}

.station {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.station:last-child {
  margin-bottom: 0;
}

.station-marker {
  width: 8px; /* Increased from 6px */
  height: 8px; /* Increased from 6px */
  border-radius: 50%;
  background: #9aa0a6;
  margin-right: 12px;
  margin-left: -5px; /* Adjusted to accommodate larger marker */
}

.station-name {
  font-size: 14px; /* Increased from 13px */
  color: #5f6368;
}

.step-info {
  font-size: 13px; /* Increased from 12px */
  color: #5f6368;
  margin-top: 6px;
}

@media (max-width: 768px) {
  .route-summary {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .route-cost {
    margin-top: 12px;
    align-items: flex-start;
  }
  
  .simplified-route-view {
    border-radius: 0;
  }
}
</style>