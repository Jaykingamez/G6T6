<template>
  <div class="home">
    <div class="jumbotron text-center">
      <h1 class="display-4">Singapore Journey Planner</h1>
      <p class="lead">Your one-stop solution for planning your journeys across Singapore.</p>
      <hr class="my-4">
      <p>Find the best routes, estimated travel times, and costs for your journey in Singapore.</p>
      <router-link to="/journey-planner" class="btn btn-primary btn-lg">Start Planning Your Journey</router-link>
    </div>
    
    <div class="container mt-5">
      <div class="row">
        <div class="col-md-4">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">Plan Your Journey</h5>
              <p class="card-text">Get multiple route options with different transport modes.</p>
              <router-link to="/journey-planner" class="btn btn-outline-primary">Plan Now</router-link>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">Save Your Journeys</h5>
              <p class="card-text">Keep track of your frequently traveled routes.</p>
              <router-link to="/saved-journeys" class="btn btn-outline-primary">View Saved</router-link>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">Manage Your Profile</h5>
              <p class="card-text">Update your personal information and preferences.</p>
              <router-link to="/profile" class="btn btn-outline-primary">Go to Profile</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
};
</script>

<style scoped>
.home {
  text-align: center;
}

.jumbotron {
  background-color: #f8f9fa;
  padding: 2rem 1rem;
  margin-bottom: 2rem;
  border-radius: 0.3rem;
}

.card {
  height: 100%;
  transition: transform 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>