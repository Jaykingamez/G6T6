<template>
  <div class="container">
    <h2 class="mt-5">Register</h2>
    <form @submit.prevent="registerUser">
      <div class="mb-3">
        <label for="username" class="form-label">Username</label>
        <input type="text" class="form-control" id="username" v-model="username" required>
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Email address</label>
        <input type="email" class="form-control" id="email" v-model="email" required>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model="password" required>
      </div>
      <button type="submit" class="btn btn-primary">Register</button>
    </form>
    <p class="mt-3">Already have an account? <router-link to="/login">Login here</router-link>.</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      email: '',
      password: ''
    };
  },
  methods: {
    async registerUser() {
      // Logic for user registration using Firebase
      try {
        // Call Firebase registration method here
        // await firebase.auth().createUserWithEmailAndPassword(this.email, this.password);
        // Optionally, save additional user info (like username) to Firestore
      } catch (error) {
        console.error("Registration error:", error);
      }
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: auto;
}
</style>