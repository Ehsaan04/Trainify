<template>
  <div class="workout-plan-container">
    <h2>Your Saved Workout Plan</h2>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading workout plan...</p>
    </div>

    <div v-else-if="!workoutPlan" class="no-plan">
      <p>No saved workout plan found. Please ask your trainer to generate one.</p>
    </div>

    <div v-else>
      <div class="rating-card">
        <h3 class="rating-title">Rate This Workout Plan</h3>
        <div class="rating-content">
          <div class="input-group">
            <label for="workout-name">Workout Name</label>
            <input
              v-model="workoutName"
              type="text"
              id="workout-name"
              class="name-input"
              placeholder="e.g. Chest and Biceps Focused Arnold Split"
            />
          </div>
          
          <div class="rating-group">
            <label>Your Rating</label>
            <div class="star-rating">
              <span
                v-for="star in 5"
                :key="star"
                class="star"
                :class="{ filled: star <= selectedRating }"
                @click="setRating(star)"
                @mouseover="hoverRating = star"
                @mouseleave="hoverRating = 0"
              >
                ★
              </span>
              <span class="rating-text" v-if="selectedRating">
                {{ ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][selectedRating - 1] }}
              </span>
            </div>
          </div>
          
          <button 
            @click="submitRating" 
            :disabled="selectedRating === 0 || !workoutName" 
            class="rating-btn"
            :class="{ submitted: ratingSubmitted }"
          >
            <span v-if="ratingSubmitted">✓ Rating Submitted</span>
            <span v-else>Submit Rating</span>
          </button>
        </div>
      </div>

      <div v-if="workoutNote" class="workout-note-card">
        <h3 class="note-title">Trainer's Workout Note</h3>
        <p class="note-text">{{ workoutNote }}</p>
      </div>


      <div class="workout-schedule">
        <div v-for="(exercises, day) in workoutPlan" :key="day" class="workout-day">
          <h3 class="day-title">{{ day }}</h3>
          <ul class="exercise-list">
            <li v-for="exercise in exercises" :key="exercise.exercise_name" class="exercise-item">
              <div class="exercise-name">{{ exercise.exercise_name }}</div>
              <div class="exercise-details">
                <span class="muscle-group">{{ exercise.target_muscle }}</span>
                <span class="equipment">{{ exercise.equipment }}</span>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

  
<script>
export default {
  name: "WorkoutPlans",
  props: {
    userData: {
      type: Object,
      required: true
    }
  },

  data() {
    return {
      workoutPlan: null,
      loading: true,
      workoutName: "",
      selectedRating: "",
      ratingSubmitted: false,
      latestPlanId: null,
      workoutNote: ""
    };
  },

  computed: {
    clientId() {
      return this.userData?.id || this.userData?.user_id;
    }
  },

  methods:{
    setRating(star) {
      this.selectedRating = star;
      this.ratingSubmitted = false; 
    },

    async submitRating() {
      //If one of the fields is missing, return without submitting
      if (!this.selectedRating || !this.latestPlanId || !this.workoutName) return;

      //POST request to endpoint to submit the rating
      try {
        const response = await fetch("http://127.0.0.1:8000/rate-workout-plan/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify({
            plan_id: this.latestPlanId,
            rating: this.selectedRating,
            workout_name: this.workoutName
          })
        });

        if (!response.ok) throw new Error("Failed to submit rating.");
        this.ratingSubmitted = true;
      } 

      catch (error) {
        console.error("Error submitting rating:", error);
      }
    },

    //GET request to fetch client's rating of their prescribed workout plan
    async fetchRating() {
      if (!this.latestPlanId) return;
      try {
        const response = await fetch(`http://127.0.0.1:8000/get-workout-plan-rating/${this.latestPlanId}/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include"
        });

        if (!response.ok) throw new Error("Failed to fetch rating");
        const data = await response.json();

        if (data.rating) {
          this.selectedRating = data.rating;
          this.ratingSubmitted = true;
        }
      } 

      catch (error) {
        console.error("Error fetching rating:", error);
      }
    },

    //Fetch note assigned to workout written by the trainer
    async fetchWorkoutNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/workout-plan-note/${this.clientId}/`, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
          credentials: "include"
        });

        if (!response.ok) throw new Error("Failed to fetch workout note");

        const data = await response.json();
        this.workoutNote = data.note || "";
      } 

      catch (error) {
        console.error("Error fetching workout note:", error);
      }
    }
  },

  //When component mounts, fetch the client's currently set workout plan
  async mounted() {
    try {
      const response = await fetch(`http://127.0.0.1:8000/get-saved-workout-plan/${this.clientId}/`, {
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error("Failed to fetch workout plan");
      }

      const data = await response.json();
      this.workoutPlan = data.workout_plan;
      this.latestPlanId = data.plan_id || null;
      if (this.latestPlanId) {
        await this.fetchRating();
      }
      await this.fetchWorkoutNote();
    } 

    catch (error) {
      console.error("Error fetching workout plan:", error);
    } 

    finally {
      this.loading = false;
    }
  }
};
</script>

