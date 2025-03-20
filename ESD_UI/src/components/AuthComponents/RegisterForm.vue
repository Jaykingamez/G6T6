<template>
  <div class="register-form">
    <form @submit.prevent="registerUser">
      <div class="mb-3">
        <label for="fullName" class="form-label">Full Name</label>
        <input 
          type="text" 
          class="form-control" 
          id="fullName" 
          v-model="formData.fullName" 
          required
        >
      </div>

      <div class="mb-3">
        <label for="email" class="form-label">Email address</label>
        <input 
          type="email" 
          class="form-control" 
          id="email" 
          v-model="formData.email" 
          required
        >
      </div>

      <div class="mb-3">
        <label for="phone" class="form-label">Phone Number</label>
        <input 
          type="tel" 
          class="form-control" 
          id="phone" 
          v-model="formData.phone" 
          required
        >
      </div>

      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Registering...' : 'Register' }}
      </button>

      <div v-if="error" class="alert alert-danger mt-3">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RegisterForm',
  data() {
    return {
      formData: {
        fullName: '',
        email: '',
        phone: ''
      },
      isLoading: false,
      error: null
    };
  },
  methods: {
    async registerUser() {
      this.isLoading = true;
      this.error = null;
      
      try {
        // Debug log the request payload
        console.log('Sending registration data:', {
          FullName: this.formData.fullName,
          Email: this.formData.email,
          Phone: this.formData.phone
        });

        const response = await axios.post('http://localhost:5201/users', {
          FullName: this.formData.fullName,
          Email: this.formData.email,
          Phone: this.formData.phone
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          withCredentials: false
        });

        console.log('Full response:', response); // Debug full response

        if (response.data && response.data.code >= 200 && response.data.code < 300) {
          this.$router.push({
            path: '/login',
            query: { registered: 'success' }
          });
        } else {
          throw new Error(response.data?.message || 'Registration failed');
        }
      } catch (error) {
        console.error('Full error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          headers: error.response?.headers
        });
        
        this.error = error.response?.data?.message 
          || error.message 
          || 'Registration failed. Please check the console for details.';
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.register-form {
  max-width: 400px;
  margin: auto;
  padding: 20px;
}
</style>