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
                  <button class="btn btn-sm btn-outline-primary" @click="changePhoto" disabled>
                    Change Photo (Coming Soon)
                  </button>
                </div>
                
                <div class="col-md-8">
                  <div v-if="!editMode">
                    <dl class="row">
                      <dt class="col-sm-3">Name:</dt>
                      <dd class="col-sm-9">{{ user.FullName }}</dd>
                      
                      <dt class="col-sm-3">Email:</dt>
                      <dd class="col-sm-9">{{ user.Email }}</dd>
                      
                      <dt class="col-sm-3">Phone:</dt>
                      <dd class="col-sm-9">{{ user.Phone || 'Not provided' }}</dd>
                      
                      <dt class="col-sm-3">Joined:</dt>
                      <dd class="col-sm-9">{{ formatDate(user.CreatedAt) }}</dd>
                    </dl>
                    
                    <button class="btn btn-primary" @click="toggleEditMode">Edit Profile</button>
                  </div>
                  
                  <div v-else>
                    <form @submit.prevent="saveProfile">
                      <div class="form-group mb-3">
                        <label for="name">Name</label>
                        <input 
                          type="text" 
                          id="name" 
                          class="form-control" 
                          v-model="editedUser.FullName" 
                          required
                          :class="{ 'is-invalid': validationErrors.FullName }"
                        >
                        <div class="invalid-feedback">{{ validationErrors.FullName }}</div>
                      </div>
                      
                      <div class="form-group mb-3">
                        <label for="email">Email</label>
                        <input 
                          type="email" 
                          id="email" 
                          class="form-control" 
                          v-model="editedUser.Email" 
                          required
                          :class="{ 'is-invalid': validationErrors.Email }"
                        >
                        <div class="invalid-feedback">{{ validationErrors.Email }}</div>
                      </div>
                      
                      <div class="form-group mb-3">
                        <label for="phone">Phone</label>
                        <input 
                          type="tel" 
                          id="phone" 
                          class="form-control" 
                          v-model="editedUser.Phone"
                          :class="{ 'is-invalid': validationErrors.Phone }"
                        >
                        <div class="invalid-feedback">{{ validationErrors.Phone }}</div>
                      </div>
                      
                      <div class="d-flex">
                        <button type="submit" class="btn btn-success me-2" :disabled="updating">
                          <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                          {{ updating ? 'Saving...' : 'Save Changes' }}
                        </button>
                        <button type="button" class="btn btn-secondary" @click="cancelEdit" :disabled="updating">Cancel</button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card mt-4 shadow">
            <div class="card-header bg-warning">
              <h3 class="mb-0">Account Settings</h3>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <h5>Change Password</h5>
                <button class="btn btn-outline-warning" @click="showChangePasswordModal = true">
                  Change Password
                </button>
              </div>
              
              <hr>
              
              <div>
                <h5>Delete Account</h5>
                <p class="text-danger">This action is irreversible. All your data will be permanently deleted.</p>
                <button class="btn btn-danger" @click="confirmDeleteAccount" :disabled="deleting">
                  <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                  {{ deleting ? 'Deleting...' : 'Delete Account' }}
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
    
    <!-- Password Modal -->
    <div v-if="showChangePasswordModal" class="modal fade show" style="display: block">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Change Password</h5>
            <button type="button" class="btn-close" @click="closePasswordModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <label for="currentPassword" class="form-label">Current Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="currentPassword" 
                  v-model="passwordForm.currentPassword"
                  required
                >
              </div>
              <div class="mb-3">
                <label for="newPassword" class="form-label">New Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="newPassword" 
                  v-model="passwordForm.newPassword"
                  required
                >
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm New Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="confirmPassword" 
                  v-model="passwordForm.confirmPassword"
                  required
                >
              </div>
              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" @click="closePasswordModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="changingPassword">
                  <span v-if="changingPassword" class="spinner-border spinner-border-sm me-2"></span>
                  {{ changingPassword ? 'Changing...' : 'Change Password' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';

export default {
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
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    };
  },
  computed: {
    ...mapState('auth', ['user']),
    userId() {
      return this.user?.UserId;
    },
    avatarUrl() {
      return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(this.user?.FullName || 'User')}`;
    }
  },
  watch: {
    // Watch for changes in the user object from Vuex store
    user: {
      immediate: true,
      handler(newUser) {
        if (!newUser) {
          this.error = 'Please log in to view your profile.';
        } else {
          this.error = null;
          // Initialize editedUser when user data is available
          this.editedUser = { ...newUser };
        }
      }
    }
  },
  created() {
    if (!this.user) {
      this.error = 'Please log in to view your profile.';
      return;
    }
    // Verify user data in the database
    this.$store.dispatch('auth/checkAuthState');
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
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
        const response = await axios.put(`${process.env.VUE_APP_USER_API_URL || 'http://localhost:5201'}/users/${this.userId}`, this.editedUser);
        
        if (response.data.code === 200) {
          // Update the Vuex store with the new user data
          this.$store.commit('auth/SET_USER', response.data.data);
          this.editMode = false;
        } else {
          throw new Error(response.data.message || 'Failed to update profile');
        }
      } catch (error) {
        console.error('Error updating profile:', error);
        if (error.response?.data?.validationErrors) {
          this.validationErrors = error.response.data.validationErrors;
        } else {
          this.error = error.response?.data?.message || 'Failed to update profile. Please try again.';
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
      if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        return;
      }
      
      this.deleting = true;
      
      try {
        await axios.delete(`http://localhost:5201/users/${this.userId}`);
        await this.$store.dispatch('auth/logout');
        this.$router.push('/');
        this.$toast.success('Your account has been deleted successfully.');
      } catch (error) {
        console.error('Error deleting account:', error);
        this.$toast.error('Failed to delete account. Please try again.');
      } finally {
        this.deleting = false;
      }
    },
    async changePassword() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        this.$toast.error('New passwords do not match.');
        return;
      }
      
      this.changingPassword = true;
      
      try {
        await axios.post(`http://localhost:5201/users/${this.userId}/change-password`, {
          currentPassword: this.passwordForm.currentPassword,
          newPassword: this.passwordForm.newPassword
        });
        
        this.closePasswordModal();
        this.$toast.success('Password changed successfully!');
      } catch (error) {
        console.error('Error changing password:', error);
        this.$toast.error(error.response?.data?.message || 'Failed to change password. Please try again.');
      } finally {
        this.changingPassword = false;
      }
    },
    closePasswordModal() {
      this.showChangePasswordModal = false;
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
    },
    changePhoto() {
      // Implementation of changePhoto method
    }
  }
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
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 2rem;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0,0,0,0.05);
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
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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

.modal {
  backdrop-filter: blur(8px);
}

.modal-content {
  border: none;
  border-radius: 20px;
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
}

.modal-header {
  border-bottom: 1px solid rgba(0,0,0,0.05);
  padding: 1.5rem;
}

.modal-body {
  padding: 2rem;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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
  background: rgba(0,0,0,0.5);
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
</style>