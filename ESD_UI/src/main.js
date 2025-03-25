// This is the entry point of the Vue application
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap-icons/font/bootstrap-icons.css';

// Toast notifications for Vue 3
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const toastOptions = {
  position: 'top-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
};

// Initialize auth state before mounting the app
store.dispatch('auth/initAuth').then(() => {
  const app = createApp(App);

  app.use(router);
  app.use(store);
  app.use(Toast, toastOptions);

  app.mount('#app');
});