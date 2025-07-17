<script setup lang="ts"></script>

<template>
  <div class="landing-page-wrapper">
    <!-- Hero Section -->
    <b-container class="hero-section text-center">
      <b-row align-v="center">
        <b-col md="6" class="text-md-start">
          <h1 class="hero-title">Seamless Parking, <span class="highlight">Simplified.</span></h1>
          <p class="hero-subtitle">
            Find, book, and pay for your parking spot in seconds. Your hassle-free parking solution
            is just a click away.
          </p>
          <b-button size="lg" to="/login" class="btn-custom mt-3">Get Started</b-button>
        </b-col>
        <b-col md="6" class="mt-5 mt-md-0">
          <!-- Custom SVG Illustration -->
          <div class="hero-illustration">
            <svg viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M 50 250 C 50 150, 150 150, 150 250"
                stroke="rgba(32, 201, 151, 0.5)"
                fill="transparent"
                stroke-width="8"
                stroke-linecap="round"
              />
              <path
                d="M 150 250 L 350 250"
                stroke="rgba(255,255,255,0.2)"
                fill="transparent"
                stroke-width="12"
                stroke-linecap="round"
              />
              <path
                d="M 350 250 C 350 150, 450 150, 450 250"
                stroke="rgba(32, 201, 151, 0.5)"
                fill="transparent"
                stroke-width="8"
                stroke-linecap="round"
              />
              <rect x="120" y="180" width="260" height="70" rx="15" fill="rgba(40, 167, 69, 0.2)" />
              <path
                d="M 100 180 Q 250 100, 400 180"
                stroke="rgba(255,255,255,0.6)"
                fill="transparent"
                stroke-width="10"
                stroke-linecap="round"
              />
              <circle
                cx="180"
                cy="270"
                r="25"
                fill="rgba(255,255,255,0.1)"
                stroke="#20c997"
                stroke-width="3"
              />
              <circle
                cx="320"
                cy="270"
                r="25"
                fill="rgba(255,255,255,0.1)"
                stroke="#20c997"
                stroke-width="3"
              />
            </svg>

            <!-- <img src="@/assets/car2.png" alt="Car Illustration" class="img-fluid car-img" /> -->
          </div>
        </b-col>
      </b-row>
    </b-container>

    <!-- Features Section -->
    <b-container class="features-section text-center">
      <h2 class="section-title">Why Choose Our App?</h2>
      <p class="section-subtitle">Everything you need for a smarter parking experience.</p>
      <b-row class="mt-5">
        <b-col md="4" class="mb-4">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="bi bi-broadcast"></i>
            </div>
            <h3>Real-time Availability</h3>
            <p>
              Check live parking spot availability across all our locations, so you never have to
              circle the block again.
            </p>
          </div>
        </b-col>
        <b-col md="4" class="mb-4">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="bi bi-calendar-check"></i>
            </div>
            <h3>Easy Booking</h3>
            <p>
              Reserve your spot in just a few taps. Your space is guaranteed before you even leave
              home.
            </p>
          </div>
        </b-col>
        <b-col md="4" class="mb-4">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="bi bi-shield-check"></i>
            </div>
            <h3>Secure & Simple</h3>
            <p>
              A unified and secure platform for both admins and users with role-based access
              control.
            </p>
          </div>
        </b-col>
      </b-row>
    </b-container>

    <!-- CTA Section -->
    <b-container class="cta-section text-center">
      <h2 class="section-title">Ready to Park Smarter?</h2>
      <p class="section-subtitle">Create an account today and take control of your parking.</p>
      <b-button size="lg" to="/signup" class="btn-custom mt-3">
        Sign Up for Free
        <i class="bi bi-arrow-right-short"></i>
      </b-button>
    </b-container>

    <!-- Footer -->
    <footer class="text-center py-4">
      <b-container>
        <p class="mb-0">&copy; 2025 Vehicle Parking System. All Rights Reserved.</p>
      </b-container>
    </footer>
  </div>
</template>

<style scoped>
@import url('bootstrap-icons/font/bootstrap-icons.css');

.car-img {
}

.landing-page-wrapper {
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(
    135deg,
    var(--background-start),
    var(--background-middle),
    var(--background-end)
  );
  color: var(--text-color);
  overflow-x: hidden;
}

/* Section Styling */
.hero-section,
.features-section,
.cta-section {
  padding: 100px 0;
  animation: fadeIn 1s ease-in-out;
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

.section-title {
  font-weight: 600;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #fff;
}

.section-subtitle {
  color: var(--text-muted);
  max-width: 600px;
  margin: 0 auto 2rem auto;
}

/* Hero Section */
.hero-title {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 700;
  line-height: 1.2;
  color: #fff;
}

.hero-title .highlight {
  color: var(--highlight-color);
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--text-muted);
  margin-top: 1.5rem;
  max-width: 500px;
}

.hero-illustration svg {
  width: 100%;
  max-width: 450px;
  height: auto;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* Features Section */
.feature-card {
  background: var(--card-bg);
  padding: 40px 30px;
  border-radius: 15px;
  height: 100%;
  border: 1px solid rgba(40, 167, 69, 0.2);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.feature-icon {
  font-size: 3rem;
  color: var(--highlight-color);
  margin-bottom: 1.5rem;
}

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #fff;
}

.feature-card p {
  color: var(--text-muted);
}

/* Buttons */
.btn-custom {
  padding: 12px 30px;
  border-radius: 50px;
  background: linear-gradient(135deg, var(--button-bg-start), var(--button-bg-end));
  border: none;
  font-weight: 600;
  color: white;
  text-decoration: none;
  transition: all 0.4s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-custom:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
  filter: brightness(1.15);
}

/* Footer */
footer {
  background-color: rgba(0, 0, 0, 0.2);
  color: var(--text-muted);
  font-size: 0.9rem;
}
</style>
