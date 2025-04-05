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
          <div class="profile-page">
            <div class="profile-header">
              <div class="header-background"></div>
              <div class="header-content">
                <div class="header-left">
                  <div class="title-with-animation">
                    <div class="header-title">
                      <h1>My Transit Account</h1>
                      <p class="header-subtitle">Manage your transit cards and view your journey history</p>
                    </div>
                    <div class="lottie-container" ref="lottieContainer"></div>
                  </div>
                </div>
                <div class="header-right">
                  <div class="header-stats">
                    <div class="stat-card">
                      <div class="stat-icon">
                        <i class="bi bi-credit-card"></i>
                      </div>
                      <div class="stat-info">
                        <span class="stat-value">{{ cards.length }}</span>
                        <span class="stat-label">Active Cards</span>
                      </div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-icon">
                        <i class="bi bi-clock-history"></i>
                      </div>
                      <div class="stat-info">
                        <span class="stat-value">{{ transactions.length }}</span>
                        <span class="stat-label">Transactions</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="profile-content">
              <div class="row g-4">
                <!-- User Profile Card -->
                <div class="col-md-5">
                  <div class="card shadow profile-card">
                    <div class="card-header">
                      <h4 class="mb-0"><i class="bi bi-person-badge me-2"></i>Account Profile</h4>
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
                      <h4 class="mb-0"><i class="bi bi-gear-fill me-2"></i>Account Settings</h4>
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
                      <h4 class="mb-0">
                        <i class="bi bi-credit-card-2-front me-2"></i>My Transit Cards
                      </h4>
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
                      <h4 class="mb-0"><i class="bi bi-activity me-2"></i>Recent Activities</h4>
                    </div>
                    <div class="card-body">
                      <!-- Loading state -->
                      <div v-if="loadingTransactions" class="text-center py-3">
                        <div class="spinner-border spinner-border-sm text-primary" role="status">
                          <span class="visually-hidden">Loading transactions...</span>
                        </div>
                        <p class="mt-2">Loading your recent activities...</p>
                      </div>
                      
                      <!-- If there are transactions -->
                      <div v-else-if="transactions.length > 0" class="transaction-list">
                        <div v-for="transaction in transactions" :key="transaction.TransactionId" class="transaction-item">
                          <div class="transaction-icon" :class="getTransactionTypeClass(transaction)">
                            <i class="bi" :class="getTransactionTypeIcon(transaction)"></i>
                          </div>
                          <div class="transaction-details">
                            <div class="transaction-title">
                              {{ getTransactionTitle(transaction) }}
                            </div>
                            <div class="transaction-meta">
                              <span class="transaction-card">{{ formatCardNumber(transaction.CardNumber) }}</span>
                              <span class="transaction-date">{{ formatTransactionDate(transaction.CreatedAt) }}</span>
                            </div>
                          </div>
                          <div class="transaction-amount" :class="{'text-success': transaction.Amount > 0, 'text-danger': transaction.Amount < 0}">
                            {{ transaction.Amount > 0 ? '+' : '' }}${{ parseFloat(transaction.Amount).toFixed(2) }}
                          </div>
                        </div>
                        
                        <div v-if="hasMoreTransactions" class="text-center mt-3">
                          <button class="btn btn-link" @click="viewAllTransactions">
                            View All Transactions <i class="bi bi-chevron-right"></i>
                          </button>
                        </div>
                      </div>
                      
                      <!-- If no transactions -->
                      <div v-else class="text-center py-3">
                        <i class="bi bi-clock-history display-4 text-muted"></i>
                        <p class="mt-3">No recent activities to display.</p>
                        <p class="text-muted small">Your transit activities will appear here once you start using your card.</p>
                      </div>
                    </div>
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
import { ref, reactive, onMounted } from 'vue';

