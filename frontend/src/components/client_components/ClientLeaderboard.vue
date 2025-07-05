<template>
  <div class="container mt-4">
    <h1 class="h3 mb-4">Client Leaderboard</h1>

    <div v-if="activeSeason">
      <h2 class="h5">Current Season: {{ activeSeason.season }}</h2>
      <ul class="mt-3 list-group">
        <li
          v-for="(entry, index) in activeSeason.leaderboard"
          :key="index"
          class="list-group-item"
        >
          {{ index + 1 }}. {{ entry.client_username }} - {{ entry.points }} points
        </li>
      </ul>

      <h3 class="h6 mt-4">Rewards:</h3>
      <ul class="list-unstyled ms-3">
        <li>🥇 1st Place: {{ activeSeason.rewards.first }}</li>
        <li>🥈 2nd Place: {{ activeSeason.rewards.second }}</li>
        <li>🥉 3rd Place: {{ activeSeason.rewards.third }}</li>
      </ul>

      <div v-if="timeRemaining">
        <h4 class="h6 mt-3">Time Remaining: {{ timeRemaining }}</h4>
      </div>
    </div>

    <div v-else>
      <h2 class="h5">No Active Season</h2>
      <p>Your trainer has not started a season yet. Please check back later.</p>
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
      errorMessage: '',
      timeRemaining: '',
    };
  },

  mounted() {
    //When component mounts, fetches the currently active season
    this.fetchActiveSeason();

    //Refreshes time remaining every 60 secs
    this.interval = setInterval(() => {
        if (this.activeSeason && this.activeSeason.end_date) {
        this.calculateTimeRemaining(this.activeSeason.end_date);
        }
    }, 60000); 
    },

    //Gets rid of the time interval for refreshing when the component unmounts
    beforeUnmount() {
        clearInterval(this.interval); 
  },

  methods: {
    //GET request for fetching the active season from endpoint
    async fetchActiveSeason() {
      try {
        const response = await fetch('http://127.0.0.1:8000/get-leaderboard/', {
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          this.activeSeason = data;
          if (data.end_date) {
              this.calculateTimeRemaining(data.end_date);
          }
        } 

        //No season currently active
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

    calculateTimeRemaining(endDateStr) {
      //Gets season end date and current date to calculate time remaining
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
  .client-leaderboard {
    max-width: 600px;
    margin: auto;
  }
</style>
  