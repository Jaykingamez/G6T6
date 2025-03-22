import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import JourneyPlanner from '../views/JourneyPlanner.vue';
import SavedJourneys from '../views/SavedJourneys.vue';
import Profile from '../views/Profile.vue';
import PaymentSuccess from '../views/PaymentSuccess.vue';
import TestPayment from '../views/TestPayment.vue';
import store from '../store';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresGuest: true // Only accessible when not logged in
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      requiresGuest: true // Only accessible when not logged in
    }
  },
  {
    path: '/journey-planner',
    name: 'JourneyPlanner',
    component: JourneyPlanner,
    meta: {
      requiresAuth: true // Requires authentication
    }
  },
  {
    path: '/saved-journeys',
    name: 'SavedJourneys',
    component: SavedJourneys,
    meta: {
      requiresAuth: true // Requires authentication
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      requiresAuth: true // Requires authentication
    }
  },
  {
    path: '/payment-success',
    name: 'PaymentSuccess',
    component: PaymentSuccess,
    meta: {
      requiresAuth: true // Requires authentication
    }
  },
  {
    path: '/test-payment',
    name: 'TestPayment',
    component: TestPayment,
    meta: {
      requiresAuth: true // Requires authentication
    }
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  
  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      // User is not authenticated, redirect to login
      next({
        path: '/login',
        query: { redirect: to.fullPath } // Store the intended destination
      });
    } else {
      next(); // User is authenticated, proceed
    }
  }
  
  // Check if route requires guest access (login/register)
  else if (to.matched.some(record => record.meta.requiresGuest)) {
    if (isAuthenticated) {
      // User is already logged in, redirect to journey planner
      next({ path: '/journey-planner' });
    } else {
      next(); // User is not authenticated, proceed
    }
  }
  
  else {
    next(); // No auth requirements, proceed
  }
});

export default router;