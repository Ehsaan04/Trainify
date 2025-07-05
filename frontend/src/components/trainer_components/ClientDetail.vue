<template>
  <div class="client-detail">
    <button @click="$emit('close')" class="back-btn">← Back</button>
    <button @click="unlinkClient" class="generate-btn">
      Unlink Client
    </button>

    <div class="client-info-container">
      <div class="client-info">
        <img
          v-if="client.profile_picture"
          :src="client.profile_picture"
          alt="Profile"
          class="profile-img"
        />
        <h2>{{ client.first_name }} {{ client.last_name }}</h2>
        <p><strong>Gender:</strong> {{ client.gender }}</p>
        <p><strong>Height:</strong> {{ client.height }} cm</p>
        <p><strong>Weight:</strong> {{ client.weight }} kg</p>

        <div class="mt-3">
          <label><strong>Goal:</strong></label>
          <select v-model="selectedGoal">
            <option
              v-for="(label, key) in goalOptions"
              :value="key"
              :key="key"
            >
              {{ label }}
            </option>
          </select>
          <button @click="updateClientGoal" class="generate-btn">
            Update Goal
          </button>
          <p v-if="goalUpdateFeedback" class="text-green-500 mt-2">
            {{ goalUpdateFeedback }}
          </p>
        </div>

        <p><strong>Priority Muscles: </strong>
          <span v-if="client.priority_muscles && client.priority_muscles.length">
            {{ formattedPriorityMuscles }}
          </span>
          <span v-else>None</span>
        </p>

        <div class="section mt-4">
          <h3>Assign Points</h3>
          <div class="section-content">
            <input
              v-model="pointsToAssign"
              type="number"
              min="1"
              placeholder="Enter points"
              class="border p-1 w-full mb-2"
            />
            <button
              @click="assignPoints"
              :disabled="assigningPoints"
              class="generate-btn"
            >
              {{ assigningPoints ? 'Assigning...' : 'Assign Points' }}
            </button>
            <p v-if="pointsFeedback" class="text-green-500 mt-2">
              {{ pointsFeedback }}
            </p>
            <p v-if="pointsError" class="text-red-500 mt-2">
              {{ pointsError }}
            </p>
          </div>
        </div>
      </div>

      <div class="weight-chart-wrapper">
        <h3>Client Weight Progress</h3>
        <WeightProgress :clientId="client.id" />
      </div>
    </div>

    <div class="plans-container">
      <!-- Meal Plan Section -->
      <ClientMealPlan
        :client="client"
        @updateClientMacros="updateClientMacros"
      />

      <!-- Workout Plan Section -->
      <div class="section">
        <h3>Workout Plan</h3>
        <div class="section-content">
          <div v-if="workoutPlan">
            <h4>Generated Workout Plan</h4>
            <div v-for="(exercises, day) in workoutPlan" :key="day">
              <h5>{{ day }}</h5>
              <ul>
                <li
                  v-for="(exercise, index) in exercises"
                  :key="exercise.exercise_name"
                  @click="newWorkoutGenerated ? refreshExercise(day, index, exercise) : null"
                  :class="{ 'clickable-exercise': newWorkoutGenerated }"
                >
                  <strong>{{ exercise.exercise_name }}</strong>
                  ({{ exercise.target_muscle }}, Equipment: {{ exercise.equipment }})
                </li>
              </ul>
            </div>

            <div class="button-row">
              <button
                @click="saveWorkoutPlan"
                :disabled="savingWorkout"
                class="generate-btn mt-3"
              >
                {{ savingWorkout ? 'Saving...' : 'Save Workout Plan' }}
              </button>
            </div>

            <p v-if="saveFeedback" class="text-green-500 mt-2">
              {{ saveFeedback }}
            </p>
          </div>

          <div v-if="!showWorkoutForm" class="button-row mt-4">
            <button
              @click="showWorkoutForm = true"
              class="generate-btn ml-2"
            >
              Generate New Workout Plan
            </button>
          </div>

          <WorkoutPlanForm
            v-if="showWorkoutForm"
            @submitWorkoutPlan="generateWorkoutPlan"
          />
        </div>

        <div class="meal-box">
          <p><strong>Trainer Workout Note:</strong></p>
          <textarea
            v-model="workoutNote"
            rows="3"
            class="w-full p-2 border rounded mb-3"
          ></textarea>
          <button @click="saveWorkoutNote" class="generate-btn mb-2">
            Save Note
          </button>
          <p v-if="workoutNoteSaveFeedback" class="text-green-500">
            {{ workoutNoteSaveFeedback }}
          </p>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-10">
          <ClientWorkoutShortlist
            :clientId="client.id"
            @refreshWorkout="fetchSavedWorkoutPlan"
          />
        </div>
      </div>
    </div>
  </div>
