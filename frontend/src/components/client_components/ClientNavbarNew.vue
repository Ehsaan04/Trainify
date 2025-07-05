<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Trainify</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">

            <li class="nav-item" :class="{ active: activeView === 'profile' }" @click="activeView = 'profile'">
              <a class="nav-link" href="javascript:void(0)">Profile</a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'workoutPlans' }" @click="activeView = 'workoutPlans'">
              <a class="nav-link" href="javascript:void(0)">Workout Plans</a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'recommendedWorkouts' }" @click="activeView = 'recommendedWorkouts'">
              <a class="nav-link" href="javascript:void(0)">Recommended Workouts</a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'workoutShortlist' }" @click="activeView = 'workoutShortlist'">
              <a class="nav-link" href="javascript:void(0)">Workout Shortlist</a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'mealPlans' }" @click="activeView = 'mealPlans'">
              <a class="nav-link" href="javascript:void(0)"> Meal Plans </a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'clientLeaderboard' }" @click="activeView = 'clientLeaderboard'">
              <a class="nav-link" href="javascript:void(0)"> Leaderboard </a>
            </li>

            <li class="nav-item" :class="{ active: activeView === trainerTab }" @click="">
              <a class="nav-link" :style="trainerStyle" href="javascript:void(0)">
                {{ trainerText }}
              </a>
            </li>

            <li class="nav-item">
              <a class="nav-link text-danger" href="javascript:void(0)" @click="logout">
                Logout
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="mt-4">
      <ClientProfile v-if="activeView === 'profile'" :userData="userData" @weight-updated="refreshGraph"/>
      <WorkoutPlans v-if="activeView==='workoutPlans'" :userData="userData" />
      <MealPlans v-if="activeView==='mealPlans'" :userData="userData"/>
      <TrainerSearch v-if="activeView==='trainerLink'" />
      <TrainerInfo v-if="activeView==='trainerInfo'" :trainerData="userData.trainer" />
      <RecommendedWorkouts v-if="activeView==='recommendedWorkouts'"  />
      <ClientLeaderboard v-if="activeView==='clientLeaderboard'"/>
      <WorkoutShortlist v-if="activeView==='workoutShortlist'"/>
    </div>
  </div>
</template>

<script>
import ClientProfile from "./ClientProfile.vue";
import WorkoutPlans from "./WorkoutPlans.vue";
import MealPlans from "./MealPlans.vue"
import TrainerSearch from "./TrainerSearch.vue";
import TrainerInfo from "./TrainerInfo.vue"; 
import RecommendedWorkouts from "./RecommendedWorkouts.vue";
import ClientLeaderboard from "./ClientLeaderboard.vue";
import WorkoutShortlist from "./WorkoutShortlist.vue";

export default {
  name: "ClientNavbarNew",
  components: {
    ClientProfile,
    WorkoutPlans,
    TrainerSearch,
    TrainerInfo,
    MealPlans,
    RecommendedWorkouts,
    ClientLeaderboard,
    WorkoutShortlist
  },

  props: {
    userData: {
      type: Object,
      required: true,
    }
  },

  data() {
    return {
      //Default to profile view
      activeView: "profile",
    };
  },

  computed: {
    //Conditional text shown depending on whether client is linked to trainer or not
    trainerText() {
      return this.userData.has_trainer ? "Trainer Linked" : "Trainer: Not Linked";
    },

    //If client is linked to a trainer, green colour, otherwise red
    trainerStyle() {
      return { color: this.userData.has_trainer ? "green" : "red" };
    },

    trainerTab() {
      return this.userData.has_trainer ? "trainerInfo" : "trainerLink";
    }
  },

  methods: {
    //Switch tab when each element on nav bar is clicked
    handleTrainerClick() {
      this.activeView = this.trainerTab; 
    },

    logout() {
      window.location.href = "http://127.0.0.1:8000/logout/";
    }
  }
};
</script>

<style scoped>
.navbar-nav .nav-item .nav-link {
  cursor: pointer;
}

.navbar-nav .nav-item .nav-link.active {
  font-weight: bold;
  color: #007bff;
}
</style>
