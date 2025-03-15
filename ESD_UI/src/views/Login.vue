<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow">
          <div class="card-header bg-primary text-white text-center">
            <h2 class="mb-0">Sign In</h2>
          </div>
          <div class="card-body p-4">
            <div class="text-center mb-4">
              <img src="@/assets/logo.png" alt="Logo" width="80" height="80" class="mb-3" />
              <p class="text-muted">Sign in to access your saved journeys and personalized features</p>
            </div>
            
            <form @submit.prevent="handleLogin">
              <div class="form-group mb-3">
                <label for="email" class="form-label">Email Address</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-envelope"></i>
                  </span>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="email" 
                    placeholder="Enter your email"
                    required
                  />
                </div>
              </div>
              
              <div class="form-group mb-3">
                <div class="d-flex justify-content-between">
                  <label for="password" class="form-label">Password</label>
                  <a href="#" class="small text-decoration-none">Forgot password?</a>
                </div>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    class="form-control" 
                    id="password" 
                    v-model="password" 
                    placeholder="Enter your password"
                    required
                  />
                  <button 
                    type="button" 
                    class="input-group-text" 
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>
              
              <div class="form-check mb-3">
                <input type="checkbox" class="form-check-input" id="remember-me" v-model="rememberMe" />
                <label class="form-check-label" for="remember-me">Remember me</label>
              </div>
              
              <button 
                type="submit" 
                class="btn btn-primary w-100 mb-3" 
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Sign In
              </button>
            </form>
            
            <div class="text-center mt-3">
              <p>Don't have an account? <router-link to="/register" class="text-decoration-none">Create Account</router-link></p>
            </div>
            
            <div v-if="error" class="alert alert-danger mt-3">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      rememberMe: false,
      showPassword: false,
      loading: false,
      error: null
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;
      
      try {
        await this.$store.dispatch('auth/login', {
          email: this.email,
          password: this.password
        });
        
        if (this.rememberMe) {
          // Store user info in localStorage for persistence
          localStorage.setItem('user', JSON.stringify(this.$store.getters['auth/user']));
        }
        
        this.$router.push('/journey-planner');
      } catch (error) {
        this.error = 'Invalid email or password. Please try again.';
        console.error('Login error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.card {
  border: none;
  border-radius: 10px;
}

.card-header {
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  padding: 1.25rem;
}

.input-group-text {
  background-color: white;
}

.btn-primary {
  padding: 10px;
}
</style>