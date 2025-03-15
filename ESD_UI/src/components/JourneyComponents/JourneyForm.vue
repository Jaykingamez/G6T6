<template>
  <div class="journey-form">
    <h2>Plan Your Journey</h2>
    <form @submit.prevent="planJourney">
      <div class="form-group">
        <label for="startPoint">Start Point</label>
        <input
          type="text"
          id="startPoint"
          v-model="startPoint"
          @input="fetchSuggestions('start')"
          class="form-control"
          placeholder="Enter start point"
        />
        <ul v-if="startSuggestions.length" class="suggestions-list">
          <li v-for="suggestion in startSuggestions" :key="suggestion" @click="selectStart(suggestion)">
            {{ suggestion }}
          </li>
        </ul>
      </div>
      <div class="form-group">
        <label for="endPoint">End Point</label>
        <input
          type="text"
          id="endPoint"
          v-model="endPoint"
          @input="fetchSuggestions('end')"
          class="form-control"
          placeholder="Enter end point"
        />
        <ul v-if="endSuggestions.length" class="suggestions-list">
          <li v-for="suggestion in endSuggestions" :key="suggestion" @click="selectEnd(suggestion)">
            {{ suggestion }}
          </li>
        </ul>
      </div>
      <button type="submit" class="btn btn-primary">Plan Journey</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      startPoint: '',
      endPoint: '',
      startSuggestions: [],
      endSuggestions: []
    };
  },
  methods: {
    fetchSuggestions(type) {
      // Fetch suggestions based on the input value
      const query = type === 'start' ? this.startPoint : this.endPoint;
      // Simulate fetching suggestions (replace with actual API call)
      this[type === 'start' ? 'startSuggestions' : 'endSuggestions'] = this.getMockSuggestions(query);
    },
    getMockSuggestions(query) {
      // Mock data for suggestions (replace with actual data)
      const mockData = ['Marina Bay Sands', 'Orchard Road', 'Changi Airport', 'Sentosa', 'Bugis'];
      return mockData.filter(item => item.toLowerCase().includes(query.toLowerCase()));
    },
    selectStart(suggestion) {
      this.startPoint = suggestion;
      this.startSuggestions = [];
    },
    selectEnd(suggestion) {
      this.endPoint = suggestion;
      this.endSuggestions = [];
    },
    planJourney() {
      // Add this line to correctly emit the event with data
      this.$emit('plan-journey', { startPoint: this.startPoint, endPoint: this.endPoint });
      console.log(`Planning journey from ${this.startPoint} to ${this.endPoint}`);
    }
  }
};
</script>

<style scoped>
.journey-form {
  max-width: 600px;
  margin: auto;
}
.suggestions-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
  border: 1px solid #ccc;
  background: white;
  position: absolute;
  z-index: 1000;
  width: 100%;
}
.suggestions-list li {
  padding: 8px;
  cursor: pointer;
}
.suggestions-list li:hover {
  background-color: #f0f0f0;
}
</style>