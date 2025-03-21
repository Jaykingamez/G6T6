<template>
  <div id="app">
    <Navbar />
    <main class="container px-0" style="width: 100%;">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script>
import Navbar from './components/Common/Navbar.vue';
import Footer from './components/Common/Footer.vue';

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  },
  created() {
    // Check if user is authenticated on app load
    this.$store.dispatch('auth/checkAuthState');
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style>