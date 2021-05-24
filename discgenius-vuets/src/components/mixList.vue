<template>
  <div class="spacer"/>
  <div v-for="mix in mixes" :key="mix.id">
    <div class="songDiv">
      <div class="mixNameLabel">{{mix.name}}</div>
      <div class="mixNumSongsLabel">{{mix.numSongs}}</div>
      <div class="mixLengthLabel">{{mix.length}}</div>
      <div class="mixTempoLabel">{{mix.tempo}}</div>
      <button class="deleteButton">
        Delete
      </button>
    </div>
    <div class="spacer"/>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import {Mix} from "@/model/mix";

@Options({
  props: {
    mixes: [Mix]
  }
})

export default class MixList extends Vue{
  mixes!: [Mix]
}
</script>

<style scoped>
.spacer {
  width: 100%;
  height: 40px;
}
.songDiv{
  width: 100%;
  margin-bottom: 20px;
}
.mixNameLabel{
  float: left;
  text-align: left;
  margin-left: 10%;
  width: 30%;
}
.mixTempoLabel{
  float: left;
  text-align: left;
  width: 5%;
  margin-left: 5%;
}
.mixLengthLabel{
  float: left;
  text-align: left;
  width: 5%;
  margin-left: 5%;
}
.mixNumSongsLabel{
  float: left;
  text-align: left;
  width: 5%;
  margin-left: 5%;
}
.deleteButton{
  float:right;
  margin-right: 15%;
  align-self: center;
}
</style>