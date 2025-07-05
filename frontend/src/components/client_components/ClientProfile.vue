<template>
  <!-- Section showing all of the client's personal data -->
  <div>
    <h1>Welcome, {{ userData.first_name }} {{ userData.last_name }}!</h1>
    <p>Your Details (Client):</p>
    <ul>
      <li><strong>Date of Birth:</strong> {{ userData.date_of_birth }}</li>
      <li><strong>Height:</strong> {{ userData.height }} cm</li>
      <li>
        <strong>Weight:</strong> {{ userData.weight }} kg
        <button @click="toggleForm" class="edit-btn">Update</button>
      </li>
      <li><strong>Goal:</strong> {{ userData.goal }}</li>
    </ul>

    <!--Hides WeightProgress graph when form is open-->
    <WeightProgress v-if="!showForm" />

    <!-- Form to let client update their weight for a given date-->
    <div v-if="showForm" class="form-container">
      <h3>Update Weight</h3>
      <form @submit.prevent="submitWeight">
        <div class="form-group">
          <label for="weight">Weight (kg):</label>
          <input type="number" id="weight" v-model="newWeight" required />
        </div>

        <div class="form-group">
          <label for="date">Date:</label>
          <input type="date" id="date" v-model="weightDate" required />
        </div>

        <div class="form-group checkbox">
          <label>
            <input type="checkbox" v-model="isCurrentWeight" />
            <span>Set as Current Weight</span>
          </label>
        </div>

        <div class="form-buttons">
          <button type="submit" class="save-btn" :disabled="loading">
            {{ loading ? "Saving..." : "Save" }}
          </button>
          <button type="button" class="cancel-btn" @click="toggleForm">Cancel</button>
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      </form>

    </div>
  </div>
</template>


<script>
import WeightProgress from './WeightProgress.vue';

export default {
  name: 'ClientProfile',
  components:{
    WeightProgress
  },

  props: {
    userData: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      showForm: false,

      //Defaults to current weight
      newWeight: this.userData.weight, 

      //Defaults to current date
      weightDate: new Date().toISOString().substr(0, 10), 

      isCurrentWeight: false,
      loading: false,
      errorMessage: '',
      successMessage: '',
    };
  },
  
  methods: {
    refreshGraph() {
      //Calls function inside WeightProgress.vue
      this.$refs.weightProgress.fetchWeightProgress(); 
    },

    toggleForm() {
      this.showForm = !this.showForm;
      this.errorMessage = '';
      this.successMessage = '';
    },

    async submitWeight() {
      this.loading = true;
      this.errorMessage = '';
      this.successMessage = '';

      //POST request to submit weight entry to database, has weight value and date as payload
      try {
        const response = await fetch('http://127.0.0.1:8000/api/updateWeight', {
          method: 'POST',
          credentials: 'include', 
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            weight: this.newWeight,
            date: this.weightDate,
            is_current: this.isCurrentWeight
          })
        });

        const data = await response.json();

        if (response.ok) {
          this.successMessage = 'Weight was updated successfully';
          if (this.isCurrentWeight) {
            //Updates client's weight on frontend
            this.userData.weight = this.newWeight;
          }
          this.toggleForm();
          this.$emit("weight-updated");
        } 
        
        else {
          this.errorMessage = 'Error ocurred when trying to update weight';
        }
      } 

      catch (error) {
        this.errorMessage = 'Failed to reach backend';
      } 

      finally {
        this.loading = false;
      }
    },
  },
};
</script>
  
<style scoped>
/* Base styles */
div {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
  line-height: 1.6;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.8rem;
  border-bottom: 2px solid #eaeaea;
  padding-bottom: 10px;
}

h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 20px 0;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

li {
  padding: 10px 0;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

li:last-child {
  border-bottom: none;
}

li strong {
  margin-right: 10px;
  color: #555;
  min-width: 150px;
  display: inline-block;
}

/* Profile picture */
.profile-picture {
  margin: 20px 0;
  text-align: center;
}

.profile-picture img {
  max-width: 200px;
  border-radius: 50%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: 3px solid #fff;
}

/* Buttons */
.edit-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.3s;
}

.edit-btn:hover {
  background-color: #2980b9;
}

.form-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.save-btn, .cancel-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.save-btn {
  background-color: #2ecc71;
  color: white;
}

.save-btn:hover {
  background-color: #27ae60;
}

.save-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #e74c3c;
  color: white;
}

.cancel-btn:hover {
  background-color: #c0392b;
}

/* Form styling */
.form-container {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.checkbox label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox input {
  margin-right: 8px;
}

input[type="number"],
input[type="date"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input[type="number"]:focus,
input[type="date"]:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* Messages */
.error-message,
.success-message {
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}

.error-message {
  background-color: #ffecec;
  color: #e74c3c;
  border-left: 4px solid #e74c3c;
}

.success-message {
  background-color: #eaffea;
  color: #27ae60;
  border-left: 4px solid #27ae60;
}

/* Responsive design */
@media (max-width: 600px) {
  li {
    flex-direction: column;
    align-items: flex-start;
  }
  
  li strong {
    margin-bottom: 5px;
  }
  
  .edit-btn {
    margin-top: 5px;
  }
}
</style>