</template>



<script>
import WeightProgress from "../client_components/WeightProgress.vue";
import ClientMealPlan from "./ClientMealPlan.vue";
import ClientWorkoutShortlist from "./ClientWorkoutShortlist.vue";
import WorkoutPlanForm from "./WorkoutPlanForm.vue";

export default {
  components: {
    WorkoutPlanForm,
    ClientWorkoutShortlist,
    ClientMealPlan,
    WeightProgress
  },

  props: {
    client: Object
  },

  data() {
    return {
      selectedGoal: this.client.goal || '',
      // Notes
      trainerNote: "",
      noteSaveFeedback: "",
      workoutNote: "Write any extra info about the workout plan here.",
      workoutNoteSaveFeedback: "",

      // Workout Plan Data
      loadingWorkout: false,
      workoutPlan: null,
      showWorkoutForm: false, 

      //Saving workout data
      savingWorkout: false,
      workoutPlanSaved: false,

      newWorkoutGenerated: false,
      equipment_available: [],

      //points data
      currentPoints: 0,
      loadingPoints: false,
      pointsToAssign: 0,
      assigningPoints: false,
      pointsFeedback: '',
      pointsError: '',

      //Goals data
      goalUpdateFeedback: '',
      goalOptions: {
        lose_weight: "Lose Weight",
        gain_muscle: "Gain Weight",
        maintain_weight: "Maintain Current Weight"
      },
    };
  },

  computed: {
    //Groups meals by meal number
    groupedMeals() {
      return this.mealPlan.reduce((acc, meal) => {
        if (!acc[meal.meal_number]) {
          acc[meal.meal_number] = [];
        }
        acc[meal.meal_number].push(meal);
        return acc;
      }, {});
    },

    //Makes priority muscles array look more user friendly 
    formattedPriorityMuscles() {
      return this.client.priority_muscles
        .map(muscle => muscle.charAt(0).toUpperCase() + muscle.slice(1))
        .join(', ');
    }
  },

  //All these methods are called when the component is mounted
  async mounted() {
    await this.fetchSavedWorkoutPlan();
    await this.fetchSavedMealPlan();
    await this.fetchClientPoints();
    await this.fetchTrainerNote();
    await this.fetchWorkoutNote();
    console.log("ClientDetail mounted");
    this.proteinMultiplier = this.client.protein_multiplier || 1.8;
    this.selectedGoal = this.client.goal;
  },

  methods: {
    //Fetches how many points the client has in the current season (if one is activr)
    async fetchClientPoints() {
      this.loadingPoints = true;
      try {
        const response = await fetch(`http://127.0.0.1:8000/get-client-points/${this.client.id}/`, {
          method: "GET",
          credentials: 'include'
        });

        const data = await response.json();
        if (response.ok) {
          this.currentPoints = data.points;
        } 
        
        else {
          this.currentPoints = 0;
        }
      } 

      catch (error) {
        console.error("Error fetching points:", error);
        this.currentPoints = 0;
      } 

      finally {
        this.loadingPoints = false;
      }
    },

    //Method that allows trainers to give clients points
    async assignPoints() {
      if (this.pointsToAssign <= 0) {
        this.pointsError = "Please enter a valid number of points.";
        return;
      }

      this.assigningPoints = true;
      this.pointsFeedback = '';
      this.pointsError = '';

      //Hits backend with a POST request, providing client's ID and number of points to be given in payload
      try {
        const response = await fetch('http://127.0.0.1:8000/assign-points/', {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: 'include',
          body: JSON.stringify({
            client_id: this.client.id,
            points: this.pointsToAssign
          })
        });

        const data = await response.json();
        if (response.ok) {
          this.pointsFeedback = `Successfully assigned ${this.pointsToAssign} points!`;
          await this.fetchClientPoints();
          this.pointsToAssign = 0; 
        } 
        else {
          this.pointsError = data.error || "Failed to assign points.";
        }
      } 
      catch (error) {
        this.pointsError = "Error assigning points.";
      } 
      finally {
        this.assigningPoints = false;
      }
    },

    //Retrieves client's currently set workout plan with a GET request
    async fetchSavedWorkoutPlan() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/get-saved-workout-plan/${this.client.id}/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch saved workout plan.");
        }

        const data = await response.json();
        this.workoutPlan = data.workout_plan; 
        this.workoutPlanSaved = !!this.workoutPlan; 
        this.newWorkoutGenerated = false;
      } 
      catch (error) {
        console.error("Error fetching saved workout plan:", error);
      }
    },

    async generateWorkoutPlan(userInput) {
      //Hides form after submission
      this.showWorkoutForm = false; 
      this.equipment_available = userInput.equipment_available;

      //POST request to generate a workout routine and store in database
      try {
        const response = await fetch(`http://127.0.0.1:8000/generate-workout-plan/${this.client.id}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            workout_days: userInput.workout_days,
            muscle_groups_per_day: userInput.muscle_groups_per_day,
            difficulty_level: "Intermediate",
            equipment_available: userInput.equipment_available,
            priority_muscles: this.client.priority_muscles
          })
        });

        if (!response.ok) {
          throw new Error("Failed to generate workout plan.");
        }

        const data = await response.json();
        this.workoutPlan = data.workout_plan || {};
        this.newWorkoutGenerated = true;
        this.workoutPlanSaved = false;

      } 
      catch (error) {
        console.error("Error generating workout plan:", error);
      }
    },

    //Method to refresh a single exercise, rather than full routine. Uses POST request
    //Passes parameters of exercise to be refreshed so new exercise has same attributes
    async refreshExercise(day, index, exercise) {
      try {
        const response = await fetch('http://127.0.0.1:8000/refresh-exercise/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            target_muscle: exercise.target_muscle,
            equipment: exercise.equipment,
            mechanics: exercise.mechanics,
            current_exercise_name: exercise.exercise_name,
            allowed_equipment: this.equipment_available
          })
        });

        const data = await response.json();
        if (response.ok && data.new_exercise) {
          this.workoutPlan[day][index] = data.new_exercise;
        } 

        else {
          alert("No alternative exercise found!");
        }
      } 

      catch (error) {
        console.error("Error refreshing exercise:", error);
        alert("Error refreshing exercise.");
      }
    },

    //Method to save workout plan in the event that any exercises are refreshed
    async saveWorkoutPlan() {
      this.savingWorkout = true;
      this.saveFeedback = '';

      try {
        const response = await fetch(`http://127.0.0.1:8000/save-workout-plan/${this.client.id}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: 'include',
          body: JSON.stringify({
            workout_plan: this.workoutPlan
          })
        });

        const data = await response.json();
        if (response.ok) {
          this.saveFeedback = "Workout plan saved successfully!";
          this.workoutPlanSaved = true;
        } 
        else {
          this.saveFeedback = data.error || "Failed to save workout plan.";
        }
      } 

      catch (error) {
        console.error("Error saving workout plan:", error);
        this.saveFeedback = "Error saving workout plan.";
      } 

      finally {
        this.savingWorkout = false;
      }
    },

    //Fetch note assigned to meal plan
    async fetchTrainerNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/meal-plan-note/${this.client.id}/`, {
          credentials: 'include'
        });
        const data = await response.json();
        this.trainerNote = data.note || "";
      } 
      catch (error) {
        console.error("Failed to fetch trainer note", error);
      }
    },

    //Method for saving the note
    async saveTrainerNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/save-meal-plan-note/${this.client.id}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: 'include',
          body: JSON.stringify({ note: this.trainerNote })
        });
        if (response.ok) {
          this.noteSaveFeedback = "Note saved!";
          setTimeout(() => this.noteSaveFeedback = "", 3000);
        }
      } 
      catch (error) {
        console.error("Failed to save trainer note", error);
      }
    },

    async fetchWorkoutNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/workout-plan-note/${this.client.id}/`, {
          credentials: 'include',
          method: 'GET',
        });
        const data = await response.json();
        this.workoutNote = data.note && data.note.trim() !== ""
  ? data.note
  : "Write any extra info about the workout plan here";

      } 

      catch (error) {
        console.error("Failed to fetch workout note", error);
      }
    },

    async saveWorkoutNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/save-workout-plan-note/${this.client.id}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: 'include',
          body: JSON.stringify({ note: this.workoutNote })
        });

        if (response.ok) {
          this.workoutNoteSaveFeedback = "Workout note saved!";
          setTimeout(() => this.workoutNoteSaveFeedback = "", 3000);
        }
      } 

      catch (error) {
        console.error("Failed to save workout note", error);
      }
    },

    updateClientMacros(updated) {
      this.client.protein_multiplier = updated.protein_multiplier;
      this.client.daily_protein = updated.daily_protein;
    },

    async updateClientGoal() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/update-goal/${this.client.id}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ goal: this.selectedGoal })
        });

        const data = await response.json();
        if (response.ok) {
          this.client.goal = data.goal;
          this.client.daily_calories = data.daily_calories;
          this.client.daily_protein = data.daily_protein;
          this.client.daily_carbs = data.daily_carbs;
          this.client.daily_fat = data.daily_fat;
          this.client.daily_fiber = data.daily_fiber;
          this.goalUpdateFeedback = "Goal updated successfully!";
        } 
        else {
          this.goalUpdateFeedback = data.error || "Update failed.";
        }
      } 
      catch (error) {
        console.error("Error updating goal:", error);
        this.goalUpdateFeedback = "Server error.";
      } 
      finally {
        setTimeout(() => (this.goalUpdateFeedback = ""), 3000);
      }
    },

    async unlinkClient() {
      if (!confirm("Are you sure you want to unlink this client?")) return;

      try {
        const response = await fetch(`http://127.0.0.1:8000/unlink-client/${this.client.id}/`, {
          method: 'POST',
          headers: {
            "Content-Type": "application/json"
          },
          credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
          alert("Client successfully unlinked.");
          this.$emit("clientUnlinked", this.client.id);
        } 
        else {
          alert(data.error || "Failed to unlink client.");
        }
      } 
      catch (error) {
        console.error("Unlink error:", error);
        alert("Server error while unlinking.");
      }
    },

    // Calculate total for a macro across all foods in a meal
    getTotal(foods, macro) {
      return foods.reduce((sum, food) => sum + food[macro], 0).toFixed(2);
    },
  }
};
</script>



