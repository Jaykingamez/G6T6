<template>
  <div class="saved-journeys">
    <div class="journey-header">
      <div class="header-background"></div>
      <div class="header-wrapper">
        <div class="header-content">
          <div class="header-left">
            <div class="header-title">
              <h1>My Bus Routes</h1>
              <p class="subtitle">Track your favorite bus services</p>
            </div>
            <div class="stats-container">
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="bi bi-bookmark-check-fill"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ Object.keys(groupedRoutes).length }}</span>
                  <span class="stat-label">Saved Routes</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="bi bi-bell-fill"></i>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ enabledNotifications.size }}</span>
                  <span class="stat-label">Active Notifications</span>
                </div>
              </div>
            </div>
          </div>
          <div class="header-right">
            <router-link to="/journey-planner" class="add-route-btn">
              <i class="bi bi-plus-lg"></i>
              <span>Add New Route</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="journey-content">
        <!-- Loading state -->
        <div v-if="loading" class="loading-state">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p>Loading your saved routes...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="alert custom-alert">
          <div class="alert-content">
            <i class="bi bi-exclamation-circle"></i>
            <div class="alert-text">
              <h4>Unable to load routes</h4>
              <p>{{ error }}</p>
            </div>
          </div>
          <button class="btn btn-light" @click="retryFetch">
            <i class="bi bi-arrow-clockwise"></i> Retry
          </button>
        </div>
        
        <!-- Empty state -->
        <div v-else-if="Object.keys(groupedRoutes).length === 0" class="empty-state">
          <div class="empty-content">
            <i class="bi bi-map"></i>
            <h3>No Saved Routes</h3>
            <p>Save your frequently used bus routes for quick access to arrival times and notifications</p>
            <router-link to="/journey-planner" class="btn btn-primary">
              <i class="bi bi-plus-lg"></i> Plan New Route
            </router-link>
          </div>
        </div>
        
        <!-- Journey cards grouped by route name -->
        <div v-else class="route-groups">
          <div v-for="(routes, routeName) in groupedRoutes" :key="routeName" class="route-group">
            <div class="route-group-header">
              <div class="route-info">
                <i class="bi bi-pin-map-fill"></i>
                <div>
                  <h3>{{ routeName }}</h3>
                  <p class="text-muted">{{ routes.length }} bus services</p>
                </div>
              </div>
            </div>
            
            <div class="route-cards">
              <div v-for="route in routes" :key="route.RouteID" class="route-card">
                <div class="route-card-content">
                  <div class="bus-info">
                    <div class="bus-number">{{ route.BusID }}</div>
                    <div class="bus-details">
                      <div class="bus-stop">
                        <i class="bi bi-geo-alt"></i>
                        <span>Bus Stop: {{ route.BusStopCode }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="route-actions">
                    <button 
                      class="btn notification-btn" 
                      :class="isNotificationEnabled(route.RouteID) ? 'active' : ''"
                      @click="enableNotification(route.RouteID)"
                      :disabled="isNotificationEnabled(route.RouteID)"
                    >
                      <i class="bi" :class="isNotificationEnabled(route.RouteID) ? 'bi-bell-fill' : 'bi-bell'"></i>
                      <span>{{ isNotificationEnabled(route.RouteID) ? 'Notifications On' : 'Get Notifications' }}</span>
                    </button>
                    
                    <button 
                      class="btn remove-btn"
                      @click="removeJourney(route.RouteID)"
                    >
                      <i class="bi bi-trash3"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <i class="bi bi-exclamation-triangle text-danger"></i>
          <h4>Delete Route</h4>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this route? This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-light" @click="cancelDelete">Cancel</button>
          <button class="btn btn-danger" :disabled="deletingJourney" @click="confirmDelete">
            <span v-if="deletingJourney" class="spinner-border spinner-border-sm me-1"></span>
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="showNotificationSuccess" class="notification-toast" :class="{ 'fade-out': isNotificationFading }">
      <div class="notification-content">
        <div class="notification-icon">
          <i class="bi bi-bell-fill"></i>
        </div>
        <div class="notification-text">
          <h4>Notifications Enabled</h4>
          <p style="font-weight: bold;">{{ notificationSuccess }}</p>
        </div>
      </div>
      <div class="notification-progress">
        <div class="progress-bar"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SavedJourneys',
  data() {
    return {
      showDeleteConfirmation: false,
      showNotificationSuccess: false,
      journeyToDelete: null,
      deletingJourney: false,
      loading: false,
      error: null,
      routes: [],
      enabledNotifications: new Set(),
      notificationSuccess: null,
      isNotificationFading: false
    };
  },
  computed: {
    groupedRoutes() {
      // Group routes by RouteName
      const grouped = {};
      for (const route of this.routes) {
        if (!grouped[route.RouteName]) {
          grouped[route.RouteName] = [];
        }
        grouped[route.RouteName].push(route);
      }
      return grouped;
    }
  },
  methods: {
    async fetchRoutes() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await fetch('http://localhost:8000/selectedroute');
        const data = await response.json();
        
        if (data.code === 200) {
          this.routes = data.data.routes;
        } else {
          throw new Error(data.message || 'Failed to fetch routes');
        }
      } catch (error) {
        console.error('Error fetching routes:', error);
        this.error = error.message || 'Failed to fetch saved journeys';
      } finally {
        this.loading = false;
      }
    },
    isNotificationEnabled(routeId) {
      return this.enabledNotifications.has(routeId);
    },
    async enableNotification(routeId) {
      try {
        const response = await fetch(`http://localhost:8000/notify-me/${routeId}`, {
          method: "GET",
        });
        
        if (!response.ok) {
          throw new Error('Failed to enable notifications');
        }

        const result = await response.json();
        this.enabledNotifications.add(routeId);
        
        // Find the route details to get the bus ID
        const route = this.routes.find(r => r.RouteID === routeId);
        if (route) {
          this.notificationSuccess = `You will receive notifications when Bus ${route.BusID} arrives!`;
          this.showNotificationSuccess = true;
          this.isNotificationFading = false;
          
          // Set timer to start fade out after 2.7 seconds (before progress bar completes)
          setTimeout(() => {
            this.isNotificationFading = true;
          }, 2700);
          
          // Hide notification after fade out animation completes
          setTimeout(() => {
            this.showNotificationSuccess = false;
            this.notificationSuccess = null;
            this.isNotificationFading = false;
          }, 3000);
        }
      } catch (err) {
        console.error("Failed to enable notification:", err);
        let errorMessage = "An error occurred while enabling notifications";
        try {
          if (err && typeof err === 'object') {
            errorMessage = err.message || errorMessage;
          }
        } catch (nestedErr) {
          console.error('Error while processing error message:', nestedErr);
        }
        this.error = errorMessage;
      }
    },
    async removeJourney(routeId) {
      this.journeyToDelete = routeId;
      this.showDeleteConfirmation = true;
    },
    async confirmDelete() {
      if (!this.journeyToDelete) {
        this.$toast.error('No route selected for deletion');
        return;
      }

      this.deletingJourney = true;
      
      try {
        const response = await fetch(`http://localhost:8000/selectedroute/${this.journeyToDelete}`, {
          method: 'DELETE'
        });

        const data = await response.json();
        
        // Check if the response indicates success
        if (response.ok && data && data.code === 200) {
          // Remove from local state
          this.routes = this.routes.filter(route => route.RouteID !== this.journeyToDelete);
          this.enabledNotifications.delete(this.journeyToDelete);
          this.$toast.success('Journey deleted successfully');
        } else {
          // If we have an error message in the response, use it
          const errorMessage = data && data.message ? data.message : 'Failed to delete journey';
          throw new Error(errorMessage);
        }
      } catch (err) {
        // Create a completely safe error handling block
        console.error('Delete error:', err);
        
        // Make absolutely sure we have a valid string message
        let errorMessage = 'Failed to delete journey';
        try {
          if (err && typeof err === 'object') {
            errorMessage = err.message || errorMessage;
          }
        } catch (nestedErr) {
          console.error('Error while processing error message:', nestedErr);
        }
        
        // Only call toast if component is still mounted
        if (this.$toast) {
          this.$toast.error(errorMessage);
        }
      } finally {
        if (this.showDeleteConfirmation !== undefined) {
          this.showDeleteConfirmation = false;
          this.journeyToDelete = null;
          this.deletingJourney = false;
        }
      }
    },
    cancelDelete() {
      this.showDeleteConfirmation = false;
      this.journeyToDelete = null;
    },
    retryFetch() {
      this.fetchRoutes();
    }
  },
  mounted() {
    this.fetchRoutes();
  }
};
</script>

