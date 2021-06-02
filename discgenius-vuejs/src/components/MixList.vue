<template>
  <div>
    <div class="spacer"/>
    <div v-for="mix in mixesWithProgress" :key="mix.mix.id">
      <div class="songDiv">
        <div class="mixNameLabel">{{mix.mix.title}}</div>
        <div class="mixNumSongsLabel">{{mix.mix.numSongs}}</div>
        <div class="mixLengthLabel">{{mix.mix.length}}</div>
        <div class="mixTempoLabel">{{mix.mix.tempo}}</div>
        <vue-ellipse-progress :progress="mix.progress"
                              :legend="true"
                              :legend-value="mix.progress"
                              :size="50"
                              color="#76b900"
                              class="mixProgress"
        >
        </vue-ellipse-progress>
        <button class="downloadButton" :disabled="mix.progress < 100">
          Download
        </button>
        <button class="deleteButton">
          Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Mix from "@/model/Mix";

export default{
  computed: {
    mixes(){
      return this.$store.getters.getMixes;
    },
    mixesWithProgress() {
      const mixesWithProg = []
      for (let i = 0, len = this.mixes.length; i < len; i++){
        mixesWithProg.push({
          mix: this.mixes[i],
          progress: this.mixes[i].progress
        })
      }
      return mixesWithProg
    }
  },
  // created() {
  //   this.$store.dispatch('fetchMixes');
  // },
  // mounted() {
  //
  // }
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
  text-align: left;
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
.mixProgress{
  display: inline-block;
  vertical-align: middle;
  margin-left: 20px;
  margin-right: 20px;
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
.downloadButton:disabled{
  color: white;
  font-size: 16px;
  background-color: grey;
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