<template>
    <div>
      <h2>Your Trainer</h2>

      <div v-if="trainerData">
        <img v-if="trainerData.profile_picture_url" :src="trainerData.profile_picture_url" alt="Trainer Picture" class="profile-img" />
        <p><strong>Name:</strong> {{ trainerData.first_name }} {{ trainerData.last_name }}</p>
        <p><strong>Email:</strong> {{ trainerData.email }}</p>
        <p><strong>Bio:</strong> {{ trainerData.bio || "No bio available" }}</p>
      </div>

      <div v-else>
        <p>No trainer assigned.</p>
      </div>

    </div>
</template>
  
<script>
export default {
  name: "TrainerInfo",
  props: {
    trainerData: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped>
.profile-img {
  max-width: 150px;
  border-radius: 50%;
}
</style>
  