<style scoped>
.saved-journeys {
  min-height: 100vh;
  background-color: #f8fafc;
  width: 100%;
  margin: 0;
  padding: 0;
  position: relative;
}

.journey-header {
  position: relative;
  background: #1a365d;
  color: white;
  padding: 3rem 0;
  margin: 0;
  width: 100%;
  overflow: hidden;
}

.header-wrapper {
  width: 100%;
  padding: 0 2rem;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  z-index: 1;
}

.content-wrapper {
  width: 100%;
  padding: 2rem;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.journey-content {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.route-groups {
  display: grid;
  gap: 2rem;
  width: 100%;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
  opacity: 0.8;
}

.header-background::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.header-left {
  flex: 1;
}

.header-title {
  margin-bottom: 2rem;
}

.header-title h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(to right, #ffffff, #e2e8f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: 1.1rem;
  color: #e2e8f0;
  margin: 0.5rem 0 0;
  font-weight: 400;
}

.stats-container {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon i {
  font-size: 1.5rem;
  color: #ffffff;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #e2e8f0;
  margin-top: 0.25rem;
}

.header-right {
  display: flex;
  align-items: flex-start;
}

.add-route-btn {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1rem 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2);
}

.add-route-btn:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(59, 130, 246, 0.3);
}

.add-route-btn i {
  font-size: 1.25rem;
}

@media (max-width: 768px) {
  .header-wrapper,
  .content-wrapper {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .header-right {
    width: 100%;
  }
  
  .add-route-btn {
    width: 100%;
    justify-content: center;
  }
}

.loading-state {
  text-align: center;
  padding: 3rem 0;
}

.loading-state p {
  margin-top: 1rem;
  color: #64748b;
}

.custom-alert {
  background: white;
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.alert-content i {
  font-size: 1.5rem;
  color: #ef4444;
}

.alert-text h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.alert-text p {
  margin: 0.25rem 0 0;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
}

.empty-content {
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.empty-content i {
  font-size: 3rem;
  color: #3b82f6;
  margin-bottom: 1.5rem;
}

.empty-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-content p {
  color: #64748b;
  margin-bottom: 1.5rem;
}

.route-group {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.route-group-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.route-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.route-info i {
  font-size: 1.5rem;
  color: #3b82f6;
}

.route-info h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.route-info p {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
}

.route-cards {
  padding: 1rem;
}

.route-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 1rem;
  transition: all 0.2s ease;
}

.route-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
}

.route-card-content {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bus-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.bus-number {
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.25rem;
}

.bus-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bus-stop, .route-id {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.route-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-btn {
  flex: 1;
}

.notification-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  transition: all 0.2s ease;
}

.notification-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

.notification-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.remove-btn {
  padding: 0.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #ef4444;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header i {
  font-size: 1.5rem;
}

.modal-header h4 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid #e2e8f0;
}

@media (max-width: 768px) {
  .journey-header {
    padding: 1.5rem 0;
  }

  .route-card-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .route-actions {
    width: 100%;
  }

  .notification-btn {
    flex: 1;
  }
}

/* Toast Notification Styles */
.notification-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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

.progress-bar {
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