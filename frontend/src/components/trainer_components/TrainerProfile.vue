<template>
    <div v-if="userData">
      <h1>Welcome, Trainer {{ userData.first_name }} {{ userData.last_name }}!</h1>
      <p>Your Details: </p>
      <ul>
        <li><strong>Bio:</strong> {{ userData.bio }}</li>
      </ul>
      <div v-if="userData.profile_picture_url">
        <img
          :src="userData.profile_picture_url"
          alt="Profile Picture"
          style="max-width: 200px; border-radius: 50%;"
        />
      </div>
    </div>
    <div v-else>
      <p>Loading user data...</p>
    </div>
  </template>
  
  <script>
  export default {
    name: "TrainerProfile",
    props: {
      userData: {
        type: Object,
        required: true,
      },
    },
  };
  </script>
  
<style scoped>
.profile-card {
  max-width: 500px;
  margin: 2rem auto;
  padding: 1.5rem;
  border-radius: 1rem;
  background-color: #ffffff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-image img {
  max-width: 150px;
  border-radius: 50%;
  border: 4px solid #4CAF50;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.profile-details {
  text-align: center;
  margin-top: 1.2rem;
}

h1 {
  font-size: 1.6rem;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.details-heading {
  font-weight: 600;
  margin: 0.8rem 0 0.5rem;
  color: #555;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  font-size: 1rem;
  margin: 0.3rem 0;
  color: #333;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #777;
}
</style>