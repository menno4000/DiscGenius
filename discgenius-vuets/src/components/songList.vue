<template>
  <div class="spacer"/>
  <div v-for="song in songs" :key="song.id">
    <div class="songDiv">
      <div class="songNameLabel">{{song.name}}</div>
      <div class="songLengthLabel">{{song.length}}</div>
      <div class="songTempoLabel">{{song.tempo}}</div>
      <button class="deleteButton">
        Delete
      </button>
    </div>
    <div class="spacer"/>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import {Song} from "@/model/song";

@Options({
  props: {
    songs: [Song]
  }
})

export default class SongList extends Vue{
  songs!: [Song];
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
.songNameLabel{
  display: inline-block;
  vertical-align: middle;
  text-align: left;
  margin-left: 10%;
  width: 30%;
}
.songTempoLabel{
  display: inline-block;
  vertical-align: middle;
  text-align: left;
  width: 5%;
  margin-left: 5%;
}
.songLengthLabel{
  display: inline-block;
  vertical-align: middle;
  text-align: left;
  width: 5%;
  margin-left: 5%;
}
.deleteButton{
  display: inline-block;
  vertical-align: middle;
  align-self: center;
  color: white;
  font-size: 16px;
  background-color: #ff5d44;
  margin: 20px;
  padding: 15px 30px;
  border-radius: 4px;
}
</style>