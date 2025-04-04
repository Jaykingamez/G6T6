<template>
  <div class="container">
    <div class="row">
      <div class="col-lg-10 mx-auto">
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <template v-else>
          <!-- Main Profile Section -->
          <div class="profile-header">
            <div class="transit-banner">                
              <h1>My Transit Account</h1>
            </div>
          </div>

          <div class="row g-4">
            <!-- User Profile Card -->
            <div class="col-md-5">
              <div class="card shadow profile-card">
                <div class="card-header">
                  <h2 class="mb-0"><i class="bi bi-person-badge me-2"></i>Account Profile</h2>
                </div>
                <div class="card-body">
                  <div class="text-center mb-4">
                    <div class="avatar-container">
                      <img :src="avatarUrl" :alt="user.FullName" class="rounded-circle img-fluid" />
                    </div>
                    <h3 class="user-name mt-3">{{ user.FullName }}</h3>
                    <span class="account-id">User ID: #{{ userId }}</span>
                  </div>

                  <div v-if="!editMode">
                    <dl class="row profile-details">
                      <dt class="col-sm-4"><i class="bi bi-envelope me-2"></i>Email:</dt>
                      <dd class="col-sm-8">{{ user.Email }}</dd>

                      <dt class="col-sm-4"><i class="bi bi-telephone me-2"></i>Phone:</dt>
                      <dd class="col-sm-8">
                        {{ user.Phone || "Not provided" }}
                      </dd>

                      <dt class="col-sm-4"><i class="bi bi-calendar-check me-2"></i>Member Since:</dt>
                      <dd class="col-sm-8">{{ formatDate(user.CreatedAt) }}</dd>
                    </dl>

                    <button class="btn btn-primary w-100" @click="toggleEditMode">
                      <i class="bi bi-pencil-square me-2"></i> Edit Profile
                    </button>
                  </div>

                  <div v-else>
                    <form @submit.prevent="saveProfile">
                      <div class="form-group mb-3">
                        <label for="name"><i class="bi bi-person me-2"></i>Name</label>
                        <input type="text" id="name" class="form-control" v-model="editedUser.FullName" required
                          :class="{ 'is-invalid': validationErrors.FullName }" />
                        <div class="invalid-feedback">
                          {{ validationErrors.FullName }}
                        </div>
                      </div>

                      <div class="form-group mb-3">
                        <label for="email"><i class="bi bi-envelope me-2"></i>Email</label>
                        <input type="email" id="email" class="form-control" v-model="editedUser.Email" required
                          :class="{ 'is-invalid': validationErrors.Email }" />
                        <div class="invalid-feedback">
                          {{ validationErrors.Email }}
                        </div>
                      </div>

                      <div class="form-group mb-3">
                        <label for="phone"><i class="bi bi-telephone me-2"></i>Phone</label>
                        <input type="tel" id="phone" class="form-control" v-model="editedUser.Phone"
                          :class="{ 'is-invalid': validationErrors.Phone }" />
                        <div class="invalid-feedback">
                          {{ validationErrors.Phone }}
                        </div>
                      </div>

                      <div class="d-flex">
                        <button type="submit" class="btn btn-success me-2 flex-grow-1" :disabled="updating">
                          <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                          <i v-else class="bi bi-check-circle me-2"></i>
                          {{ updating ? "Saving..." : "Save Changes" }}
                        </button>
                        <button type="button" class="btn btn-secondary flex-grow-1" @click="cancelEdit" :disabled="updating">
                          <i class="bi bi-x-circle me-2"></i> Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>

              <!-- Account Settings Card -->
              <div class="card mt-4 shadow settings-card">
                <div class="card-header">
                  <h3 class="mb-0"><i class="bi bi-gear-fill me-2"></i>Account Settings</h3>
                </div>
                <div class="card-body">
                  <div class="setting-group">
                    <h5><i class="bi bi-shield-lock me-2"></i>Account Security</h5>
                    <p class="text-muted">
                      Managing your account security options
                    </p>
                    <button class="btn btn-outline-primary mb-3">
                      <i class="bi bi-key me-2"></i>Change Password
                    </button>
                  </div>

                  <div class="setting-group border-top pt-4">
                    <h5><i class="bi bi-exclamation-triangle me-2"></i>Danger Zone</h5>
                    <p class="text-danger">
                      This action is irreversible. All your data will be permanently deleted.
                    </p>
                    <button class="btn btn-danger" @click="confirmDeleteAccount" :disabled="deleting">
                      <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bi bi-trash me-2"></i>
                      {{ deleting ? "Deleting..." : "Delete Account" }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Transit Cards Section -->
            <div class="col-md-7">
              <div class="card shadow transit-card-section">
                <div class="card-header">
                  <h3 class="mb-0">
                    <i class="bi bi-credit-card-2-front me-2"></i>My Transit Cards
                  </h3>
                </div>
                <div class="card-body">
                  <div v-if="loading" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Loading cards...</span>
                    </div>
                  </div>

                  <div v-else-if="cards && cards.length" class="transit-cards">
                    <div v-for="card in cards" :key="card.CardId" class="mb-4">
                      <div class="transit-card">
                        <div class="card-header-strip"></div>
                        <div class="card-content">
                          <div class="card-top">
                            <div class="card-chip"></div>
                            <div class="card-logo">
                              <i class="fas fa-bus"></i>
                              Transit Card
                            </div>
                          </div>
                          <div class="card-details">
                            <div class="card-number">{{ card.CardSerialNumber }}</div>
                            <div class="card-holder-name">{{ user.FullName }}</div>
                            <div class="card-info">
                              <div class="card-type">Transit Pass</div>
                              <div class="card-valid">ACTIVE</div>
                            </div>
                          </div>
                          <div class="card-balance">
                            Balance: ${{ card.Balance.toFixed(2) }}
                          </div>
                        </div>
                      </div>

                      <!-- Card balance and actions -->
                      <div class="card-actions mt-3">
                        <div class="balance-section">
                          <div class="balance-info">
                            <div class="balance-label">Available Balance</div>
                            <div class="balance-amount">${{ card.Balance.toFixed(2) }}</div>
                          </div>
                          <button class="btn btn-primary" @click="topUpCard(card)" :disabled="isProcessing">
                            <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
                            <i v-else class="bi bi-plus-circle me-2"></i>
                            Top Up
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-else class="text-center py-4 no-cards">
                    <div class="empty-card-placeholder">
                      <i class="bi bi-credit-card-2-front"></i>
                    </div>
                    <h4 class="mt-4">No Transit Cards Found</h4>
                    <p class="text-muted">
                      You don't have any transit cards yet. Apply for a card to start using our transit system.
                    </p>
                    <button class="btn btn-primary mt-3" @click="applyForCard" :disabled="applyingForCard">
                      <span v-if="applyingForCard" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bi bi-plus-circle me-2"></i>
                      {{ applyingForCard ? "Processing..." : "Apply for Transit Card" }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Recent Activities Card -->
              <div class="card mt-4 shadow activity-card">
                <div class="card-header">
                  <h3 class="mb-0"><i class="bi bi-activity me-2"></i>Recent Activities</h3>
                </div>
                <div class="card-body">
                  <!-- If no activities yet -->
                  <div class="text-center py-3">
                    <i class="bi bi-clock-history display-4 text-muted"></i>
                    <p class="mt-3">No recent activities to display.</p>
                    <p class="text-muted small">Your transit activities will appear here once you start using your card.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { mapState } from "vuex";
import { useToast } from 'vue-toastification';
import { ref, reactive } from 'vue';

export default {
  setup() {
    const toast = useToast();
    const cardStates = reactive({});
    return { toast, cardStates }
  },
  data() {
    return {
      loading: false,
      error: null,
      editMode: false,
      editedUser: {},
      updating: false,
      deleting: false,
      validationErrors: {},
      showChangePasswordModal: false,
      changingPassword: false,
      passwordForm: {
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      },
      cards: [],
      applyingForCard: false,
      isProcessing: false,
      selectedCard: null,
    };
  },
  computed: {
    ...mapState("auth", ["user"]),
    userId() {
      return this.user?.UserId;
    },
    avatarUrl() {
      return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(
        this.user?.FullName || "User"
      )}`;
    },
  },
  watch: {
    // Watch for changes in the user object from Vuex store
    user: {
      immediate: true,
      handler(newUser) {
        if (!newUser) {
          this.error = "Please log in to view your profile.";
        } else {
          this.error = null;
          // Initialize editedUser when user data is available
          this.editedUser = { ...newUser };
        }
      },
    },
  },
  created() {
    if (!this.user) {
      this.error = "Please log in to view your profile.";
      return;
    }
    // Verify user data in the database
    this.$store.dispatch("auth/checkAuthState");
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return "N/A";
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    },
    toggleEditMode() {
      this.editMode = !this.editMode;
      if (this.editMode) {
        this.editedUser = { ...this.user };
      }
      this.validationErrors = {};
    },
    async saveProfile() {
      this.updating = true;
      this.validationErrors = {};

      try {
        const response = await axios.put(
          `${process.env.VUE_APP_USER_API_URL || "http://localhost:5201"
          }/users/${this.userId}`,
          this.editedUser
        );

        if (response.data.code === 200) {
          // Update the Vuex store with the new user data
          this.$store.commit("auth/SET_USER", response.data.data);
          this.editMode = false;
        } else {
          throw new Error(response.data.message || "Failed to update profile");
        }
      } catch (error) {
        console.error("Error updating profile:", error);
        if (error.response?.data?.validationErrors) {
          this.validationErrors = error.response.data.validationErrors;
        } else {
          this.error =
            error.response?.data?.message ||
            "Failed to update profile. Please try again.";
        }
      } finally {
        this.updating = false;
      }
    },
    cancelEdit() {
      this.editMode = false;
      this.editedUser = { ...this.user };
      this.validationErrors = {};
    },
    async confirmDeleteAccount() {
      if (
        !confirm(
          "Are you sure you want to delete your account? This action cannot be undone."
        )
      ) {
        return;
      }

      this.deleting = true;

      try {
        await axios.delete(`http://localhost:5201/users/${this.userId}`);
        await this.$store.dispatch("auth/logout");
        this.$router.push("/");
        this.$toast.success("Your account has been deleted successfully.");
      } catch (error) {
        console.error("Error deleting account:", error);
        this.$toast.error("Failed to delete account. Please try again.");
      } finally {
        this.deleting = false;
      }
    },
    async applyForCard() {
      this.applyingForCard = true;
      try {
        // Generate a random card serial number
        const serialNumber =
          "SN" + Math.random().toString(36).substr(2, 9).toUpperCase();

        const response = await axios.post(
          `${process.env.VUE_APP_CARD_API_URL || "http://localhost:5203"
          }/cards`,
          {
            UserId: this.userId,
            Balance: 0.0,
            CardSerialNumber: serialNumber,
          }
        );

        if (response.data.code === 201) {
          // // Add the new card to the cards array
          // this.cards = [...this.cards, response.data.data];
          await this.fetchUserCards(); // Refresh cards list after successful application
          this.$toast.success("Card application successful!");
        } else {
          throw new Error(response.data.message || "Failed to apply for card");
        }
      } catch (error) {
        console.error("Error applying for card:", error);
        this.$toast.error(
          error?.response?.data?.message || "Failed to apply for card"
        );
      } finally {
        this.applyingForCard = false;
      }
    },

    async fetchUserCards() {
      try {
        console.log('Fetching cards for user:', this.userId); // Debug log

        const response = await axios.get(
          `${process.env.VUE_APP_CARD_API_URL || 'http://localhost:5203'}/cards`, {
          params: {
            user_id: this.userId
          }
        }
        );

        console.log('Card service response:', response.data); // Debug log

        if (response.data.code === 200 && Array.isArray(response.data.data)) {
          this.cards = response.data.data;
          console.log('Cards loaded:', this.cards); // Debug log
        } else {
          this.cards = [];
          console.warn('No cards data in response:', response.data);
        }
      } catch (error) {
        console.error('Error fetching cards:', error);
        this.cards = [];
        this.$toast.error(
          error.response?.data?.message || 'Failed to fetch cards'
        );
      }
    },
    topUpCard(card) {
      // Prevent card flip when clicking top up button
      event.stopPropagation();
      this.selectedCard = card;
      // Navigate to top up page with card details
      this.$router.push({
        name: 'TopUp',
        params: {
          cardId: card.CardId
        },
        query: {
          userId: this.userId,
          cardNumber: card.CardSerialNumber,
          currentBalance: card.Balance,
          phone_number: this.user.Phone || '', // Add phone number from user profile
        }
      });
    },
    toggleCardFlip(cardId) {
      // Direct property assignment works with reactive objects in Vue 3
      this.cardStates[cardId] = !this.cardStates[cardId];
    },
  },
  async created() {
    // Add this to fetch cards when component is created
    if (this.userId) {
      await this.fetchUserCards();
    }

    // Check for payment status in URL parameters
    const status = this.$route.query.status;
    const message = this.$route.query.message;
    const amount = this.$route.query.amount;
    const newBalance = this.$route.query.new_balance;

    if (status) {
      switch (status) {
        case 'success':
          this.$toast.success(
            `Payment successful! Amount: $${amount}${newBalance ? ` (New balance: $${newBalance})` : ''}`
          );
          this.fetchUserCards(); // Refresh cards after successful payment
          break;
        case 'failed':
          this.$toast.error(message || 'Payment failed');
          break;
        case 'error':
          this.$toast.error(message || 'An error occurred');
          break;
      }

      // Clean up URL parameters
      this.$router.replace({ query: {} });
    }
  },
};
</script>

