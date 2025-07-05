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
            <li class="nav-item" :class="{ active: activeView === 'clientRequests' }" @click="activeView = 'clientRequests'">
              <a class="nav-link" href="javascript:void(0)">Client Requests</a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'manageClients' }" @click="activeView = 'manageClients'">
              <a class="nav-link" href="javascript:void(0)">Manage Clients</a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'leaderboard' }" @click="activeView = 'leaderboard'">
              <a class="nav-link" href="javascript:void(0)">Leaderboard</a>
            </li>

            <li class="nav-item" :class="{ active: activeView === 'trainerProfile' }" @click="activeView = 'trainerProfile'">
              <a class="nav-link" href="javascript:void(0)">Profile</a>
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
      <ClientRequests v-if="activeView === 'clientRequests'" />
      <ManageClients
        v-if="activeView === 'manageClients' && !selectedClient"
        @clientSelected="handleClientSelect"
      />
      <ClientDetail
        v-if="selectedClient"
        :client="selectedClient"
        @close="selectedClient = null"
      />
      <TrainerLeaderboard v-if="activeView === 'leaderboard'" />
      <TrainerProfile v-if="activeView === 'trainerProfile'" :userData="userData" />
    </div>
  </div>
</template>

<script>
import ClientRequests from "./ClientRequests.vue";
import ManageClients from "./ManageClients.vue";
import ClientDetail from "./ClientDetail.vue";
import TrainerProfile from "./TrainerProfile.vue";
import TrainerLeaderboard from "./TrainerLeaderboard.vue";

export default {
  name: "TrainerNavbar",
  components: {
    ClientRequests,
    ManageClients,
    ClientDetail,
    TrainerProfile,
    TrainerLeaderboard
  },

  data() {
    return {
      activeView: "manageClients",
      //Keeps track of currently selected client for ClientDetail.vue to be rendered
      selectedClient: null, 
    };
  },

  methods: {
    //Handles when a client is clicked
    handleClientSelect(client) {
      this.selectedClient = client; 
    },

    logout() {
      window.location.href = "http://127.0.0.1:8000/logout/";
    }
  },
  props: {
    userData: {
      type: Object,
      required: true,
    }
  }
};
</script>

<style scoped>
.navbar-nav .nav-item .nav-link.active {
  font-weight: bold;
  color: #007bff;
}
</style>
