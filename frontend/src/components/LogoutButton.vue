<template>
  <button @click="logout" class="btn btn-danger">
    Logout
  </button>
</template>

<script>
export default {
  name: 'LogoutButton',
  methods: {
    async logout() {
      try {
        const response = await fetch('http://127.0.0.1:8000/logout/', {
          method: 'POST',
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error('Logout failed');
        }

        window.location.href = 'http://127.0.0.1:8000/';
      } 
      
      catch (error) {
        console.error('Error during logout:', error);
        alert('Failed to logout. Please try again.');
      }
    }
  }
};
</script>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 0.25rem;
}
</style>
