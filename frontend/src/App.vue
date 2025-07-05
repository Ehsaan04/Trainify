<script setup>
import { ref, onMounted } from 'vue';
import ClientDashboard from './components/client_components/ClientDashboard.vue';
import TrainerDashboard from './components/trainer_components/TrainerDashboard.vue';

//Stores user data
const userData = ref(null);

//Stores loading state
const loading = ref(true);

//Error state
const error = ref(null);

//Fetches user data from backend
async function fetchUserData() {
  try {
    userData.value = null;
    loading.value = true;

    const response = await fetch('http://127.0.0.1:8000/api/getUserData', {
      credentials: 'include'
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch user data');
    }

    userData.value = data;
  } 
  
  catch (error) {
    console.error('Error occurred attempting to fetch user data', error);
    error.value = 'User data failed to load.';
  } 
  
  finally {
    loading.value = false;
  }
}

//Calls fetchUserData when component mounts
onMounted(fetchUserData);
</script>


<template>
  <div>
    <div v-if="loading">
      <p>Loading...</p>
    </div>

    <div v-else-if="error">
      <p>{{ error }}</p>
    </div>

    <!--Conditional rendering based on user type-->
    <div v-else>
      <!--Passes user data as a prop to each dashboard-->
      <ClientDashboard v-if="userData.user_type === 'Client'" :user-data="userData" />
      <TrainerDashboard v-else-if="userData.user_type === 'Trainer'" :user-data="userData" />
      <p v-else>Unknown user type. Please contact support.</p>
    </div>
  </div>
</template>

<style scoped>
p {
  text-align: center;
  font-size: 1.2rem;
  color: #333;
}
</style>
