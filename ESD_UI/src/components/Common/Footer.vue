<template>
  <footer class="footer mt-auto py-3 bg-light">
    <div class="container text-center">
      <span class="text-muted">© {{ currentYear }} NavSmart SG. All rights reserved.</span>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
};
</script>

<style scoped>
.footer {
  margin-top: 50px;
}
</style>