<style scoped>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Variables */
:root {
  --primary-color: #4F46E5;
  --primary-light: #6366F1;
  --primary-dark: #4338CA;
  --secondary-color: #818CF8;
  --accent-color: #C7D2FE;
}

/* Base Styles */
.container {
  padding: 2rem 1rem;
  background: #f8f9fa;
  min-height: calc(100vh - 60px);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header Section */
.profile-header {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  color: white;
  padding: 2.5rem 1rem;
  margin: -2rem -1rem 2rem;
  position: relative;
}

.transit-banner {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.transit-banner h1 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.02em;
}

/* Card Base Styles */
.card {
  border: none;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  background: white;
  margin-bottom: 1.5rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.card-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  font-weight: 600;
}

/* Profile Section */
.profile-card .card-header {
  background: white;
  color: #1a1a1a;
  font-size: 1.25rem;
}

.profile-card .card-header i {
  color: #005BAC;
}

.avatar-container {
  width: 100px;
  height: 100px;
  position: relative;
  margin: 0 auto 1rem;
}

.avatar-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.user-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
}

.account-id {
  font-size: 0.875rem;
  color: #666;
  font-weight: 500;
}

/* Updated Card Styles */
.transit-card {
  position: relative;
  width: 100%;
  height: 300px;  /* Increased height */
  background: linear-gradient(135deg, #005BAC 0%, #0077CC 100%);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s ease;
  margin-bottom: 0.5rem;
}

.transit-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
}

