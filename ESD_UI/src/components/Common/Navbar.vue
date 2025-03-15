<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <img src="@/assets/logo.png" alt="Logo" width="30" height="30" class="d-inline-block align-top me-2">
        Singapore Journey Planner
      </router-link>
      
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/journey-planner">Journey Planner</router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link" to="/saved-journeys">Saved Journeys</router-link>
          </li>
        </ul>
        
        <ul class="navbar-nav">
          <template v-if="!isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Register</router-link>
            </li>
          </template>
          <template v-else>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                <i class="bi bi-person-circle me-1"></i>
                {{ user ? user.email : 'Account' }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click.prevent="handleLogout">Logout</a></li>
              </ul>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Navbar',
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'user']),
  },
  methods: {
    async handleLogout() {
      try {
        await this.$store.dispatch('auth/logout');
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout failed:', error);
      }
    }
  }
};
</script>

<style scoped>
.navbar {
  margin-bottom: 20px;
}
</style>