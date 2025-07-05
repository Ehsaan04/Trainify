<template>
  <div class="container mt-4">
    <h1 class="h3 mb-4">Trainer Leaderboard</h1>

    <!-- Active Season Leaderboard -->
    <div v-if="activeSeason">
      <h2 class="h5">Current Season: {{ activeSeason.season }}</h2>
      <ul class="mt-3 list-group">
        <li v-for="(entry, index) in activeSeason.leaderboard" :key="index" class="list-group-item">
          {{ index + 1 }}. {{ entry.client_username }} - {{ entry.points }} points
        </li>
      </ul>
      <h3 class="h6 mt-4">Rewards:</h3>
      <ul class="list-unstyled ms-3">
        <li>🥇 1st Place: {{ activeSeason.rewards.first }}</li>
        <li>🥈 2nd Place: {{ activeSeason.rewards.second }}</li>
        <li>🥉 3rd Place: {{ activeSeason.rewards.third }}</li>
      </ul>

      <div v-if="activeSeason && timeRemaining">
        <h4 class="h6 mt-3">Time Remaining: {{ timeRemaining }}</h4>
      </div>
    </div>

    <!-- Season Creation Form -->
    <div v-else>
      <h2 class="h5 mb-2">No Active Season</h2>
      <p>Create a new season below:</p>
      <form @submit.prevent="createSeason" class="mt-3">
        <div class="mb-3">
          <label class="form-label">Name:</label>
          <input v-model="seasonForm.name" type="text" required class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Start Date:</label>
          <input v-model="seasonForm.start_date" type="date" required class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">End Date:</label>
          <input v-model="seasonForm.end_date" type="date" required class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">First Place Reward:</label>
          <input v-model="seasonForm.first_place_reward" type="text" required class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Second Place Reward:</label>
          <input v-model="seasonForm.second_place_reward" type="text" required class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Third Place Reward:</label>
          <input v-model="seasonForm.third_place_reward" type="text" required class="form-control" />
        </div>
        <button type="submit" class="btn btn-primary">Create Season</button>
      </form>
    </div>

    <div v-if="errorMessage" class="alert alert-danger mt-4">
      {{ errorMessage }}
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      activeSeason: null,
      timeRemaining: '',
      seasonForm: {
        name: '',
        start_date: '',
        end_date: '',
        first_place_reward: '',
        second_place_reward: '',
        third_place_reward: ''
      },
      errorMessage: ''
    };
  },

  //When component mounts fetches the active season and calculates the time remaining within it
  mounted() {
    this.fetchActiveSeason();
    this.interval = setInterval(() => {
      if (this.activeSeason && this.activeSeason.end_date) {
        this.calculateTimeRemaining(this.activeSeason.end_date);
      }
    }, 30000); // every 30 seconds
  },

  //Stops running the interval when the component is removed from the DOM
  beforeUnmount() {
    clearInterval(this.interval); 
  },

  methods: {
    //Fetches the current season's leaderboard
    async fetchActiveSeason() {
      try {
        const response = await fetch('http://127.0.0.1:8000//get-leaderboard/', {
        credentials: 'include' 
      });

        if (response.ok) {
          const data = await response.json();
          this.activeSeason = data;
          if (data.end_date) {
            this.calculateTimeRemaining(data.end_date);
          }

        } 

        else if (response.status === 404) {
          this.activeSeason = null; 
        } 
        
        else {
          this.errorMessage = "Failed to fetch leaderboard.";
        }
      } 
      
      catch (error) {
        this.errorMessage = "Error fetching data.";
      }
    },

    //Hits endpoint with request for creating a new season
    //Provides data from season creation form in the payload
    async createSeason() {
      try {
        const response = await fetch('http://127.0.0.1:8000/create-season/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.seasonForm)
        });
        const data = await response.json();

        if (response.ok) {
          alert('Season created!');
          this.fetchActiveSeason();
        } 
        else {
          this.errorMessage = data.error || "Failed to create season.";
        }
      } 
      catch (error) {
        this.errorMessage = "Error creating season.";
      }
    },

    //Method for calculating how much time is remaining in the season
    calculateTimeRemaining(endDateStr) {
      const endDate = new Date(endDateStr);
      const now = new Date();

      //Time remaining in milliseconds
      const diffMs = endDate - now; 
      if (diffMs <= 0) {
        this.timeRemaining = 'Season has ended';
        return;
      }

      //Converts time remaining (ms) to days
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      //Calculates remaining hours after subtracting/modulo remaining days
      const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

      //Calculates remaining minutes after subtracting/modulo remaining hours
      const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

      //Template literal to format remaining time in user friendly way
      //User ternary operator to check if time frame is plural
      //e.g. if number of days is 1 don't add "s" to "day", otherwise add "s" to make it "days"
      this.timeRemaining = `${diffDays} day${diffDays !== 1 ? 's' : ''} ${diffHours} hour${diffHours !== 1 ? 's' : ''} ${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} remaining`;
    }

  }
};
</script>

<style scoped>
.trainer-leaderboard {
  max-width: 600px;
  margin: auto;
}
</style>
