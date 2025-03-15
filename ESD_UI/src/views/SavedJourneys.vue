<template>
  <div class="container mt-4 mb-5">
    <h1 class="text-center mb-4">My Saved Journeys</h1>
    
    <div v-if="savedJourneys.length === 0" class="text-center mt-5">
      <div class="empty-state">
        <i class="bi bi-bookmark-heart" style="font-size: 3rem;"></i>
        <h3 class="mt-3">No saved journeys yet</h3>
        <p class="text-muted">Plan and save your first journey to see it here.</p>
        <router-link to="/journey-planner" class="btn btn-primary mt-3">
          Plan a Journey
        </router-link>
      </div>
    </div>
    
    <div v-else>
      <div class="row">
        <div class="col-md-4 mb-4" v-for="journey in savedJourneys" :key="journey.id">
          <div class="card h-100 shadow-sm">
            <div class="card-header d-flex justify-content-between align-items-center">
              <span class="badge" :class="getBadgeClass(journey.transportMode)">
                {{ journey.transportMode }}
              </span>
              <small class="text-muted">Saved on {{ formatDate(journey.savedAt) }}</small>
            </div>
            <div class="card-body">
              <h5 class="card-title">{{ journey.startPoint }} to {{ journey.endPoint }}</h5>
              <ul class="list-unstyled">
                <li><strong>Travel Time:</strong> {{ journey.travelTime }} mins</li>
                <li><strong>Cost:</strong> ${{ journey.cost.toFixed(2) }}</li>
              </ul>
            </div>
            <div class="card-footer bg-white">
              <div class="d-flex justify-content-between">
                <button class="btn btn-sm btn-outline-primary" @click="planSimilar(journey)">
                  Plan Similar
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="removeJourney(journey.id)">
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirmation Modal Placeholder -->
    <div v-if="showDeleteConfirmation" class="modal-overlay">
      <div class="modal-content p-4 bg-white rounded shadow">
        <h4>Confirm Deletion</h4>
        <p>Are you sure you want to delete this saved journey?</p>
        <div class="d-flex justify-content-end">
          <button class="btn btn-secondary me-2" @click="showDeleteConfirmation = false">Cancel</button>
          <button class="btn btn-danger" @click="confirmDelete">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'SavedJourneys',
  data() {
    return {
      showDeleteConfirmation: false,
      journeyToDelete: null,
      // Mock data - would normally come from store
      savedJourneys: [
        {
          id: '1',
          startPoint: 'Changi Airport',
          endPoint: 'Marina Bay Sands',
          transportMode: 'MRT',
          travelTime: 35,
          cost: 2.50,
          savedAt: '2023-03-01T08:30:00Z'
        },
        {
          id: '2',
          startPoint: 'Orchard Road',
          endPoint: 'Sentosa',
          transportMode: 'Bus',
          travelTime: 45,
          cost: 1.80,
          savedAt: '2023-02-15T14:20:00Z'
        },
        {
          id: '3',
          startPoint: 'Jurong East',
          endPoint: 'Changi Business Park',
          transportMode: 'Taxi',
          travelTime: 30,
          cost: 22.50,
          savedAt: '2023-02-28T18:45:00Z'
        }
      ]
    };
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-SG', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }).format(date);
    },
    getBadgeClass(transportMode) {
      switch(transportMode.toLowerCase()) {
        case 'mrt':
          return 'bg-primary text-white';
        case 'bus':
          return 'bg-success text-white';
        case 'taxi':
          return 'bg-warning text-dark';
        default:
          return 'bg-secondary text-white';
      }
    },
    planSimilar(journey) {
      this.$router.push({
        name: 'JourneyPlanner',
        params: {
          startPoint: journey.startPoint,
          endPoint: journey.endPoint
        }
      });
    },
    removeJourney(journeyId) {
      this.journeyToDelete = journeyId;
      this.showDeleteConfirmation = true;
    },
    confirmDelete() {
      // Would typically dispatch to store
      this.savedJourneys = this.savedJourneys.filter(journey => journey.id !== this.journeyToDelete);
      this.showDeleteConfirmation = false;
      this.journeyToDelete = null;
    }
  },
  mounted() {
    // In a real app, would fetch saved journeys from store/API
    // this.$store.dispatch('journeys/fetchSavedJourneys');
  }
};
</script>

<style scoped>
.empty-state {
  padding: 50px 20px;
  border: 2px dashed #dee2e6;
  border-radius: 10px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  max-width: 400px;
  width: 100%;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>