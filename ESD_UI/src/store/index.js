// src/store/index.js

import { createStore } from 'vuex';
import auth from './modules/auth';
import journeys from './modules/journeys';

export default createStore({
  modules: {
    auth,
    journeys
  }
});