<template>
  <div class="container mt-4 mb-5">
    <h1 class="text-center mb-4">My Saved Journeys</h1>
    
    <!-- Loading state -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your saved journeys...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="alert alert-danger mx-auto mt-4" style="max-width: 600px;">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <strong>Error:</strong> {{ error }}
      <div class="mt-3">
        <button class="btn btn-sm btn-outline-danger" @click="retryFetch">
          <i class="bi bi-arrow-clockwise me-1"></i> Retry
        </button>
      </div>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="savedJourneys.length === 0" class="text-center mt-5">
      <div class="empty-state">
        <i class="bi bi-bookmark-heart" style="font-size: 3rem;"></i>
        <h3 class="mt-3">No saved journeys yet</h3>
        <p class="text-muted">Plan and save your first journey to see it here.</p>
        <router-link to="/journey-planner" class="btn btn-primary mt-3">
          Plan a Journey
        </router-link>
      </div>
    </div>
    
    <!-- Journey cards -->
    <div v-else>
      <div class="row">
        <div class="col-md-4 mb-4" v-for="journey in savedJourneys" :key="journey.id">
          <div class="card h-100 shadow-sm">
            <div class="card-header d-flex justify-content-between align-items-center">
              <span class="badge" :class="getBadgeClass(journey.transportMode)">
                {{ journey.transportMode }}
              </span>
              <small class="text-muted">Route ID: {{ journey.id }}</small>
            </div>
            <div class="card-body">
              <h5 class="card-title">Bus Stop: {{ journey.startPoint }}</h5>
              <p class="text-muted">Bus ID: {{ journey.endPoint }}</p>
              <ul class="list-unstyled">
                <li v-if="journey.travelTime"><strong>Travel Time:</strong> {{ journey.travelTime }} mins</li>
                <li v-if="journey.cost"><strong>Cost:</strong> ${{ Number(journey.cost).toFixed(2) }}</li>
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
    
    <!-- Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="modal-overlay">
      <div class="modal-content p-4 bg-white rounded shadow">
        <h4>Confirm Deletion</h4>
        <p>Are you sure you want to delete this saved journey?</p>
        <div class="d-flex justify-content-end">
          <button class="btn btn-secondary me-2" @click="cancelDelete">Cancel</button>
          <button class="btn btn-danger" :disabled="deletingJourney" @click="confirmDelete">
            <span v-if="deletingJourney" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'SavedJourneys',
  data() {
    return {
      showDeleteConfirmation: false,
      journeyToDelete: null,
      deletingJourney: false
    };
  },
  computed: {
    ...mapState({
      loading: state => state.journeys.loading,
      error: state => state.journeys.error,
    }),
    ...mapGetters({
      savedJourneys: 'journeys/allSavedJourneys'
    })
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'Unknown date';
      
      try {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        }).format(date);
      } catch (e) {
        console.error('Date formatting error:', e);
        return 'Invalid date';
      }
    },
    getBadgeClass(transportMode) {
      if (!transportMode) return 'bg-secondary text-white';
      
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
    async confirmDelete() {
      this.deletingJourney = true;
      try {
        await this.$store.dispatch('journeys/removeJourney', this.journeyToDelete);
        this.$toast.success('Journey deleted successfully');
      } catch (error) {
        this.$toast.error('Failed to delete journey: ' + (error.message || 'Unknown error'));
      } finally {
        this.showDeleteConfirmation = false;
        this.journeyToDelete = null;
        this.deletingJourney = false;
      }
    },
    cancelDelete() {
      this.showDeleteConfirmation = false;
      this.journeyToDelete = null;
    },
    retryFetch() {
      this.fetchSavedJourneys();
    },
    fetchSavedJourneys() {
      this.$store.dispatch('journeys/fetchSavedJourneys');
    }
  },
  mounted() {
    // Fetch saved journeys when component mounts
    this.fetchSavedJourneys();
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