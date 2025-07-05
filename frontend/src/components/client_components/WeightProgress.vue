<template>
  <div class="container">
    <h2>Weight Progress</h2>

    <div v-if="loading">Loading...</div>

    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <!-- Weight graph component -->
    <canvas ref="weightChart"></canvas>
  </div>
</template>

<script>
import { nextTick } from "vue";
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: "WeightProgress",
  data() {
    return {
      weightProgress: [],
      loading: true,
      errorMessage: "",
      chart: null,
    };
  },

  props: {
    clientId: {
      type: Number,
      default: null 
    }
  },

  async mounted() {
    await this.fetchWeightProgress();
  },

  methods: {
    async fetchWeightProgress() {
      this.loading = true;
      this.errorMessage = "";

      //Url changes depending on whether there is a clientID (logged in as trainer) or not (logged in as client)
      const endpoint = this.clientId
        ? `http://127.0.0.1:8000/api/getClientWeightProgress/${this.clientId}/`
        : `http://127.0.0.1:8000/api/getWeightProgress`;

      //Hits the respective endpoint
      try {
        const response = await fetch(endpoint, {
          credentials: "include"
        });

        const data = await response.json();

        if (response.ok) {
          this.weightProgress = data.weight_progress;

          if (this.weightProgress.length > 0) {
            //Wait for DOM to be loaded before rendering chart
            await nextTick();
            this.renderChart();
          } 
          else {
            this.errorMessage = "No weight data available.";
          }
        } 
        else {
          this.errorMessage = data.error || "Failed to fetch weight progress.";
        }
      } 
      catch (error) {
        this.errorMessage = "Failed to reach backend";
      } 
      finally {
        this.loading = false;
      }
    },

    renderChart() {
      if (!this.$refs.weightChart) {
        console.error("Chart element not found!");
        return;
      }

      if (this.chart) {
        this.chart.destroy();
      }

      //Gets the required context from Chart.js to draw a 2D chart
      const ctx = this.$refs.weightChart.getContext("2d");

      //Creates a new chart with the 2d context
      this.chart = new Chart(ctx, {
        //Specifies that we are creating a line chart
        type: "line",

        data: {
          //Array of x axis labels, in this case the dates
          labels: this.weightProgress.map(entry => entry.date),

          //Specifies datasets, each dataset represents a line on the graph
          //For purposes of this application, only one dataset is used (client's weight-date data)
          datasets: [
            {
              label: "Weight Progress",
              //Data consists of the y axis values
              data: this.weightProgress.map(entry => entry.weight),

              //Styling for the chart
              borderColor: "#3498db",
              backgroundColor: "rgba(52, 152, 219, 0.2)",
              borderWidth: 2,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });

      console.log("Chart rendered successfully!");
    },
  },
};
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 600px;
  margin: auto;
  text-align: center;
}

.error {
  color: red;
  margin-top: 10px;
}

canvas {
  width: 100% !important;
  height: 300px !important;
}
</style>
