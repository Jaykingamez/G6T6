<template>
  <div class="login-container">
    <div class="login-form fade-in">
      <h2 class="text-center mb-4">Welcome Back</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group mb-4">
          <label for="fullName" class="form-label">Full Name</label>
          <div class="input-group input-group-lg hover-effect">
            <span class="input-group-text border-end-0">
              <i class="bi bi-person"></i>
            </span>
            <input
              type="text"
              class="form-control border-start-0"
              id="fullName"
              v-model="formData.fullName"
              placeholder="Enter your full name"
              required
            />
          </div>
        </div>

        <div class="form-group mb-4">
          <label for="password" class="form-label">Password</label>
          <div class="input-group input-group-lg hover-effect">
            <span class="input-group-text border-end-0">
              <i class="bi bi-lock"></i>
            </span>
            <input
              type="password"
              class="form-control border-start-0"
              id="password"
              v-model="formData.password"
              placeholder="Enter your password"
              required
            />
          </div>
        </div>

        <button type="submit" class="btn btn-primary btn-lg w-100 mb-3 pulse" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <p class="text-center mt-4 slide-up">
          Don't have an account? 
          <router-link to="/register" class="text-decoration-none fw-bold">Register</router-link>
        </p>

        <div v-if="error" class="alert alert-danger mt-3 shake">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      formData: {
        fullName: '',
        password: ''
      },
      loading: false,
      error: null
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;

      try {
        await this.$store.dispatch('auth/login', this.formData);
        // Check if there's a redirect URL in the query parameters
        const redirectPath = this.$route.query.redirect || '/';
        this.$router.push(redirectPath);
      } catch (error) {
        this.error = error.message || 'Invalid credentials. Please try again.';
        console.error('Login error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-form {
  width: 100%;
  max-width: 750px;
  padding: 2.5rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  margin: auto;
}

.form-control, .input-group-text {
  border: 1.5px solid #e0e0e0;
  padding: 12px;
  font-size: 1rem;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.hover-effect:hover .form-control,
.hover-effect:hover .input-group-text {
  background: white;
  border-color: #4a90e2;
}

.form-control:focus {
  box-shadow: none;
  border-color: #4a90e2;
  background: white;
}

.btn-primary {
  background: #4a90e2;
  border: none;
  padding: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #357abd;
  transform: translateY(-2px);
}

.btn-primary:disabled {
  background: #a0aec0;
}

/* Animations */
.fade-in {
  animation: fadeIn 0.6s ease-in;
}

.slide-up {
  animation: slideUp 0.5s ease-out;
}

.shake {
  animation: shake 0.5s ease-in-out;
}

.pulse {
  transition: transform 0.3s ease;
}

.pulse:hover:not(:disabled) {
  animation: pulse 1.5s infinite;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

h2 {
  color: #2d3748;
  font-weight: 700;
  margin-bottom: 2rem;
}

.form-label {
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

router-link {
  color: #4a90e2;
  transition: color 0.3s ease;
}

router-link:hover {
  color: #357abd;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>