<template>
  <div class="register-page">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <register-form />
      </div>
    </div>
  </div>
</template>

<script>
import RegisterForm from '@/components/AuthComponents/RegisterForm.vue'

export default {
  name: 'Register',
  components: {
    RegisterForm
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>