export default {
  setup() {
    const toast = useToast();
    const cardStates = reactive({});
    const lottieContainer = ref(null);

    onMounted(async () => {
      // Load the Lottie script
      if (!document.querySelector('script[src*="dotlottie-player"]')) {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = "https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs";
          script.type = "module";
          script.onload = resolve;
          script.onerror = reject;
          document.head.appendChild(script);
        });
      }

      // Wait a bit for the component to be registered
      setTimeout(() => {
        if (lottieContainer.value) {
          const player = document.createElement('dotlottie-player');
          player.setAttribute('src', 'https://lottie.host/dad50be8-9e8b-4602-b747-5fa46357ae7e/g90VC9zJ3c.lottie');
          player.setAttribute('background', 'transparent');
          player.setAttribute('speed', '1');
          player.setAttribute('loop', '');
          player.setAttribute('autoplay', '');
          player.style.width = '300px';
          player.style.height = '300px';
          player.style.margin = '-1rem 0';
          lottieContainer.value.appendChild(player);
        }
      }, 100);
    });

    return { toast, cardStates, lottieContainer }
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
      loadingTransactions: false,
      transactions: [],
      hasMoreTransactions: false,
      transactionLimit: 5,
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
        this.toast.success("Your account has been deleted successfully.");
      } catch (error) {
        console.error("Error deleting account:", error);
        this.toast.error("Failed to delete account. Please try again.");
      } finally {
        this.deleting = false;
      }
    },
    async applyForCard() {
      try {
        this.applyingForCard = true;
        
        if (!this.userId) {
          this.toast.error("Please log in to apply for a card.");
          return;
        }
        
        // Generate a random card serial number
        const serialNumber = "SN" + Math.random().toString(36).substr(2, 9).toUpperCase();

        const response = await axios.post(
          `${process.env.VUE_APP_CARD_API_URL || "http://localhost:5203"}/cards`,
          {
            UserId: this.userId,
            Balance: 0.0,
            CardSerialNumber: serialNumber,
          }
        );

        // Check if response exists and has the expected structure
        if (!response || !response.data) {
          throw new Error("Invalid server response");
        }

        // Success case
        if (response.data.code === 201) {
          await this.fetchUserCards();
          this.toast.success("Card application successful!");
          return;
        }

        // Server returned an error
        throw new Error(response.data.message || "Failed to apply for card");

      } catch (error) {
        console.error("Error applying for card:", error);
        // Improved error handling that doesn't try to access properties that might not exist
        const errorMessage = error.message || "An unexpected error occurred";
        this.toast.error(errorMessage);
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
        this.toast.error(
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
    async fetchTransactions() {
      if (!this.cards || this.cards.length === 0) {
        console.log('No cards found, skipping transaction fetch');
        this.transactions = [];
        this.hasMoreTransactions = false;
        return;
      }
      
      this.loadingTransactions = true;
      const allTransactions = [];
      
      try {
        // Create an array of promises to fetch transactions for all cards
        const transactionPromises = this.cards.map(card => {
          const apiUrl = new URL('https://personal-tkjmxw54.outsystemscloud.com/TransactionManagement/rest/TransactionsAPI/GetTransactionsByCardId');
          // Add CardId as a query parameter
          apiUrl.searchParams.append('CardId', card.CardId);
          
          console.log(`Fetching transactions for card ${card.CardId} from URL:`, apiUrl.toString());
          
          return axios.get(apiUrl.toString())
            .then(response => {
              console.log(`Received transactions for card ${card.CardId}:`, response.data);
              // Process successful response
              if (response.data && Array.isArray(response.data)) {
                // Add card information to each transaction
                return response.data.map(transaction => ({
                  ...transaction,
                  CardNumber: card.CardSerialNumber,
                  CardId: card.CardId
                }));
              }
              console.warn(`No valid transaction data for card ${card.CardId}`);
              return [];
            })
            .catch(error => {
              // Individual card transaction fetch failed - log but don't throw
              console.warn(`Failed to fetch transactions for card ${card.CardId}:`, error);
              return [];
            });
        });
        
        // Use Promise.allSettled to handle both fulfilled and rejected promises
        const results = await Promise.allSettled(transactionPromises);
        
        // Process all results, including those that succeeded
        results.forEach(result => {
          if (result.status === 'fulfilled' && Array.isArray(result.value)) {
            allTransactions.push(...result.value);
          }
        });
        
        // Sort all transactions by date, newest first
        allTransactions.sort((a, b) => new Date(b.CreatedAt) - new Date(a.CreatedAt));
        
        // Check if there are more transactions than our limit
        this.hasMoreTransactions = allTransactions.length > this.transactionLimit;
        
        // Store only the latest few transactions
        this.transactions = allTransactions.slice(0, this.transactionLimit);
        
        console.log('Processed transactions:', this.transactions);
        
      } catch (error) {
        console.error("Error in transaction processing:", error);
        this.toast.error("Failed to fetch transaction history");
      } finally {
        this.loadingTransactions = false;
      }
    },

    // Add this method to provide sample transactions when API fails
    getMockTransactions() {
      const now = new Date();
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      const lastWeek = new Date(now);
      lastWeek.setDate(lastWeek.getDate() - 7);
      
      return [
        {
          TransactionId: 1001,
          UserId: this.userId,
          CardId: this.cards?.[0]?.CardId || 0,
          CardNumber: this.cards?.[0]?.CardSerialNumber || 'SN12345678',
          Amount: 10.00,
          PreviousBalance: 5.00,
          NewBalance: 15.00,
          CreatedAt: now.toISOString()
        },
        {
          TransactionId: 1002,
          UserId: this.userId,
          CardId: this.cards?.[0]?.CardId || 0,
          CardNumber: this.cards?.[0]?.CardSerialNumber || 'SN12345678',
          Amount: -2.50,
          PreviousBalance: 17.50,
          NewBalance: 15.00,
          CreatedAt: yesterday.toISOString()
        },
        {
          TransactionId: 1003,
          UserId: this.userId,
          CardId: this.cards?.[0]?.CardId || 0,
          CardNumber: this.cards?.[0]?.CardSerialNumber || 'SN12345678',
          Amount: 20.00,
          PreviousBalance: 0.00,
          NewBalance: 20.00,
          CreatedAt: lastWeek.toISOString()
        }
      ];
    },
    
    formatTransactionDate(dateString) {
      if (!dateString) return "N/A";
      const date = new Date(dateString);
      
      const today = new Date();
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      
      // Format as "Today" or "Yesterday" or the actual date
      if (date.toDateString() === today.toDateString()) {
        return `Today, ${date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })}`;
      } else if (date.toDateString() === yesterday.toDateString()) {
        return `Yesterday, ${date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })}`;
      } else {
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined,
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        });
      }
    },
    
    getTransactionTypeIcon(transaction) {
      if (transaction.Amount > 0) {
        return "bi-plus-circle-fill"; // Top-up
      } else {
        return "bi-dash-circle-fill"; // Fare payment
      }
    },
    
    getTransactionTypeClass(transaction) {
      if (transaction.Amount > 0) {
        return "bg-success-soft"; // Top-up
      } else {
        return "bg-danger-soft"; // Fare payment
      }
    },
    
    getTransactionTitle(transaction) {
      if (transaction.Amount > 0) {
        return "Card Top-Up";
      } else {
        return "Transit Fare";
      }
    },
    
    formatCardNumber(cardNumber) {
      if (!cardNumber) return '';
      // Show only the last 4 characters of card number for privacy
      return `Card: ${cardNumber.slice(-4)}`;
    },
    
    viewAllTransactions() {
      // In a real app, you'd navigate to a dedicated transactions page
      // For now, we'll just show all transactions by fetching them again without a limit
      this.transactionLimit = 999;
      this.fetchTransactions();
      this.hasMoreTransactions = false; // Hide the "View All" button after expanding
    },
  },
  async created() {
    // Add this to fetch cards and transactions when component is created
    if (this.userId) {
      await this.fetchUserCards();
      await this.fetchTransactions();
    }

    // Check for payment status in URL parameters
    const status = this.$route.query.status;
    const message = this.$route.query.message;
    const amount = this.$route.query.amount;
    const newBalance = this.$route.query.new_balance;

    if (status) {
      switch (status) {
        case 'success':
          this.toast.success(
            `Payment successful! Amount: $${amount}${newBalance ? ` (New balance: $${newBalance})` : ''}`
          );
          this.fetchUserCards(); // Refresh cards after successful payment
          this.fetchTransactions(); // Also refresh transaction history
          break;
        case 'failed':
          this.toast.error(message || 'Payment failed');
          break;
        case 'error':
          this.toast.error(message || 'An error occurred');
          break;
      }

      // Clean up URL parameters
      this.$router.replace({ query: {} });
    }
  },
};
</script>

