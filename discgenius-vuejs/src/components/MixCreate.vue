<template>
  <div>
    <div class="spacer"/>
    <div id="songSelect">
      <label class="stepDescription">1. Select Songs for the new Mix</label>
      <div>
        <select v-model="selected1" @change="selectFirstSong" class="audioSelect">
          <option v-for="song in songs"
                  :key="song.id"
                  :value="song">{{ song.title }}
          </option>
          <option v-for="mix in mixes"
                  :key="mix.id"
                  :value="mix">{{ mix.title }}
          </option>
        </select>
        <label class="songInfo">tempo: {{ tempo1 }}</label>
        <label class="songInfo">length: {{ length1 }}</label>
      </div>
      <div v-if="length1 > 0">
        <v-slider v-model="exitPoint"
                  max="100"
                  min="0"
                  hint="Exit Point"
                  class="entryPointSlider"/>
        <label class="entryPointLabel">
          {{convertExitPoint}}
        </label>
      </div>
      <div>
        <select v-model="selected2" @change="selectSecondSong" class="audioSelect">
          <option v-for="song in songs"
                  :key="song.id"
                  :value="song">{{ song.title }}
          </option>
          <option v-for="mix in mixes"
                  :key="mix.id"
                  :value="mix">{{ mix.title }}
          </option>
        </select>
        <label class="songInfo">tempo: {{ tempo2 }}</label>
        <label class="songInfo">length: {{ length2 }}</label>
      </div>
      <div v-if="length2 > 0">
        <v-slider v-model="entryPoint"
                  max="100"
                  min="0"
                  hint="Entry Point"
                  class="entryPointSlider"/>
        <label class="entryPointLabel">
          {{convertEntryPoint}}
        </label>
      </div>
      <div>
        <label class="tempoOverrideLabel">Override Mix Tempo?</label>
        <input type="checkbox" class="tempoOverrideCheck" v-model="tempoOverride"/>
        <input class="tempoOverrideInput" v-model="customTempo" placeholder="120.0" :disabled="tempoOverride === false"/>
      </div>
    </div>
    <div id="previewSelect" v-if="songsSelected">
      <label class="stepDescription">2. Select a Mix Scenario</label>
      <div>
        <img class="legend" src="@/assets/legend.png"/>
      </div>
      <div>
        <div class="scenarioBlock">
          <button class="scenarioButton"
                  v-on:click="selectScenario('EQ_1.0')">
            <img class="scenarioPreview" src="@/assets/EQ_01.png"/>
          </button>
          <div>
            <label>Three-Band-EQ 1</label>
          </div>
        </div>
        <div class="scenarioBlock">
          <button class="scenarioButton"
                  v-on:click="selectScenario('EQ_2.0')">
            <img class="scenarioPreview" src="@/assets/EQ_02.png"/>
          </button>
          <div>
            <label>Three-Band-EQ 2 (Bass Cut)</label>
          </div>
        </div>
      </div>
      <div>
        <div class="scenarioBlock">
          <button class="scenarioButton"
                  v-on:click="selectScenario('VFF_1.0')">
            <img class="scenarioPreview" src="@/assets/VFF_nocut.png"/>
          </button>
          <div>
            <label>Volumetric Fade 1</label>
          </div>
        </div>
        <div class="scenarioBlock">
          <button class="scenarioButton"
                  v-on:click="selectScenario('VFF_1.1')">
            <img class="scenarioPreview" src="@/assets/VFF_cut.png"/>
          </button>
          <div>
            <label>Volumetric Fade 2 (Bass Cut)</label>
          </div>
        </div>
      </div>
    </div>
    <div id="mixNameAndSend" v-if="previewSelected">
      <label class="stepDescription">3. Name the Mix, Hit Submit and Download when it's ready</label>
      <div class="flexContainer">
        <div class="mixSubmit">
          <input class="mixNameInput" v-model="mixName" placeholder="Mix Name"/>
        </div>
        <div class="mixSubmit">
          <button class="submitButton"
                  :disabled="mixName===''"
                  v-on:click="submit">Submit</button>
        </div>
        <div v-if="submitted" class="mixProgress">
          <vue-ellipse-progress :progress="calcedProgress"
                                :legend-value="progress"
                                :size="100"
                                color="#76b900">

          </vue-ellipse-progress>
        </div>
        <span>{{submitted}}</span>
        <span>{{progress}}</span>
        <div v-if="submitted" class="mixDownload">
          <button class="downloadButton"
                  :disabled="progress < 100">Download</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Song from '../model/Song'
import Mix from '../model/Mix'
import {v4 as uuidv4} from 'uuid'

