<template>
  <div class="login-form">
    <h2 class="text-center">Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">Email</label>
        <input
          type="email"
          class="form-control"
          id="email"
          v-model="email"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          class="form-control"
          id="password"
          v-model="password"
          required
        />
      </div>
      <button type="submit" class="btn btn-primary btn-block">Login</button>
      <p class="text-center mt-3">
        Don't have an account? <router-link to="/register">Register</router-link>
      </p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: ''
    };
  },
  methods: {
    handleLogin() {
      // Logic for handling user login will go here
      // This will typically involve calling a method from the auth store
    }
  }
};
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
}
</style>