<template>
    <div v-if="userData">
      <h1>Welcome, Trainer {{ userData.first_name }} {{ userData.last_name }}!</h1>
      <p>Your Details:</p>
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
  h1 {
    font-size: 1.8rem;
    color: #333;
  }
  
  ul {
    list-style-type: none;
    padding: 0;
  }
  
  li {
    margin: 0.5rem 0;
  }
  
  img {
    display: block;
    margin-top: 1rem;
  }
  </style>
  