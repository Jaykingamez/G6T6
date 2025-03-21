<template>
  <div class="journey-card">
    <div class="card-content">
      <div class="transport-icon">
        <i :class="getTransportIcon"></i>
      </div>
      <div class="journey-details">
        <h3 class="transport-mode">{{ transportMode }}</h3>
        <div class="journey-stats">
          <div class="stat">
            <i class="bi bi-clock"></i>
            <span>{{ travelTime }} min</span>
          </div>
          <div class="stat">
            <i class="bi bi-currency-dollar"></i>
            <span>${{ cost.toFixed(2) }}</span>
          </div>
        </div>
      </div>
      <div class="journey-actions">
        <button class="btn-save" @click="saveJourney" title="Save Journey">
          <i class="bi bi-bookmark-plus"></i>
          <span>Save</span>
        </button>
        <button class="btn-map" @click="viewOnMap" title="View on Map">
          <i class="bi bi-map"></i>
          <span>Map</span>
        </button>
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
      type: Number,
      required: true
    }
  },
  computed: {
    getTransportIcon() {
      const icons = {
        'MRT': 'bi bi-train-front',
        'Bus': 'bi bi-bus-front',
        'Taxi': 'bi bi-taxi-front',
        'Walk': 'bi bi-person-walking'
      };
      return icons[this.transportMode] || 'bi bi-arrow-right-circle';
    }
  },
  methods: {
    saveJourney() {
      this.$emit('save-journey', {
        transportMode: this.transportMode,
        travelTime: this.travelTime,
        cost: this.cost
      });
    },
    viewOnMap() {
      this.$emit('view-on-map', {
        transportMode: this.transportMode
      });
    }
  }
};
</script>

<style scoped>
.journey-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.8);
  backdrop-filter: blur(10px);
  margin-bottom: 1rem;
}

.journey-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
}

.card-content {
  padding: 1.5rem;
}

.transport-icon {
  background: linear-gradient(135deg, #4299e1 0%, #2c5282 100%);
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  color: white;
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.journey-card:hover .transport-icon {
  transform: scale(1.05);
}

.transport-mode {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.journey-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  font-size: 0.95rem;
}

.stat i {
  color: #4299e1;
}

.journey-actions {
  display: flex;
  gap: 1rem;
}

.btn-save,
.btn-map {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  cursor: pointer;
}

.btn-save {
  background: #4299e1;
  color: white;
}

.btn-map {
  background: #edf2f7;
  color: #2d3748;
}

.btn-save:hover {
  background: #3182ce;
}

.btn-map:hover {
  background: #e2e8f0;
}

.btn-save i,
.btn-map i {
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .card-content {
    padding: 1.25rem;
  }

  .transport-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }

  .transport-mode {
    font-size: 1.1rem;
  }

  .journey-stats {
    gap: 1rem;
  }

  .stat {
    font-size: 0.9rem;
  }
}
</style>