.card-header-strip {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #FFB800 0%, #FF9500 100%);
}

.card-content {
  height: 100%;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.card-chip {
  width: 45px;
  height: 35px;
  background: linear-gradient(135deg, #FFB800 0%, #FF9500 100%);
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.card-chip::after {
  content: '';
  position: absolute;
  top: 50%;
  left: -5px;
  right: -5px;
  height: 1px;
  background: rgba(0, 0, 0, 0.2);
}

.card-logo {
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  letter-spacing: 0.5px;
}

.card-logo i {
  margin-right: 0.75rem;
  font-size: 1.5rem;
}

.card-details {
  margin: 1.5rem 0;
}

.card-number {
  font-family: 'Inter', monospace;
  font-size: 1.25rem;
  font-weight: 500;
  letter-spacing: 2px;
  margin-bottom: 1rem;
  opacity: 0.9;
}

.card-holder-name {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.card-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.card-type {
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.9;
}

.card-valid {
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 1px;
}

.card-balance {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.card-actions {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.balance-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-info {
  display: flex;
  flex-direction: column;
}

.balance-label {
  font-size: 0.875rem;
  color: #666;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.balance-amount {
  font-size: 2rem;
  font-weight: 600;
  color: #005BAC;
  line-height: 1;
}

.btn-primary {
  background: #005BAC;
  border: none;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #0077CC;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 91, 172, 0.2);
}

.btn-primary:active {
  transform: translateY(0);
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .transit-card {
    height: 220px;
  }

  .balance-amount {
    font-size: 1.75rem;
  }

  .btn-primary {
    padding: 0.625rem 1.25rem;
  }
}
</style>
