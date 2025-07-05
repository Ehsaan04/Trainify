<template>
  <div>
    <h2>Client Requests</h2>
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    <div v-else-if="loading" class="text-center">
      <p>Loading client requests...</p>
    </div>
    <div v-else>
      <ul class="list-group">
        <li
          v-for="request in requests"
          :key="request.id"
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          <div>
            <h5>{{ request.client_username }}</h5>
            <p>{{ request.message }}</p>
            <small class="text-muted">Requested on: {{ formatDate(request.created_at) }}</small>
          </div>
          <div>
            <button class="btn btn-success me-2" @click="respondToRequest(request.id, 'approve')" :disabled="request.status === 'approved'">
              Accept
            </button>
            <button class="btn btn-danger" @click="respondToRequest(request.id, 'reject')" :disabled="request.status === 'rejected'">
              Reject
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "ClientRequests",
  data() {
    return {
      requests: [],
      loading: true,
      error: null,
    };
  },
  methods: {
    //Fetches all requests that the trainer has received from clients
    async fetchRequests() {
      try {
        const response = await fetch("http://127.0.0.1:8000/view_requests/", {
          credentials: "include",
        });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to fetch client requests.");
        }
        this.requests = data.requests;
      } 
      catch (error) {
        this.error = error.message;
      } 
      finally {
        this.loading = false;
      }
    },

    //Method to let the backend know whether the trainer accepts or declines the request
    async respondToRequest(requestId, action) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/respond_to_request/${requestId}/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ action }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to process the request.");
        }
        alert(data.success);

      } 
      catch (error) {
        alert(error.message);
      }
    },

    formatDate(dateString) {
      const options = { year: "numeric", month: "short", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
  },

  mounted() {
    this.fetchRequests();
  },
};
</script>

<style scoped>
h2 {
  margin-bottom: 1rem;
}
.list-group-item {
  margin-bottom: 1rem;
  padding: 1rem;
}
</style>
