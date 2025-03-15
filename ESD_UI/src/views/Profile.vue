<template>
  <div class="container">
    <div class="row">
      <div class="col-md-8 mx-auto">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h2 class="mb-0">User Profile</h2>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-4 text-center">
                <div class="avatar-container mb-3">
                  <img src="https://via.placeholder.com/150" alt="Profile Avatar" class="rounded-circle img-fluid" />
                </div>
                <button class="btn btn-sm btn-outline-primary">Change Photo</button>
              </div>
              
              <div class="col-md-8">
                <div v-if="!editMode">
                  <dl class="row">
                    <dt class="col-sm-3">Name:</dt>
                    <dd class="col-sm-9">{{ user.name }}</dd>
                    
                    <dt class="col-sm-3">Email:</dt>
                    <dd class="col-sm-9">{{ user.email }}</dd>
                    
                    <dt class="col-sm-3">Phone:</dt>
                    <dd class="col-sm-9">{{ user.phone || 'Not provided' }}</dd>
                    
                    <dt class="col-sm-3">Joined:</dt>
                    <dd class="col-sm-9">{{ user.joinedDate }}</dd>
                  </dl>
                  
                  <button class="btn btn-primary" @click="toggleEditMode">Edit Profile</button>
                </div>
                
                <div v-else>
                  <form @submit.prevent="saveProfile">
                    <div class="form-group mb-3">
                      <label for="name">Name</label>
                      <input type="text" id="name" class="form-control" v-model="editedUser.name" required>
                    </div>
                    
                    <div class="form-group mb-3">
                      <label for="email">Email</label>
                      <input type="email" id="email" class="form-control" v-model="editedUser.email" required>
                    </div>
                    
                    <div class="form-group mb-3">
                      <label for="phone">Phone</label>
                      <input type="tel" id="phone" class="form-control" v-model="editedUser.phone">
                    </div>
                    
                    <div class="d-flex">
                      <button type="submit" class="btn btn-success me-2">Save Changes</button>
                      <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
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
              <button class="btn btn-danger" @click="confirmDeleteAccount">
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Password Modal (would be implemented with a modal component) -->
    <div v-if="showChangePasswordModal" class="modal-placeholder alert alert-info mt-3">
      Password change modal would appear here
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+65 9876 5432',
        joinedDate: '01 Jan 2023',
      },
      editMode: false,
      editedUser: {},
      showChangePasswordModal: false
    };
  },
  methods: {
    toggleEditMode() {
      this.editMode = true;
      this.editedUser = { ...this.user };
    },
    saveProfile() {
      this.user = { ...this.editedUser };
      this.editMode = false;
      // Here you would typically call an API to update the user profile
      alert('Profile updated successfully!');
    },
    cancelEdit() {
      this.editMode = false;
    },
    confirmDeleteAccount() {
      if (confirm('Are you sure you want to delete your account? This cannot be undone.')) {
        // Logic to delete account
        alert('Account deletion functionality would be implemented here.');
      }
    }
  }
};
</script>

<style scoped>
.container {
  margin-top: 30px;
  margin-bottom: 50px;
}

.avatar-container {
  width: 150px;
  height: 150px;
  margin: 0 auto;
  overflow: hidden;
}

.card {
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
}

.modal-placeholder {
  max-width: 500px;
  margin: 20px auto;
}
</style>