<style scoped>
/* Import Google Fonts - with additional weights and features */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Variables */
:root {
  --primary-color: #4F46E5;
  --primary-light: #6366F1;
  --primary-dark: #4338CA;
  --secondary-color: #818CF8;
  --accent-color: #C7D2FE;
  --font-family-base: Avenir, Helvetica, Arial, sans-serif;
}

/* Base Styles */
.container {
  padding: 0px 1rem;
  background: #f8f9fa;
  min-height: calc(100vh - 60px);
  font-family: var(--font-family-base);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  max-width: 1200px;
  margin: 0 auto;
}

/* Main Profile Section */
.profile-page {
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
  overflow-x: hidden;
}

.profile-header {
  position: relative;
  padding: 4rem 0;
  overflow: visible;
  color: white;
  min-height: 300px;
  width: 100%;
  background: linear-gradient(135deg, #1e4d8e 0%, #2870c4 100%);
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff10" fill-opacity="1" d="M0,32L48,42.7C96,53,192,75,288,101.3C384,128,480,160,576,165.3C672,171,768,149,864,128C960,107,1056,85,1152,80C1248,75,1344,85,1392,90.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
  background-position: bottom;
  background-repeat: no-repeat;
  background-size: cover;
  opacity: 0.1;
  z-index: 1;
}

.header-content {
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  position: relative;
  flex: 1;
  min-width: 0;
  max-width: 650px;
}

.header-right {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-left: 2rem;
}

.header-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 0;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1.25rem;
  border-radius: 16px;
  width: 220px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.title-with-animation {
  position: relative;
  min-height: 250px;
  display: flex;
  align-items: center;
}

.header-title {
  position: relative;
  z-index: 10;
  max-width: 600px;
}

.header-title h1 {
  font-size: 3rem;
  font-weight: 700;
  margin: 0;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.header-subtitle {
  font-size: 1.25rem;
  margin: 1.5rem 0 0;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
  line-height: 1.6;
  max-width: 500px;
}

/* Decorative elements */
.header-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(to bottom, transparent, rgba(255, 255, 255, 0.1));
  z-index: 1;
}

@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    gap: 2rem;
  }

  .header-right {
    margin-left: 0;
    width: 100%;
  }

  .header-stats {
    flex-direction: row;
    justify-content: center;
    flex-wrap: wrap;
  }

  .stat-card {
    width: calc(50% - 1rem);
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 1rem;
  }

  .stat-card {
    width: 100%;
    min-width: 0;
  }

  .profile-content {
    padding: 1.5rem;
  }

  .container {
    padding: 1rem;
  }
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
  letter-spacing: -0.01em;
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
  letter-spacing: -0.01em;
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
  letter-spacing: -0.01em;
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

