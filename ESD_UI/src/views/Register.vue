<template>
  <div class="container">
    <h2 class="mt-5">Register</h2>
    <register-form />
  </div>
</template>

<script>
import RegisterForm from '../components/AuthComponents/RegisterForm.vue';

export default {
  name: 'Register',
  components: {
    RegisterForm
  }
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: auto;
}
</style>