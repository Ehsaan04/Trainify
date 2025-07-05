<template>
    <div class="section">
      <h3>Meal Plan</h3>
      <div class="section-content">
        <p><strong>Daily Caloric Goal:</strong> {{ client.daily_calories }} kcal</p>
        <p><strong>Carbohydrates:</strong> {{ client.daily_carbs }}g</p>
        <p><strong>Protein:</strong> {{ client.daily_protein }}g</p>
        <p><strong>Fats:</strong> {{ client.daily_fat }}g</p>
        <p><strong>Fiber:</strong> {{ client.daily_fiber }}g</p>
        <p v-if="formattedGeneratedAt"><strong>Last meal plan was generated on</strong> {{ formattedGeneratedAt }}</p>

        <div class="mt-4">
          <label for="proteinMultiplier"><strong>Protein Multiplier (1.3 - 2.5):</strong></label>
          <input type="number" id="proteinMultiplier" v-model.number="proteinMultiplier" step="0.1" min="1.3" max="2.5" />
          <button @click="updateProteinMultiplier" class="generate-btn ml-2">Save</button>
          <p v-if="proteinUpdateFeedback" class="text-green-500 mt-2">{{ proteinUpdateFeedback }}</p>
        </div>
  
        <p><strong>Number of Meals:</strong>
          <select v-model="numMeals">
            <option v-for="n in [2,3]" :key="n" :value="n">{{ n }}</option>
          </select>
        </p>
  
        <button @click="generateMealPlan" :disabled="loadingMeal" class="generate-btn">
          {{ loadingMeal ? 'Generating...' : 'Generate Meal Plan' }}
        </button>
  
        <div v-if="Object.keys(groupedMeals).length > 0" class="meal-plan-results">
          <h4>Generated Meal Plan</h4>
          <div v-for="(foods, mealNumber) in groupedMeals" :key="mealNumber" class="meal-box">
            <h5>Meal {{ mealNumber }}</h5>
            <ul class="food-list">
              <li v-for="food in foods" :key="food.food_name">
                <strong>{{ food.food_name }}</strong>: {{ food.weight_in_grams }}g ({{ food.servings }} servings)
              </li>
            </ul>
            <div class="meal-totals">
              <p><strong>Total Calories:</strong> {{ getTotal(foods, "calories") }} kcal</p>
              <p><strong>Total Protein:</strong> {{ getTotal(foods, "protein") }}g</p>
              <p><strong>Total Carbs:</strong> {{ getTotal(foods, "carbs") }}g</p>
              <p><strong>Total Fats:</strong> {{ getTotal(foods, "fats") }}g</p>
              <p><strong>Total Fiber:</strong> {{ getTotal(foods, "fiber") }}g</p>
            </div>
            <button class="generate-btn mb-2" @click="regenerateMeal(mealNumber)">Regenerate Meal {{ mealNumber }}</button>
          </div>
        </div>
      </div>
  
      <div class="meal-box">
        <p><strong>Trainer Note:</strong></p>
        <textarea v-model="trainerNote" rows="3" class="w-full p-2 border rounded mb-3"></textarea>
        <button @click="saveTrainerNote" class="generate-btn mb-2">Save Note</button>
        <p v-if="noteSaveFeedback" class="text-green-500">{{ noteSaveFeedback }}</p>
      </div>
    </div>
  </template>
  
