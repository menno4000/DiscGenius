<template>
  <div>
    <div class="spacer"/>
    <div v-for="song in songs" :key="song.id">
      <div class="songDiv">
        <div class="songNameLabel">{{song.title}}</div>
        <div class="songLengthLabel">{{song.length}}</div>
        <div class="songTempoLabel">{{song.tempo}}</div>
        <button class="deleteButton">
          Delete
        </button>
      </div>
      <div class="spacer"/>
    </div>
  </div>
</template>

<script >
import Song from "../model/Song";

export default {
  props: {
    songs: {
      type: [Song]
    }
  }
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
  padding: 10px 20px;
  border-radius: 4px;
}
</style>