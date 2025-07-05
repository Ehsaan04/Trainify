<template>
  <div class="shortlist-container">
    <h2>Saved Workout Plans</h2>

    <div v-if="loading">Loading saved workouts...</div>

    <div v-else-if="savedWorkouts.length === 0">You haven't saved any plans yet.</div>

    <div v-else>
      <div v-for="plan in savedWorkouts" :key="plan.plan_id" class="shortlist-card">
        <h3>{{ plan.workout_name }}</h3>
        <p><strong>Rated by:</strong> {{ plan.rated_by }}</p>
        <p><strong>Frequency:</strong> {{ plan.training_frequency }}x/week</p>
        <p><strong>Created:</strong> {{ plan.created_at }}</p>

        <div v-for="(exercises, day) in plan.workout_plan" :key="day" class="day-block">
          <h4>{{ day }}</h4>
          <ul>
            <li v-for="exercise in exercises" :key="exercise.exercise_name">
              <strong>{{ exercise.exercise_name }}</strong>
              ({{ exercise.target_muscle }}, Equipment: {{ exercise.equipment }})
            </li>
          </ul>
        </div>

        <button @click="removePlan(plan.plan_id)" class="btn btn-outline-danger mt-3">
          <i class="bi bi-trash"></i> Remove from Shortlist
        </button>


      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "WorkoutShortlist",
  data() {
    return {
      savedWorkouts: [],
      loading: true,
    };
  },

  methods: {
    async removePlan(planId) {
      if (!confirm("Are you sure you want to remove this workout from your shortlist?")) return;

      try {
      const response = await fetch(`http://127.0.0.1:8000/remove-saved-workout/${planId}/`, {
          method: "DELETE",
          credentials: "include"
      });

      if (!response.ok) throw new Error("Failed to remove workout");

      //Removes deleted plan from local state
      this.savedWorkouts = this.savedWorkouts.filter(plan => plan.plan_id !== planId);
      } 
      catch (err) {
      console.error("Remove error:", err);
      }
    }
  },

  //When component mounts, fetches the client's shortlist
  async mounted() {
    try {
      const response = await fetch("http://127.0.0.1:8000/get-saved-recommended-workouts/", {
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to fetch saved workouts");

      const data = await response.json();
      this.savedWorkouts = data.saved_workouts || [];
    } 
    
    catch (err) {
      console.error("Error:", err);
    } 
    
    finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
.shortlist-container {
  padding: 1rem;
}
.shortlist-card {
  border: 1px solid #ccc;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 6px;
}
.day-block {
  margin-top: 1rem;
}
</style>
