<template>
  <div class="recommendations-container">
    <h2>Recommended Workouts</h2>
    <div v-if="loading">Loading recommendations...</div>
    <div v-else-if="recommendations.length === 0">No recommendations yet.</div>
    <div v-else>
      <div
            v-for="plan in recommendations"
            :key="plan.plan_id"
            class="recommendation-card"
          >
            <h3>{{ plan.workout_name }}</h3>
            <p><strong>Rated by:</strong> {{ plan.rated_by }}</p>
            <p><strong>Frequency:</strong> {{ plan.training_frequency }}x/week</p>
            <p><strong>Created:</strong> {{ plan.created_at }}</p>
            <button @click="viewPlan(plan.plan_id)" class="btn btn-primary btn-sm me-2">
              <i class="bi bi-eye"></i> View Full Plan
            </button>
            <button @click="savePlan(plan.plan_id)" class="btn btn-success btn-sm">
              <i class="bi bi-bookmark-plus"></i> Save Plan
            </button>
      </div>
    </div>

    <!-- Workout Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3>Workout Plan</h3>
        <div v-if="selectedWorkoutPlan">
          <div v-for="(exercises, day) in selectedWorkoutPlan" :key="day">
            <h4>{{ day }}</h4>
            <ul>
              <li
                v-for="exercise in exercises"
                :key="exercise.exercise_name"
              >
                <strong>{{ exercise.exercise_name }}</strong>
                ({{ exercise.target_muscle }}, Equipment: {{ exercise.equipment }})
              </li>
            </ul>
          </div>
        </div>
        <button @click="closeModal" class="btn btn-secondary mt-3">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RecommendedWorkouts",
  data() {
    return {
      recommendations: [],
      loading: true,
      showModal: false,               
      selectedWorkoutPlan: null
    };
  },

  //When component mounts, fetches the recommended workouts from the endpoint
  async mounted() {
    try {
      const response = await fetch("http://127.0.0.1:8000/get-recommended-workouts/", {
        credentials: "include"
      });

      if (!response.ok) throw new Error("Failed to fetch recommendations");
      const data = await response.json();
      this.recommendations = data.recommendations || [];
    } 

    catch (error) {
      console.error("Error:", error);
    } 

    finally {
      this.loading = false;
    }
  },

  methods: {
    //Method for viewing the full workout plan of a recommendation
    async viewPlan(planId) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/get-workout-plan-by-id/${planId}/`);
        const data = await response.json();
        this.selectedWorkoutPlan = data.workout_plan;
        this.showModal = true;
      } 

      catch (error) {
        console.error("Failed to load plan", error);
      }
    },
    
    //Method for saving a recommended workout plan - makes a POST request to the backend
    async savePlan(planId) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/save-recommended-workout/${planId}/`, {
          method: "POST",
          credentials: "include"
        });

        if (!response.ok) throw new Error("Failed to save workout plan");
        alert("Workout plan saved!");
      } 

      catch (error) {
        console.error("Save error:", error);
      }
    },

    closeModal() {
      this.showModal = false;
      this.selectedWorkoutPlan = null;
    }
  }
};
</script>
  
<style scoped>
.recommendations-container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}

.recommendation-card {
  background: #fff;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  background: #fff;
  padding: 25px;
  border-radius: 8px;
  max-width: 700px;
  width: 90%;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
</style>
