<template>
  <div class="container">
    <div class="row">
      <div class="col-md-8 mx-auto">
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <template v-else>
          <div class="card shadow">
            <div class="card-header bg-primary text-white">
              <h2 class="mb-0">User Profile</h2>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4 text-center">
                  <div class="avatar-container mb-3">
                    <img :src="avatarUrl" :alt="user.FullName" class="rounded-circle img-fluid" />
                  </div>
                </div>

                <div class="col-md-8">
                  <div v-if="!editMode">
                    <dl class="row">
                      <dt class="col-sm-3">Name:</dt>
                      <dd class="col-sm-9">{{ user.FullName }}</dd>

                      <dt class="col-sm-3">Email:</dt>
                      <dd class="col-sm-9">{{ user.Email }}</dd>

                      <dt class="col-sm-3">Phone:</dt>
                      <dd class="col-sm-9">
                        {{ user.Phone || "Not provided" }}
                      </dd>

                      <dt class="col-sm-3">Joined:</dt>
                      <dd class="col-sm-9">{{ formatDate(user.CreatedAt) }}</dd>
                    </dl>

                    <button class="btn btn-primary" @click="toggleEditMode">
                      Edit Profile
                    </button>
                  </div>

                  <div v-else>
                    <form @submit.prevent="saveProfile">
                      <div class="form-group mb-3">
                        <label for="name">Name</label>
                        <input type="text" id="name" class="form-control" v-model="editedUser.FullName" required
                          :class="{ 'is-invalid': validationErrors.FullName }" />
                        <div class="invalid-feedback">
                          {{ validationErrors.FullName }}
                        </div>
                      </div>

                      <div class="form-group mb-3">
                        <label for="email">Email</label>
                        <input type="email" id="email" class="form-control" v-model="editedUser.Email" required
                          :class="{ 'is-invalid': validationErrors.Email }" />
                        <div class="invalid-feedback">
                          {{ validationErrors.Email }}
                        </div>
                      </div>

                      <div class="form-group mb-3">
                        <label for="phone">Phone</label>
                        <input type="tel" id="phone" class="form-control" v-model="editedUser.Phone"
                          :class="{ 'is-invalid': validationErrors.Phone }" />
                        <div class="invalid-feedback">
                          {{ validationErrors.Phone }}
                        </div>
                      </div>

                      <div class="d-flex">
                        <button type="submit" class="btn btn-success me-2" :disabled="updating">
                          <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                          {{ updating ? "Saving..." : "Save Changes" }}
                        </button>
                        <button type="button" class="btn btn-secondary" @click="cancelEdit" :disabled="updating">
                          Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Cards Section -->
          <div class="card shadow mt-4">
            <div class="card-header bg-info text-white">
              <h3 class="mb-0">Your Cards</h3>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading cards...</span>
                </div>
              </div>

              <div v-else-if="cards && cards.length">
                <div class="row g-4">
                  <div class="col-12">
                    <div v-for="card in cards" :key="card.CardId" class="mb-4">
                      <div class="card border-0 shadow-sm hover-effect">
                        <div class="card-body p-4">
                          <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="card-title mb-0">
                              <i class="bi bi-credit-card me-2"></i>
                              {{ card.CardSerialNumber }}
                            </h5>
                            <span class="badge bg-info">Debit Card</span>
                          </div>
                          <div class="row">
                            <div class="col-md-6">
                              <dl class="row mb-0">
                                <dt class="col-sm-4">Card ID:</dt>
                                <dd class="col-sm-8">{{ card.CardId }}</dd>
                                <dt class="col-sm-4">Status:</dt>
                                <dd class="col-sm-8">
                                  <span class="badge bg-success">Active</span>
                                </dd>
                              </dl>
                            </div>
                            <div class="col-md-6">
                              <div class="text-md-end">
                                <p class="text-muted mb-1">Available Balance</p>
                                <h4 class="text-success mb-0">
                                  ${{ card.Balance.toFixed(2) }}
                                </h4>
                                <button class="btn btn-success btn-sm mt-2" @click="topUpCard(card)"
                                  :disabled="isProcessing">
                                  <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
                                  <i v-else class="bi bi-plus-circle me-2"></i>
                                  Top Up
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-4">
                <i class="bi bi-credit-card-2-front display-4 text-muted mb-3"></i>
                <p class="text-muted">
                  No cards found. Apply for a card today!
                </p>
                <button class="btn btn-primary" @click="applyForCard" :disabled="applyingForCard">
                  <span v-if="applyingForCard" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-plus-circle me-2"></i>
                  {{ applyingForCard ? "Applying..." : "Apply for Card" }}
                </button>
              </div>
            </div>
          </div>
          <div class="card mt-4 shadow">
            <div class="card-header bg-warning">
              <h3 class="mb-0">Account Settings</h3>
            </div>
            <div class="card-body">
              <div>
                <h5>Delete Account</h5>
                <p class="text-danger">
                  This action is irreversible. All your data will be permanently
                  deleted.
                </p>
                <button class="btn btn-danger" @click="confirmDeleteAccount" :disabled="deleting">
                  <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                  {{ deleting ? "Deleting..." : "Delete Account" }}
                </button>
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

