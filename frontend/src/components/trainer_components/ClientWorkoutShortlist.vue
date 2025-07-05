<template>
  <div class="mt-4">
    <h3>Client's Saved Workout Shortlist</h3>
    <div v-if="loading">Loading saved workouts...</div>

    <div v-else-if="plans.length === 0">No saved workouts found.</div>
    
    <div v-else>
      <div v-for="plan in plans" :key="plan.plan_id" class="card mb-3 p-3 shadow-sm">
        <h4>{{ plan.workout_name }}</h4>
        <p><strong>Rated by:</strong> {{ plan.rated_by }}</p>
        <p><strong>Frequency:</strong> {{ plan.training_frequency }}x/week</p>
        <p><strong>Created:</strong> {{ plan.created_at }}</p>

        <div v-for="(exercises, day) in plan.workout_plan" :key="day" class="ms-3">
          <h5>{{ day }}</h5>
          <ul>
            <li v-for="exercise in exercises" :key="exercise.exercise_name">
              <strong>{{ exercise.exercise_name }}</strong> 
              ({{ exercise.target_muscle }}, Equipment: {{ exercise.equipment }})
            </li>
          </ul>
        </div>
        <button
          class="btn btn-outline-primary btn-sm mt-2"
          @click="assignAsActive(plan.plan_id)"
          >
          <i class="bi bi-check-circle"></i> Set as Active Plan
          </button>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ClientWorkoutShortlist",
  props: {
    clientId: Number
  },

  data() {
    return {
      plans: [],
      loading: true
    };
  },

  //Trainer can set a routine from the client's shortlist as their new active workout
  methods: {
    async assignAsActive(planId) {
      if (!confirm("Set this plan as the client's active workout?")) return;

      try {
        const response = await fetch(`http://127.0.0.1:8000/assign-saved-workout/${this.clientId}/${planId}/`, {
            method: "POST",
            credentials: "include"
        });

        const data = await response.json();
        if (response.ok) {
            alert("Plan set as active!");
            this.$emit("refreshWorkout");  
        } 
        
        else {
            alert(data.error || "Failed to assign plan.");
        }
      } 
      
      catch (error) {
        console.error("Assignment error:", error);
        alert("Error assigning plan.");
      }
    }
  },

  //When component mounts, fetches all the client's shortlisted workouts so the trainer can view them
  async mounted() {
    try {
      const response = await fetch(`http://127.0.0.1:8000/get-client-saved-workouts/${this.clientId}/`, {
        credentials: "include"
      });

      const data = await response.json();
      if (response.ok) {
        this.plans = data.saved_workouts || [];
      } 
      
      else {
        console.error(data.error || "Failed to fetch saved workouts.");
      }
    } 
    
    catch (error) {
      console.error("Fetch error:", error);
    } 
    
    finally {
      this.loading = false;
    }
  }
};
</script>
