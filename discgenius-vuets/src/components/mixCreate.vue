<template>
  <div class="spacer"/>
  <section id="songSelect">
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
  </section>
  <section id="previewSelect" v-if="songsSelected">
    <div>
      <div class="one">
        <button class="scenarioButton"
                v-on:click="selectScenario('EQ_1.0')">
          <img class="scenarioPreview" src="@/assets/EQ_01.png"/>
        </button>
      </div>
      <div class="two">
        <button class="scenarioButton"
                v-on:click="selectScenario('EQ_2.0')">
          <img class="scenarioPreview" src="@/assets/EQ_02.png"/>
        </button>
      </div>
    </div>
    <div>
      <div class="one">
        <button class="scenarioButton"
                v-on:click="selectScenario('VFF_1.0')">
          <img class="scenarioPreview" src="@/assets/VFF_cut.png"/>
        </button>
      </div>
      <div class="two">
        <button class="scenarioButton"
                v-on:click="selectScenario('VFF_1.1')">
          <img class="scenarioPreview" src="@/assets/VFF_nocut.png"/>
        </button>
      </div>
    </div>
  </section>
  <section id="mixNameAndSend" v-if="previewSelected">
    <div>
      <input v-model="mixName" placeholder="Mix Name"/>
    </div>
  </section>
</template>

<script lang="ts">
import {Options, Vue} from 'vue-class-component';
import {Song} from '../model/song';
import {Mix} from '../model/mix';

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
  height: 20px;
}
.audioSelect {
  margin: 10px;
}
.one {
  float: left;
  margin-left: 10%;
  width: 25%;
}
.two {
  float: right;
  margin-right: 10%;
  width: 25%;
}
.songInfo {
  width: 100px;
  text-align: center;
  margin-left: 5px;
  margin-right: 5px;
}
.scenarioButton {
  width: 100%;
  height: 200px;
  margin: 10px;
}
.scenarioPreview {
  height: 100%;
  align-content: center;
}
.mixNameInput{
  width: 30%;
}
</style>