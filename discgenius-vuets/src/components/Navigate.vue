<template>
  <button class='navButton' v-on:click="$emit('switch', 1)">Create Mix</button>
  <button class='navButton' v-on:click="$emit('switch', 2)">Mix List</button>
  <button class='navButton' v-on:click="$emit('switch', 3)">Song List</button>
</template>

<script lang="ts">
import { Vue } from 'vue-class-component';


export default class Navigate extends Vue{

}
</script>

<style scoped>
.navButton {
  margin: 20px;
}
</style>