<script>
export default {
  name: "ClientMealPlan",
  props: {
    client: Object
  },

  data() {
    return {
      mealPlan: [],
      loadingMeal: false,
      numMeals: 3,
      proteinMultiplier: this.client.protein_multiplier || 1.8,
      trainerNote: "Write any extra data about the meal plan here",
      proteinUpdateFeedback: "",
      noteSaveFeedback: "",
      generatedAt: null
    };
  },

  computed: {
    //Groups foods/meals that have same meal number
    //E.g. all foods in meal 1 will be grouped together
    groupedMeals() {
      return this.mealPlan.reduce((acc, meal) => {
        if (!acc[meal.meal_number]) acc[meal.meal_number] = [];
        acc[meal.meal_number].push(meal);
        return acc;
      }, {});
    },

    //Formats date that meal plan was generated into user friendly format
    formattedGeneratedAt() {
      if (!this.generatedAt) return null;
      const date = new Date(this.generatedAt);
      return date.toLocaleString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    }

  },

  //When component mounts, fetch current meal plan and trainer note
  async mounted() {
    await this.fetchMealPlan();
    await this.fetchTrainerNote();
  },
  
  methods: {
    //Method for fetching meal plan with GET request to backend
    async fetchMealPlan() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/get-saved-meal-plan/${this.client.id}/`);
        const data = await response.json();
        this.mealPlan = data.meal_plans || [];
        this.generatedAt = data.generated_at || null;
      } 
      catch (error) {
        console.error("Failed to fetch meal plan", error);
      }
    },

    //Method for generating meal plan; hits backend with a POST request
    //Passes number of meals in payload
    async generateMealPlan() {
      this.loadingMeal = true;
      try {
        const response = await fetch(`http://127.0.0.1:8000/generate-meal-plan/${this.client.id}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ num_meals: this.numMeals })
        });
        const data = await response.json();
        this.mealPlan = data.meal_plans || [];
      } 
      catch (error) {
        console.error("Failed to generate meal plan", error);
      } 
      finally {
        this.loadingMeal = false;
      }
    },

    //Method for re-generating a single meal, rather than all of them
    async regenerateMeal(mealNumber) {
      try {
        await fetch(`http://127.0.0.1:8000/regenerate-meal/${this.client.id}/${mealNumber}/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ num_meals: this.numMeals }) 
        });
        await this.fetchMealPlan();
      } 
      catch (error) {
        console.error("Error regenerating meal", error);
      }
    },

    //Fetches note set by trainer for the meal plan, can contain extra tips or advice etc
    async fetchTrainerNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/meal-plan-note/${this.client.id}/`, {
          credentials: "include"
        });

        const data = await response.json();
        this.trainerNote = data.note && data.note.trim() !== "" 
        ? data.note 
        : "Write any extra information about the meal plan here.";

      } 
      catch (error) {
        console.error("Failed to fetch trainer note", error);
      }
    },

    //Submits meal plan note to backend with POST request
    async saveTrainerNote() {
      try {
        const response = await fetch(`http://127.0.0.1:8000/save-meal-plan-note/${this.client.id}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ note: this.trainerNote })
        });
        if (response.ok) {
          this.noteSaveFeedback = "Note saved!";
          setTimeout(() => (this.noteSaveFeedback = ""), 3000);
        }
      } 
      catch (error) {
        console.error("Failed to save trainer note", error);
      }
    },

    //Lets trainer change how many grams of protein per kg bodyweight
    //Adds extra customisation in the client's macros
    async updateProteinMultiplier() {
      try {
          const response = await fetch(`http://127.0.0.1:8000/update-protein-multiplier/${this.client.id}/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ protein_multiplier: this.proteinMultiplier }),
          credentials: "include"
          });

          if (response.ok) {
          this.proteinUpdateFeedback = "Updated successfully!";

          this.$emit("updateClientMacros", {
              protein_multiplier: this.proteinMultiplier,
              daily_protein: (this.client.weight * this.proteinMultiplier).toFixed(2)
          });

          setTimeout(() => (this.proteinUpdateFeedback = ""), 3000);
          }
      } 
      catch (error) {
          console.error("Failed to update multiplier", error);
      }
      },

    getTotal(foods, macro) {
      return foods.reduce((sum, f) => sum + f[macro], 0).toFixed(2);
    }
  }
};
</script>
  
<style scoped>
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

.meal-plan-results {
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

textarea {
  width: 100%;
  box-sizing: border-box;
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
</style>
