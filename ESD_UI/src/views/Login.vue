<template>
  <div class="login-page">
    <div class="row justify-content-center width-full margin-top-0">
      <div class="col-md-6 col-lg-5">
        <login-form />
      </div>
    </div>
  </div>
</template>

<script>
import LoginForm from '@/components/AuthComponents/LoginForm.vue'

export default {
  name: 'Login',
  components: {
    LoginForm
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding-top: 0;
}
</style>