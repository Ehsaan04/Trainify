<template>
  <div class="trainer-search">
    <h2>Search for Trainers</h2>
    
    <div class="search-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search by username" 
        @input="searchTrainers" 
      />
    </div>

    <!-- Results -->
    <table v-if="trainers.length" class="table">

      <thead>
        <tr>
          <th>Username</th>
          <th>Bio</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="trainer in trainers" :key="trainer.username">
          <td>{{ trainer.username }}</td>
          <td>{{ trainer.bio || 'No bio available' }}</td>
          <td>
            <button 
              class="btn btn-primary" 
              @click="sendRequest(trainer.username)"
              :disabled="pendingRequests.includes(trainer.username)"
            >
              {{ pendingRequests.includes(trainer.username) ? 'Requested' : 'Request' }}
            </button>
          </td>
        </tr>
      </tbody>

    </table>

    <!-- No Results -->
    <p v-if="!trainers.length && searchQuery">No trainers found.</p>
  </div>
</template>

<script>
export default {
  name: 'TrainerSearch',
  data() {
    return {
      searchQuery: '', 
      trainers: [],   
      pendingRequests: [], 
    };
  },

  methods: {
    //Method for searching for a trainer by username
    async searchTrainers() {
      //If user input is empty, return nothing
      if (!this.searchQuery.trim()) {
        this.trainers = [];
        return;
      }

      //Otherwise, hit the endpoint and include the user input in the URL
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/search_trainers/?username=${encodeURIComponent(this.searchQuery)}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        //Store the received data and assign the received trainers to the local trainers variable
        const data = await response.json();
        this.trainers = data.trainers;
      } 

      catch (error) {
        console.error('Error searching for trainers:', error);
        this.trainers = [];
      }
    },

    //Method sends a POST request for linking with a trainer
    async sendRequest(trainerUsername) {
      try {
        const response = await fetch('http://127.0.0.1:8000/send_request/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ trainer_username: trainerUsername }),
        });

        const data = await response.json();
        if (data.success) {
          this.pendingRequests.push(trainerUsername);
          alert('Request successfully sent!');
        } 

        else {
          alert(data.error || 'Request failed to send.');
        }
      } 
      
      catch (error) {
        console.error('Error sending request:', error);
        alert('Failed to send request. Please try again.');
      }
    },
  },
};
</script>



<style scoped>
.trainer-search {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  text-align: center;
}

.search-bar input {
  width: 100%;
  padding: 10px;
  margin-bottom: 20px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
}

.table th {
  background-color: #f4f4f4;
}
</style>