.empty-card-placeholder {
  font-size: 4rem;
  color: #ccc;
  margin-bottom: 1rem;
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

/* Transaction list styling */
.transaction-list {
  margin: 0;
}

.transaction-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s ease;
}

.transaction-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.transaction-item:last-child {
  border-bottom: none;
}

.transaction-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.bg-success-soft {
  background-color: rgba(0, 168, 84, 0.1);
}

.bg-success-soft i {
  color: #00a854;
  font-size: 1.25rem;
}

.bg-danger-soft {
  background-color: rgba(237, 76, 103, 0.1);
}

.bg-danger-soft i {
  color: #ed4c67;
  font-size: 1.25rem;
}

.transaction-details {
  flex: 1;
}

.transaction-title {
  font-weight: 500;
  font-size: 0.95rem;
  color: #2c3e50;
  letter-spacing: -0.01em;
}

.transaction-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8125rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.transaction-card {
  color: #495057;
  font-weight: 500;
}

.transaction-amount {
  font-weight: 600;
  font-size: 1rem;
}

.profile-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Container adjustments */
.container {
  padding: 2rem 1rem;
  background: #f8f9fa;
  min-height: calc(100vh - 60px);
  font-family: var(--font-family-base);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.row {
  margin: 0;
}

.col-lg-10 {
  padding: 0;
}

@media (max-width: 768px) {
  .profile-content {
    padding: 1rem;
  }

  .card {
    margin-bottom: 1rem;
  }

  .card-header {
    padding: 1rem;
  }
}
</style>
