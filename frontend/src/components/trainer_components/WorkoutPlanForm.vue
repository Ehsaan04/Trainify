<template>
  <div class="workout-form-container">
    <h3>Customize Your Workout Plan</h3>

    <!-- Option to select number of workout days -->
    <label>How many days will your split be?</label>
    <select v-model="numDays" @change="generateDayInputs">
      <option v-for="n in 6" :key="n" :value="n">{{ n }} days</option>
    </select>

    <!-- Muscle checkboxes for each day -->
    <div v-for="(muscleGroups, index) in muscleGroupsPerDay" :key="index" class="day-section">
      <h4>Day {{ index + 1 }}</h4>
      <div v-for="muscle in availableMuscles" :key="muscle" class="checkbox-group">
        <input
          type="checkbox"
          :id="`day-${index}-${muscle}`"
          :value="muscle"
          v-model="muscleGroupsPerDay[index]"
        />
        <label :for="`day-${index}-${muscle}`">{{ muscle }}</label>
      </div>
    </div>

    <!-- Equipment checkboxes -->
    <h4>Select Available Equipment:</h4>
    <div class="equipment-container">
      <div v-for="equipment in availableEquipment" :key="equipment" class="checkbox-group">
        <input
          type="checkbox"
          :id="`equipment-${equipment}`"
          :value="equipment"
          v-model="selectedEquipment"
        />
        <label :for="`equipment-${equipment}`">{{ equipment }}</label>
      </div>
    </div>

    <!-- Submit button -->
    <button @click="submitWorkoutPlan" class="submit-btn">Generate Plan</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      //3 days is default
      numDays: 3, 

      //3 empty arrays for each day by default
      muscleGroupsPerDay: [[], [], []],
      availableMuscles: ["Chest", "Back", "Shoulders", "Biceps", "Triceps", "Quadriceps", "Hamstrings", "Glutes", "Forearms"],
      availableEquipment: ["Dumbbell", "Barbell", "Cable", "EZ Bar", "Pull-Up Bar", "Kettlebell"], 

      //Default selected equipment
      selectedEquipment: ["Dumbbell", "Barbell", "Cable"], 
    };
  },
  
  methods: {
    //Generates the days depending on how many are selected by the user
    generateDayInputs() {
      this.muscleGroupsPerDay = Array.from({ length: this.numDays }, () => []);
    },

    //Emits event to parent component, and provides submitted data from form
    submitWorkoutPlan() {
      this.$emit("submitWorkoutPlan", {
        workout_days: this.numDays,
        muscle_groups_per_day: this.muscleGroupsPerDay,
        equipment_available: this.selectedEquipment
      });
    }
  }
};
</script>

<style scoped>
.workout-form-container {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.day-section {
  margin-bottom: 15px;
}

.checkbox-group {
  display: flex;
  align-items: center;
  margin: 5px 0;
}

.equipment-container {
  display: flex;
  flex-wrap: wrap;
}

.submit-btn {
  margin-top: 15px;
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:hover {
  background: #0056b3;
}
</style>
