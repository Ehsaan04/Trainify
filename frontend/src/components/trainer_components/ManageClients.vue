<template>
  <div class="client-container">
    <h2 class="title">My Clients</h2>

    <div v-if="error" class="alert">
      {{ error }}
    </div>

    <div v-else-if="loading" class="loading">
      <p>Loading clients...</p>
      <div class="spinner"></div>
    </div>

    <div v-else class="client-list-container">
      <ul v-if="clients.length > 0" class="client-list">
        <li
          v-for="client in clients"
          :key="client.id"
          class="client-card"
          @click="$emit('clientSelected', client)" 
        >
          <div class="client-image">
            <img
              v-if="client.profile_picture"
              :src="client.profile_picture"
              alt="Profile"
              class="profile-pic"
            />
            <div v-else class="profile-placeholder">
              {{ client.first_name.charAt(0) }}{{ client.last_name.charAt(0) }}
            </div>
          </div>

          <div class="client-info">
            <h5 class="client-name">{{ client.first_name }} {{ client.last_name }}</h5>
            <div class="client-details">
              <p><strong>Email:</strong> {{ client.email }}</p>
              <p><strong>Gender:</strong> {{ client.gender }}</p>
              <div class="metrics">
                <p><strong>Height:</strong> {{ client.height }} cm</p>
                <p><strong>Weight:</strong> {{ client.weight }} kg</p>
              </div>
              <p class="goal"><strong>Goal:</strong> {{ client.goal_label }}</p>
            </div>
          </div>

        </li>
      </ul>
      <p v-else class="no-clients">You have no assigned clients.</p>
    </div>
  </div>
</template>


<script>
export default {
  name: "ManageClients", 
  data() {
    return {
      clients: [],
      loading: true,
      error: null,
    };
  },

  methods: {
    //Fetches the data of all the clients assigned to the trainer
    async fetchClients() {
      try {
        const response = await fetch("http://127.0.0.1:8000/trainer/clients/", {
          credentials: "include",
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to load clients.");
        }

        this.clients = data.clients;
      } 
      
      catch (error) {
        this.error = error.message || "Failed to load clients.";
      } 
      
      finally {
        this.loading = false;
      }
    },
  },
  
  mounted() {
    this.fetchClients();
  },
};
</script>

<style scoped>
.client-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.title {
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 600;
  font-size: 1.75rem;
}

.alert {
  background-color: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-top: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.client-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.client-card {
  display: flex;
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  border: 1px solid #eee;
}

.client-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.client-image {
  width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  padding: 1rem;
}

.profile-pic {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-placeholder {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 600;
}

.client-info {
  flex: 1;
  padding: 1.25rem;
}

.client-name {
  margin: 0 0 0.75rem 0;
  color: #333;
  font-weight: 600;
  font-size: 1.25rem;
}

.client-details p {
  margin: 0.5rem 0;
  color: #555;
  font-size: 0.9rem;
}

.metrics {
  display: flex;
  gap: 1.5rem;
  margin: 0.5rem 0;
}

.goal {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eee;
  color: #555;
}

.no-clients {
  text-align: center;
  color: #777;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 0.5rem;
  font-style: italic;
}

@media (max-width: 768px) {
  .client-list {
    grid-template-columns: 1fr;
  }
  
  .client-card {
    flex-direction: column;
  }
  
  .client-image {
    width: 100%;
    padding: 1.5rem 1rem;
  }
  
  .metrics {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>



