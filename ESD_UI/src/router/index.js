import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import JourneyPlanner from '../views/JourneyPlanner.vue';
import SavedJourneys from '../views/SavedJourneys.vue';
import Profile from '../views/Profile.vue';
import PaymentSuccess from '../views/PaymentSuccess.vue';
import TestPayment from '../views/TestPayment.vue';

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
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
  },
  {
    path: '/journey-planner',
    name: 'JourneyPlanner',
    component: JourneyPlanner,
  },
  {
    path: '/saved-journeys',
    name: 'SavedJourneys',
    component: SavedJourneys,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
  },
  {
    path: '/payment-success',
    name: 'PaymentSuccess',
    component: PaymentSuccess,
  },
  {
    path: '/test-payment',
    name: 'TestPayment',
    component: TestPayment,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;