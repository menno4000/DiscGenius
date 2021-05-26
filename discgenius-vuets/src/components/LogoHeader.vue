<template>
  <div id="header">
    <img alt="Logo" src="@/assets/dglogo_htw_tp.png">
    <h1>{{title}}</h1>
    <h4>{{subtitle}}</h4>
  </div>
</template>

<script lang="ts">
import { Vue } from 'vue-class-component';

export default class LogoHeader extends Vue{
  title = "DiscGenius"
  subtitle = "A DJ-Style Song-Mixing Application"
}
</script>

<style scoped>

img{
  max-height: 150px;
  max-height: 150px;
}

</style>