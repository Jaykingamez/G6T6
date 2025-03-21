<template>
  <div class="home">
    <div class="hero-section">
      <div class="hero-content">
        <div class="container-fluid p-0">
          <div class="row align-items-center hero-row">
            <div class="col-lg-6 hero-text fade-in" style="padding-left: 100px;">
              <h1 class="hero-title">Singapore Journey Planner</h1>
              <p class="hero-subtitle">Your one-stop solution for planning your journeys across Singapore.</p>
              <p class="hero-description">Find the best routes, estimated travel times, and costs for your journey in Singapore.</p>
              <router-link to="/journey-planner" class="cta-button">
                Start Planning Your Journey
                <i class="bi bi-arrow-right"></i>
              </router-link>
            </div>
            <div class="col-lg-6 hero-image slide-in-right">
              <div class="image-wrapper">
                <img src="@/assets/hero-image.jpg" alt="Journey Planning Illustration" class="img-fluid">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="features-section">
      <div class="container-fluid">
        <div class="section-header text-center mb-5">
          <h2 class="section-title">Everything you need for your journey</h2>
          <div class="title-underline"></div>
        </div>
        <div class="row g-4 features-grid">
          <div class="col-md-4 px-4">
            <div class="feature-card">
              <div class="icon-wrapper">
                <i class="bi bi-map"></i>
              </div>
              <h3 class="feature-title">Plan Your Journey</h3>
              <p class="feature-text">Get multiple route options with different transport modes, optimized for your preferences.</p>
              <router-link to="/journey-planner" class="feature-link">
                Plan Now
                <i class="bi bi-arrow-right-short"></i>
              </router-link>
            </div>
          </div>
          
          <div class="col-md-4 px-4">
            <div class="feature-card">
              <div class="icon-wrapper">
                <i class="bi bi-bookmark-star"></i>
              </div>
              <h3 class="feature-title">Save Your Journeys</h3>
              <p class="feature-text">Keep track of your frequently traveled routes and access them with just one click.</p>
              <router-link to="/saved-journeys" class="feature-link">
                View Saved
                <i class="bi bi-arrow-right-short"></i>
              </router-link>
            </div>
          </div>
          
          <div class="col-md-4 px-4">
            <div class="feature-card">
              <div class="icon-wrapper">
                <i class="bi bi-person-gear"></i>
              </div>
              <h3 class="feature-title">Manage Your Profile</h3>
              <p class="feature-text">Customize your experience by updating your preferences and personal information.</p>
              <router-link to="/profile" class="feature-link">
                Go to Profile
                <i class="bi bi-arrow-right-short"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>
      <div class="features-background"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
};
</script>

<style scoped>
.home {
  text-align: center;
  width: 100%;
  padding: 0;
  margin: 0;
}

.hero-section {
  position: relative;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  overflow: hidden;
}

.hero-content {
  padding: 4rem 0;
  position: relative;
  width: 100%;
}

.hero-row {
  margin: 0;
  padding: 0;
  align-items: flex-start;
  position: relative;
  width: 100%;
}

.hero-text {
  text-align: left;
  padding: 5rem 2rem 3rem 0;
  position: relative;
  z-index: 2;
}

.hero-image {
  position: relative;
  z-index: 1;
  overflow: visible;
  padding: 0;
  margin: -2rem 0 0 0;
  display: flex;
  justify-content: flex-end;
}

.image-wrapper {
  position: relative;
  height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  min-height: 500px;
  padding: 0;
  margin: 0;
  transform-style: preserve-3d;
  perspective: 1000px;
  width: 100%;
}

.image-wrapper img {
  position: relative;
  width: 120%;
  height: auto;
  max-height: none;
  object-fit: contain;
  transform: translateZ(20px);
  filter: drop-shadow(0 20px 30px rgba(0, 0, 0, 0.15));
  animation: slideInWithPerspective 1.2s ease-out;
  margin-right: -1px; /* Ensures no gap at the edge */
}

@keyframes slideInWithPerspective {
  0% {
    opacity: 0;
    transform: translateX(200px) translateZ(20px) rotateY(-5deg);
  }
  100% {
    opacity: 1;
    transform: translateX(0) translateZ(20px) rotateY(0);
  }
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.5rem;
  color: #4a5568;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.hero-description {
  font-size: 1.1rem;
  color: #718096;
  margin-bottom: 2rem;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
  border-radius: 50px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
}

.cta-button i {
  margin-left: 0.5rem;
  transition: transform 0.3s ease;
}

.cta-button:hover i {
  transform: translateX(4px);
}

.features-section {
  padding: 8rem 0;
  position: relative;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
  overflow: hidden;
  background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
}

.features-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle at 20% 150%, #4299e1 0%, transparent 40%),
                    radial-gradient(circle at 80% -50%, #3182ce 0%, transparent 35%);
  opacity: 0.1;
  z-index: 0;
}

.section-header {
  position: relative;
  z-index: 1;
}

.section-title {
  font-size: 2.75rem;
  font-weight: 800;
  color: #2d3748;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #4299e1 0%, #3182ce 100%);
  margin: 1.5rem auto;
  border-radius: 2px;
}

.features-grid {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.9);
  padding: 2.5rem;
  border-radius: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  height: 100%;
  text-align: left;
  border: 1px solid rgba(226, 232, 240, 0.8);
  backdrop-filter: blur(10px);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
  border-color: rgba(66, 153, 225, 0.3);
}

.icon-wrapper {
  width: 70px;
  height: 70px;
  border-radius: 20px;
  background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.feature-card:hover .icon-wrapper {
  transform: scale(1.1) rotate(-5deg);
}

.icon-wrapper i {
  font-size: 2rem;
  color: #4299e1;
  transition: all 0.3s ease;
}

.feature-card:hover .icon-wrapper i {
  transform: scale(1.1);
  color: #3182ce;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 1rem;
}

.feature-text {
  color: #718096;
  margin-bottom: 1.5rem;
  line-height: 1.7;
  font-size: 1.05rem;
}

.feature-link {
  display: inline-flex;
  align-items: center;
  color: #4299e1;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  padding: 0.5rem 0;
  position: relative;
}

.feature-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #4299e1 0%, #3182ce 100%);
  transition: width 0.3s ease;
}

.feature-link:hover {
  color: #3182ce;
}

.feature-link:hover::after {
  width: 100%;
}

.feature-link i {
  margin-left: 0.5rem;
  transition: transform 0.3s ease;
}

.feature-link:hover i {
  transform: translateX(8px);
}

/* Animations */
.fade-in {
  animation: fadeIn 1s ease-out;
}

.slide-in-right {
  animation: slideInRight 1s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive Design */
@media (max-width: 991.98px) {
  .hero-content {
    padding: 3rem 0;
  }

  .hero-text {
    text-align: center;
    padding: 2rem 1rem;
  }

  .hero-image {
    margin-top: 0;
  }

  .image-wrapper {
    min-height: 400px;
    margin-right: 0;
    justify-content: center;
    align-items: center;
  }

  .image-wrapper img {
    width: 100%;
    transform: translateZ(10px);
    animation: slideInMobile 1.2s ease-out;
  }

  @keyframes slideInMobile {
    0% {
      opacity: 0;
      transform: translateX(100px) translateZ(10px);
    }
    100% {
      opacity: 1;
      transform: translateX(0) translateZ(10px);
    }
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.25rem;
  }

  .section-title {
    font-size: 2.25rem;
  }

  .features-section {
    padding: 6rem 0;
  }

  .feature-card {
    padding: 2rem;
  }
}
</style>