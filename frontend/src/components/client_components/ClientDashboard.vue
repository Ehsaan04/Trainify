<template>
  <ClientNavbarNew :userData="userData" />
</template>

<script>
import ClientNavbarNew from './ClientNavbarNew.vue';

export default {
  name: "ClientDashboard",
  components: {
    ClientNavbarNew
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
  h1 {
    font-size: 1.8rem;
    color: #333;
  }
  
  ul {
    list-style-type: none;
    padding: 0;
  }
  
  li {
    margin: 0.5rem 0;
  }
  
  img {
    display: block;
    margin-top: 1rem;
  }
</style>
  