export default{
  data(){
    return {
      selected1 : new Song("stub", 0.0, 0.0, "0"),
      tempo1 : 0.0,
      length1 : 0.0,
      selected2 : new Song("stub", 0.0, 0.0, "0"),
      tempo2 : 0.0,
      length2 : 0.0,
      yeOldeStub : "",
      numTracksSelected : 0,
      songsSelected : false,
      previewSelected : false,
      scenario : "",
      mixName : "",
      submitted : false,
      tempoOverride: false,
      customTempo: 120.0,
      entryPoint: 30.0,
      exitPoint: 70.0
    }
  },
  computed: {
    convertExitPoint(){
      return (this.exitPoint / 100)
    },
    convertEntryPoint(){
      return (this.entryPoint / 100)
    },
    calcedProgress() {
      return this.progress;
    },
    mixNumSongs(){
      let numSongs1 = 1;
      let numSongs2 = 1;
      if(this.selected1 instanceof Mix){
        numSongs1 = this.selected1.numSongs;
      }
      if(this.selected2 instanceof Mix){
        numSongs2 = this.selected2.numSongs;
      }
      return numSongs1+numSongs2;
    },
    mixTempo(){
      if(this.tempoOverride){
        return this.customTempo;
      }else{
        return this.tempo1;
      }
    },
    newMixLength(){
      let adjustedSong2Length = (this.tempo1 / this.tempo2) * this.length2;
      return this.length1 + adjustedSong2Length;
    },
    newMix(){
      new Mix(this.mixName, this.newMixLength(), this.mixNumSongs(), this.mixTempo(), uuidv4())
    }
  },
  props: {
    songs:{
      type: [Song]
    },
    mixes:{
      type: [Mix]
    }
  },
  watch: {
    progress: {
      handler: 'updateProgress'
    }
  },
  methods: {
    selectFirstSong() {
      this.tempo1 = this.selected1.tempo
      this.length1 = this.selected1.length
      this.numTracksSelected += 1;
      this.checkSongSelection();
    },
    selectSecondSong() {
    this.tempo2 = this.selected2.tempo
    this.length2 = this.selected2.length
    this.numTracksSelected += 1;
    this.checkSongSelection();
    },
    checkSongSelection() {
      if (this.numTracksSelected === 2) {
        this.songsSelected = true;
      }
    },
    selectScenario(pName) {
      this.scenario = pName;
      this.previewSelected = true;
    },
    submit() {
      this.submitted = true;
      function progressLoop (){
        setTimeout(function (){
          this.progress ++;
          if(this.progress < 100){
            progressLoop();
          }
        }, 100)
      }
      progressLoop();
    },
    updateProgress(newState) {
      this.progress = newState
    }
  }

}
</script>

<style scoped>
.spacer {
  width: 100%;
  height: 30px;
}
.stepDescription{
  margin-top: 10px;
  margin-bottom: 10px;
}
.audioSelect {
  margin: 10px;
}
.entryPointSlider{
  display: inline-block;
  vertical-align: middle;
  width: 200px;
}
.entryPointLabel{
  display: inline-block;
  vertical-align: middle;
  width: 40px;
  text-align: center;
}
.tempoOverrideCheck{
  display: inline-block;
  vertical-align: middle;
  width: 40px;
  text-align: center;
}
.tempoOverrideCheck{
  display: inline-block;
  vertical-align: middle;
}
.tempoOverrideInput{
  display: inline-block;
  vertical-align: middle;
  text-align: center;
  width: 35px;
}
.songInfo {
  width: 100px;
  text-align: center;
  margin-left: 5px;
  margin-right: 5px;
}
.scenarioBlock{
  display: inline-block;
  height: 25%;
  width: 25%;
  margin: 10px;
}
.legend{
  width: 140px;
  height: 140px;
}
.scenarioButton {
  background-color: white;
  width: 100%;
  margin: 10px;
}
.scenarioPreview {
  height: 100%;
  width: 100%;
  align-content: center;
}
.mixNameInput{
  align-content: center;
  flex-basis: 100px;
}
.mixSubmit{
  margin: 10px;
  display: inline-block;
  vertical-align: middle;
}
.submitButton{
  color: white;
  font-size: 16px;
  background-color: #00b9ff;
  margin: 20px;
  padding: 15px 30px;
  border-radius: 4px;
}
.submitButton:disabled{
  color: white;
  font-size: 16px;
  background-color: grey;
  margin: 20px;
  padding: 10px 20px;
  border-radius: 4px;
}
.mixProgress{
  display: inline-block;
  vertical-align: middle;
}
.mixDownload{
  margin: 10px;
  display: inline-block;
  vertical-align: middle;
}
.downloadButton{
  color: white;
  font-size: 16px;
  background-color: #00b9ff;
  margin: 20px;
  padding: 15px 30px;
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
</style>