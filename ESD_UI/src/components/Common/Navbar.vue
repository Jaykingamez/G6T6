<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <img src="@/assets/logo.png" alt="Singapore Journey Planner" width="220" class="logo-image">
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
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0.75rem 1rem;
}

.navbar-brand {
  transition: transform 0.3s ease;
  padding: 0;
  margin-right: 2rem;
}

.navbar-brand:hover {
  transform: translateY(-1px);
}

.logo-image {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.05));
  transition: transform 0.3s ease;
  height: auto;
  max-height: 55px;
  width: auto;
}

.navbar-brand:hover .logo-image {
  transform: scale(1.02);
}

.brand-text {
  font-weight: 600;
  font-size: 1.25rem;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.nav-link {
  font-weight: 600;
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
  color: #2d3748 !important;
}

.nav-link:hover {
  color: #4299e1 !important;
}

.navbar-toggler {
  border-color: #2d3748;
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(45, 55, 72, 1)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

.dropdown-menu {
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.dropdown-item {
  padding: 0.5rem 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
  color: #2d3748;
}

.dropdown-item:hover {
  background-color: #f7fafc;
  color: #4299e1;
}

.navbar-nav .dropdown-toggle {
  color: #2d3748 !important;
}

.navbar-nav .dropdown-toggle:hover {
  color: #4299e1 !important;
}
</style>