<style scoped>
.workout-plan-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #333;
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-weight: 700;
  font-size: 1.8rem;
  position: relative;
  padding-bottom: 0.75rem;
}

.no-plan {
  background-color: #fff;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  color: #666;
  border-left: 4px solid #FFC107;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.rating-card {
  background-color: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.rating-title {
  background: linear-gradient(to right, #FF9800, #FFC107);
  color: white;
  margin: 0;
  padding: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
  text-align: center;
  letter-spacing: 0.5px;
}

.rating-content {
  padding: 1.5rem;
}

.input-group, .rating-group {
  margin-bottom: 1.25rem;
}

.input-group label, .rating-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.95rem;
}

.name-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.name-input:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
  outline: none;
}

.star-rating {
  display: flex;
  align-items: center;
  font-size: 2rem;
  cursor: pointer;
}

.star {
  color: #e0e0e0;
  transition: all 0.2s ease;
  position: relative;
  margin-right: 0.25rem;
}



.star.filled {
  color: #FFC107;
  text-shadow: 0 0 5px rgba(255, 193, 7, 0.5);
}

.rating-text {
  margin-left: 1rem;
  font-size: 1rem;
  color: #666;
  font-weight: 500;
}

.rating-btn {
  width: 100%;
  padding: 0.85rem;
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(to right, #4CAF50, #8BC34A);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.rating-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.rating-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

.rating-btn.submitted {
  background: #2E7D32;
}

.workout-schedule {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.workout-day {
  background-color: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  width: 100%;
}


.day-title {
  background: linear-gradient(to right, #4CAF50, #8BC34A);
  color: white;
  margin: 0;
  padding: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
  text-align: center;
  letter-spacing: 0.5px;
}

.exercise-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.exercise-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
}

.exercise-item:last-child {
  border-bottom: none;
}


.exercise-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.05rem;
}

.exercise-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #666;
}

.muscle-group {
  background-color: #e8f5e9;
  color: #4CAF50;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 500;
}

.equipment {
  background-color: #e3f2fd;
  color: #2196F3;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .workout-plan-container {
    padding: 1.5rem;
  }
  
  .exercise-details {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .muscle-group, .equipment {
    display: inline-block;
    margin-bottom: 0.5rem;
  }
  
  .star-rating {
    font-size: 1.75rem;
  }
}

.workout-note-card {
background-color: #fff;
border-radius: 10px;
box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
margin-bottom: 2rem;
padding: 1.25rem;
text-align: center;
}

.note-title {
background-color: #1976d2;
color: white;
margin: 0 -1.25rem 1rem -1.25rem;
padding: 1rem;
border-top-left-radius: 10px;
border-top-right-radius: 10px;
}

.note-text {
font-size: 1.05rem;
color: #333;
line-height: 1.6;
}

</style>