export default {
  setup() {
    const toast = useToast();
    return { toast }
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
      cards: [], // Add this to store user's cards
      applyingForCard: false, // Add this to track application state
      isProcessing: false,
      selectedCard: null
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
          this.toast?.success("Card application successful!");
        } else {
          throw new Error(response.data.message || "Failed to apply for card");
        }
      } catch (error) {
        console.error("Error applying for card:", error);
        this.toast?.error(
          error?.response?.data?.message || "Failed to apply for card"
        );
      } finally {
        this.applyingForCard = false;
      }
    },

    async fetchUserCards() {
      try {
        const response = await axios.get(
          `${process.env.VUE_APP_CARD_API_URL || "http://localhost:5203"}/cards`, {
          params: {
            user_id: this.userId
          }
        }
        );

        if (response?.data?.code === 200 && response?.data?.data?.cards) {
          this.cards = response.data.data.cards;
        } else {
          this.cards = []; // Set empty array if no cards found
          console.warn("No cards data in response:", response);
        }
      } catch (error) {
        console.error("Error fetching cards:", error);
        this.cards = []; // Set empty array on error
        // Use toast notification instead of accessing undefined error property
        this.$toast?.error(
          error.response?.data?.message || "Failed to fetch cards"
        );
      }
    },
    topUpCard(card) {
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
    }
  },
  async created() {
    // Add this to fetch cards when component is created
    if (this.userId) {
      await this.fetchUserCards();
    }
  },

  
};
</script>

<style scoped>
.container {
  padding: 2rem 1rem;
  background: #f8fafc;
  min-height: calc(100vh - 60px);
}

.card {
  border: none;
  border-radius: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 2rem;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.05);
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  padding: 1.5rem;
  border-bottom: none;
}

.card-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.card-body {
  padding: 2rem;
}

.avatar-container {
  width: 150px;
  height: 150px;
  position: relative;
  margin: 0 auto 1rem;
}

.avatar-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.avatar-container:hover img {
  transform: scale(1.05);
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #4f46e5;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #f1f5f9;
  color: #64748b;
  border: none;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-danger {
  background: #ef4444;
  border: none;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-control {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
}

dl.row {
  margin-bottom: 2rem;
}

dt {
  font-weight: 600;
  color: #64748b;
}

dd {
  color: #1e293b;
  font-weight: 500;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

.slide-up {
  animation: slideUp 0.5s ease-out;
}

/* Card variations */
.card.shadow {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.card.mt-4 {
  margin-top: 2rem;
}

.card-header.bg-warning {
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%) !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .card-body {
    padding: 1.5rem;
  }

  .avatar-container {
    width: 120px;
    height: 120px;
  }

  dl.row {
    margin-bottom: 1.5rem;
  }

  .btn {
    padding: 0.5rem 1rem;
  }
}

/* Loading animation */
.spinner-border {
  width: 3rem;
  height: 3rem;
  color: #4f46e5;
}

/* Alert styling */
.alert {
  border-radius: 12px;
  border: none;
  padding: 1rem 1.5rem;
}

.alert-danger {
  background: #fef2f2;
  color: #dc2626;
}

/* Form validation */
.is-invalid {
  border-color: #ef4444 !important;
}

.invalid-feedback {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* Password modal specific styles */
.modal.fade.show {
  background: rgba(0, 0, 0, 0.5);
}

.btn-close {
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.btn-close:hover {
  opacity: 1;
}

/* Settings section */
.card-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

/* Delete account section */
.text-danger {
  color: #ef4444 !important;
}

/* Loading spinner */
.text-center.my-5 {
  padding: 3rem 0;
}

.hover-effect {
  transition: all 0.3s ease;
}

.hover-effect:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
}

.badge.bg-info {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
}

.badge.bg-success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
}

.text-success {
  color: #16a34a !important;
}

.display-4 {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.card-title {
  color: #1e293b;
  font-size: 1.1rem;
  font-weight: 600;
}

dt {
  color: #64748b;
  font-weight: 500;
}

dd {
  color: #1e293b;
  font-weight: 500;
}

.btn-success.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-success.btn-sm:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(34, 197, 94, 0.2);
}
</style>
