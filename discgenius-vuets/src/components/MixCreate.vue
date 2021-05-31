<template>
  <div class="spacer"/>
  <div id="songSelect">
    <label class="stepDescription">1. Select Songs for the new Mix</label>
    <div>
      <select v-model="selected1" @change="selectFirstSong" class="audioSelect">
        <option v-for="song in songs"
                :key="song.id"
                :value="song">{{ song.name }}
        </option>
        <option v-for="mix in mixes"
                :key="mix.id"
                :value="mix">{{ mix.name }}
        </option>
      </select>
      <label class="songInfo">tempo: {{ tempo1 }}</label>
      <label class="songInfo">length: {{ length1 }}</label>
    </div>
    <div>
      <select v-model="selected2" @change="selectSecondSong" class="audioSelect">
        <option v-for="song in songs"
                :key="song.id"
                :value="song">{{ song.name }}
        </option>
        <option v-for="mix in mixes"
                :key="mix.id"
                :value="mix">{{ mix.name }}
        </option>
      </select>
      <label class="songInfo">tempo: {{ tempo2 }}</label>
      <label class="songInfo">length: {{ length2 }}</label>
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
        <button class="submitButton" :disabled="mixName===''">Submit</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import {Song} from '@/model/song';
import {Mix} from '@/model/mix';

@Options({
  props: {
    songs: [Song],
    mixes: [Mix]
  }
})

export default class MixCreate extends Vue {
  selected1 = new Song("stub", 0, 0, "0");
  tempo1 = 0;
  length1 = 0;
  selected2 = new Song("stub", 0, 0, "0");
  tempo2 = 0;
  length2 = 0;
  yeOldeStub = "";
  numSongsSelected = 0;
  songsSelected = false;
  previewSelected = false;
  scenario = "";
  mixName = "";
  songs!: [Song];
  mixes!: [Mix];


  selectFirstSong(): void {
    this.tempo1 = this.selected1.tempo
    this.length1 = this.selected1.length
    this.numSongsSelected += 1;
    this.checkSongSelection();
  }

  selectSecondSong(): void {
    this.tempo2 = this.selected2.tempo
    this.length2 = this.selected2.length
    this.numSongsSelected += 1;
    this.checkSongSelection();
  }

  checkSongSelection(): void {
    if (this.numSongsSelected == 2) {
      this.songsSelected = true;
    }
  }

  selectScenario(pName: string): void {
    this.scenario = pName
    this.previewSelected = true;
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
</style>