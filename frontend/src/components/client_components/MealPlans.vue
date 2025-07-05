<template>
  <div class="meal-plan-container">
    <h2>Your Saved Meal Plan</h2>

    <div v-if="loading" class="loading">Loading meal plan...</div>

    <div v-else-if="!mealPlan.length">
      <p>No meal plan found. Please ask your trainer to generate one.</p>
    </div>

    <div v-else>
      <div v-for="(foods, mealNumber) in groupedMeals" :key="mealNumber" class="meal-box">
        <h3>Meal {{ mealNumber }}</h3>
        <ul class="food-list">
          <li v-for="food in foods" :key="food.food_name">
            <span><strong>{{ food.food_name }}</strong>: {{ food.weight_in_grams }}g ({{ food.servings }} serving<span v-if="food.servings > 1">s</span>)</span>
          </li>
        </ul>
        <div class="meal-totals">
          <p><strong>Total Calories:</strong> {{ getTotal(foods, 'calories') }} kcal</p>
          <p><strong>Protein:</strong> {{ getTotal(foods, 'protein') }}g</p>
          <p><strong>Carbs:</strong> {{ getTotal(foods, 'carbs') }}g</p>
          <p><strong>Fats:</strong> {{ getTotal(foods, 'fats') }}g</p>
          <p><strong>Total Fiber:</strong> {{ getTotal(foods, "fiber") }}g</p>
        </div>
      </div>

      <div v-if="trainerNote" class="meal-box">
        <h3>Trainer's Note</h3>
        <p>{{ trainerNote }}</p>
      </div>

    </div>
  </div>
</template>
  
<script>
export default {
  name: "MealPlans",
  props: {
    userData: {
      type: Object,
      required: true
    }
  },

  data() {
    return {
      mealPlan: [],
      trainerNote: "",
      loading: true
    };
  },

  computed: {
    //Groups meals/foods with same meal number together
    //e.g. all foods that are part of meal 1 are grouped together
    groupedMeals() {
      return this.mealPlan.reduce((acc, meal) => {
        if (!acc[meal.meal_number]) acc[meal.meal_number] = [];
        acc[meal.meal_number].push(meal);
        return acc;
      }, {});
    }
  },

  //GET request to retrieve the note set by the trainer for the meal plan
  methods: {
    async fetchTrainerNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/meal-plan-note/${this.userData.id}/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include"
        });

        if (!response.ok) throw new Error("Was unable to fetch note for meal plan");
        const data = await response.json();
        this.trainerNote = data.note || "";
      } 
      catch (error) {
        console.error("Error fetching note for meal plan:", error);
      }
    },

    //GET request to retrieve the client's current meal plan
    async fetchMealPlan() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/get-saved-meal-plan/${this.userData.id}/`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include"
        });

        if (!response.ok) throw new Error("Failed to fetch meal plan");
        const data = await response.json();
        this.mealPlan = data.meal_plans || [];
      } 

      catch (error) {
        console.error("Error fetching meal plan:", error);
      } 

      finally {
        this.loading = false;
      }
    },

    //Returns sum of a given macro across a list of foods
    //e.g. total protein in meal 1
    getTotal(foods, macro) {
      return foods.reduce((sum, food) => sum + food[macro], 0).toFixed(2);
    }
  },
  
  //When component mounts, fetch the meal plan and note
  mounted() {
    this.fetchMealPlan();
    this.fetchTrainerNote();
  }
};
</script>
  
<style scoped>
.meal-plan-container {
  max-width: 800px;
  margin: auto;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  font-style: italic;
  color: gray;
}

.meal-box {
  background: #f7f9fc;
  border-left: 4px solid #007bff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.food-list {
  list-style: none;
  padding-left: 0;
}

.food-list li {
  font-size: 16px;
  margin-bottom: 6px;
}

.meal-totals {
  margin-top: 10px;
  font-weight: bold;
  border-top: 1px solid #ddd;
  padding-top: 8px;
}
</style>
  