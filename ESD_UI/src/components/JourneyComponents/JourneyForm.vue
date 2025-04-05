<template>
  <div class="journey-form-container">
    <div class="journey-form">
      <form @submit.prevent="planJourney">
        <div class="form-row">
          <div class="location-input">
            <div class="input-icon">
              <i class="bi bi-geo-alt-fill"></i>
            </div>
            <div class="input-group">
              <input
                type="text"
                id="startPoint"
                v-model="startPoint"
                @input="fetchSuggestions('start')"
                @focus="startFocused = true"
                @blur="handleBlur('start')"
                class="form-control"
                placeholder="Enter start point"
                required
              />
              
              <div v-if="startSuggestions.length && startFocused" class="suggestions-dropdown">
                <div 
                  v-for="suggestion in startSuggestions" 
                  :key="suggestion" 
                  class="suggestion-item"
                  @mousedown="selectStart(suggestion)"
                >
                  <i class="bi bi-pin-map-fill"></i>
                  {{ suggestion }}
                </div>
              </div>
            </div>
          </div>

          <div class="location-swap">
            <button type="button" class="swap-btn" @click="swapLocations" title="Swap locations">
              <i class="bi bi-arrow-down-up"></i>
            </button>
          </div>

          <div class="location-input">
            <div class="input-icon">
              <i class="bi bi-geo-fill"></i>
            </div>
            <div class="input-group">
              <input
                type="text"
                id="endPoint"
                v-model="endPoint"
                @input="fetchSuggestions('end')"
                @focus="endFocused = true"
                @blur="handleBlur('end')"
                class="form-control"
                placeholder="Enter destination"
                required
              />
              
              <div v-if="endSuggestions.length && endFocused" class="suggestions-dropdown">
                <div 
                  v-for="suggestion in endSuggestions" 
                  :key="suggestion" 
                  class="suggestion-item"
                  @mousedown="selectEnd(suggestion)"
                >
                  <i class="bi bi-pin-map-fill"></i>
                  {{ suggestion }}
                </div>
              </div>
            </div>
          </div>

          <button type="submit" class="search-btn" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            <i v-else class="bi bi-search"></i>
            <span>Find Routes</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { planJourney } from '@/services/api';

export default {
  data() {
    return {
      startPoint: '',
      endPoint: '',
      startSuggestions: [],
      endSuggestions: [],
      startFocused: false,
      endFocused: false,
      loading: false
    };
  },
  methods: {
    fetchSuggestions(type) {
      const query = type === 'start' ? this.startPoint : this.endPoint;
      if (query.length < 2) {
        this[type === 'start' ? 'startSuggestions' : 'endSuggestions'] = [];
        return;
      }
      this[type === 'start' ? 'startSuggestions' : 'endSuggestions'] = this.getMockSuggestions(query);
    },
    getMockSuggestions(query) {
      const mockData = [
        'Marina Bay Sands',
        'Orchard Road',
        'Changi Airport',
        'Sentosa',
        'Bugis',
        'Clarke Quay',
        'Jurong East',
        'Tampines Mall',
        'VivoCity'
      ];
      return mockData.filter(item => 
        item.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 5);
    },
    selectStart(suggestion) {
      this.startPoint = suggestion;
      this.startSuggestions = [];
    },
    selectEnd(suggestion) {
      this.endPoint = suggestion;
      this.endSuggestions = [];
    },
    handleBlur(type) {
      setTimeout(() => {
        if (type === 'start') {
          this.startFocused = false;
        } else {
          this.endFocused = false;
        }
      }, 200);
    },
    swapLocations() {
      [this.startPoint, this.endPoint] = [this.endPoint, this.startPoint];
    },
    async planJourney() {
      if (!this.startPoint || !this.endPoint) {
        alert("Please enter both start point and destination");
        return;
      }
      
      this.loading = true;
      
      try {
        // Call the planJourney API with the form inputs
        const response = await planJourney(this.startPoint, this.endPoint);
        
        console.log('Journey planning response:', response);
        
        // Store raw response for debugging
        localStorage.setItem('lastApiResponse', JSON.stringify(response));
        
        // Emit the results to parent component
        this.$emit('plan-journey', {
          startPoint: this.startPoint,
          endPoint: this.endPoint,
          journeyResponse: response
        });
      } catch (error) {
        console.error('Error planning journey:', error);
        
        // Try to extract response from error object for debugging
        if (error.response && error.response.data) {
          console.log('API error response:', error.response.data);
          localStorage.setItem('lastApiError', JSON.stringify(error.response.data));
        }
        
        alert(`Failed to plan journey: ${error.message || 'Unknown error'}`);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.journey-form-container {
  width: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.journey-form {
  width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto;
  gap: 1rem;
  align-items: start;
}

.location-input {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.input-icon {
  width: 46px;
  height: 46px;
  background: #ffffff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4299e1;
  font-size: 1.2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.input-group {
  flex: 1;
  position: relative;
}

.form-control {
  width: 100%;
  padding: 0.85rem 1.2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.form-control:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.25), 0 4px 6px rgba(0, 0, 0, 0.05);
}

.suggestions-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.suggestion-item {
  padding: 0.85rem 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-item:hover {
  background: #f7fafc;
}

.suggestion-item i {
  color: #4299e1;
  font-size: 0.9rem;
}

.location-swap {
  display: flex;
  align-items: center;
}

.swap-btn {
  width: 46px;
  height: 46px;
  border: none;
  background: #ffffff;
  border-radius: 12px;
  color: #4299e1;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.swap-btn:hover {
  background: #f0f9ff;
  transform: rotate(180deg);
}

.search-btn {
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0 1.5rem;
  height: 46px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.search-btn:hover {
  background: #2c5282;
  transform: translateY(-2px);
  box-shadow: 0 7px 14px rgba(0, 0, 0, 0.1);
}

.search-btn i {
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .journey-form-container {
    padding: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .location-swap {
    justify-content: center;
    margin: 0.5rem 0;
  }

  .swap-btn {
    transform: rotate(90deg);
  }

  .swap-btn:hover {
    transform: rotate(270deg);
  }

  .search-btn {
    width: 100%;
    justify-content: center;
    margin-top: 0.5rem;
  }
}
</style>