<template>
  <div class="spacer"/>
  <div v-for="mix in mixes" :key="mix.id">
    <div class="songDiv">
      <div class="mixNameLabel">{{mix.name}}</div>
      <div class="mixNumSongsLabel">{{mix.numSongs}}</div>
      <div class="mixLengthLabel">{{mix.length}}</div>
      <div class="mixTempoLabel">{{mix.tempo}}</div>
      <button class="downloadButton">
        Download
      </button>
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
  height: 20px;
}
.songDiv{
  width: 100%;
  margin-bottom: 20px;
}
.mixNameLabel{
  display: inline-block;
  vertical-align: middle;
  margin-left: 10%;
  width: 25%;
}
.mixTempoLabel{
  display: inline-block;
  vertical-align: middle;
  width: 5%;
  margin-left: 10px;
}
.mixLengthLabel{
  display: inline-block;
  vertical-align: middle;
  width: 5%;
  margin-left: 10px;
}
.mixNumSongsLabel{
  display: inline-block;
  vertical-align: middle;
  text-align: left;
  width: 5%;
  margin-left: 10px;
}
.downloadButton{
  display: inline-block;
  vertical-align: middle;
  color: white;
  font-size: 16px;
  background-color: #00b9ff;
  margin: 20px;
  padding: 10px 20px;
  border-radius: 4px;
}
.deleteButton{
  display: inline-block;
  vertical-align: middle;
  align-self: center;
  color: white;
  font-size: 16px;
  background-color: #ff5d44;
  margin: 20px;
  padding: 10px 20px;
  border-radius: 4px;
}
</style>