<style scoped>
.client-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

.back-btn {
  background-color: transparent;
  border: none;
  color: #3182ce;
  font-size: 16px;
  cursor: pointer;
  padding: 5px 0;
  margin-bottom: 20px;
  display: inline-block;
}

.back-btn:hover {
  text-decoration: underline;
}

.client-info {
  background-color: #edf2f7;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.profile-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px;
}

.section {
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section h3 {
  color: #2d3748;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 10px;
  margin-top: 0;
}

.section-content {
  padding: 10px 0;
}

.generate-btn {
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.generate-btn:hover {
  background-color: #3182ce;
}

.generate-btn:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.plans-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 768px) {
  .plans-container {
    grid-template-columns: 1fr 1fr;
  }
}

.meal-plan-results, 
.workout-plan-results {
  margin-top: 20px;
}

.meal-box {
  background-color: #ebf8ff;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
}

.meal-box h5 {
  color: #2b6cb0;
  margin-top: 0;
  margin-bottom: 10px;
}

.food-list {
  list-style-type: none;
  padding-left: 0;
}

.food-list li {
  padding: 5px 0;
  border-bottom: 1px dashed #bee3f8;
}

.meal-totals {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #bee3f8;
  font-size: 0.9em;
}

.meal-totals p {
  margin: 5px 0;
}

.clickable-exercise {
  cursor: pointer;
  transition: color 0.2s;
}

.clickable-exercise:hover {
  color: #3182ce;
  text-decoration: underline;
}

select {
  padding: 5px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  margin: 5px 0;
}

input[type="number"] {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  width: 100%;
}

.mt-2 {
  margin-top: 8px;
}

.mt-3 {
  margin-top: 12px;
}

.mt-4 {
  margin-top: 16px;
}

.text-green-500 {
  color: #48bb78;
}

.text-red-500 {
  color: #f56565;
}
textarea {
  width: 100%;
  box-sizing: border-box; /* ensures padding doesn't shrink the element */
}

.client-info-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
}

.client-info,
.weight-chart-wrapper {
  flex: 1;
  min-width: 300px;
  box-sizing: border-box;
}

.weight-chart-wrapper {
  background-color: #edf2f7;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.button-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

</style>
