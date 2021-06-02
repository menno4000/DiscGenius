<template>
  <div>
    <div class="spacer"/>
    <div>
      <button class="uploadButton" v-on:click="uploadSong()">
        Upload New Song
      </button>
    </div>
    <div v-for="song in songs" :key="song.id">
      <div class="songDiv">
        <div class="songNameLabel">{{song.title}}</div>
        <div class="songLengthLabel">{{song.length}}</div>
        <div class="songTempoLabel">{{song.tempo}}</div>
        <button class="deleteButton" v-on:click="deleteSong(song)">
          Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script >
import Song from "../model/Song";

export default {
  computed: {
    songs(){
      return this.$store.state.songs;
    }
  },
  methods: {
    deleteSong(song){

    },
    uploadSong(song){

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
.uploadButton{
  margin: 20px;
  font-size: 16px;
  background-color: #76b900;
  border-radius: 4px;
  color: white;
  padding: 10px 20px;
}
</style>