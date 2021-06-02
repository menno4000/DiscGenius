<template>
  <div>
    <button class='navButton' v-on:click="$emit('switch', 1)">Create Mix</button>
    <button class='navButton' v-on:click="$emit('switch', 2)">Mix List</button>
    <button class='navButton' v-on:click="$emit('switch', 3)">Song List</button>
  </div>
</template>

<script>
export default {
  'name': 'Navigate'
}
</script>

<style scoped>
.navButton {
  color: white;
  font-size: 16px;
  background-color: #76b900;
  margin: 20px;
  padding: 15px 30px;
  border-radius: 4px;
}
</style>