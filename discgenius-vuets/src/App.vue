<template>
  <LogoHeader/>
  <section class="flexContainer">
    <div class="one">
      <Navigate v-on:switch="switchViewState($event)"/>
    </div>
    <div class="two">
      <LoginState :authState="authState"
                  :username="username"
                  v-on:login="doLogin($event)"/>
    </div>
  </section>
  <section>
    <div v-if="viewState===0">
      <FrontPage ref="frontPage"/>
    </div>
    <div v-if="viewState===1">
      <MixCreate :songs="songs"
                 :mixes="mixes"/>
    </div>
    <div v-if="viewState===2">
      <MixList :mixes="mixes"/>
    </div>
    <div v-if="viewState===3">
      <SongList :songs="songs"/>
    </div>
  </section>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import LogoHeader from '@/components/LogoHeader.vue';
import Navigate from '@/components/Navigate.vue';
import LoginState from "@/components/LoginState.vue";
import FrontPage from "@/components/FrontPage.vue";
import MixCreate from "@/components/MixCreate.vue";
import SongList from "@/components/SongList.vue";
import MixList from "@/components/MixList.vue";
import { Song } from './model/song';
import { Mix } from './model/mix';

let username_stub = "Test User";

let songs_stub = [
  new Song("Song 1", 361, 130, "s1"),
  new Song("Song 2", 382, 134, "s2"),
  new Song("Song 3", 304, 127, "s3"),
];
let mixes_stub = [
  new Mix("Mix 1", 702, 2, 130, "m1"),
  new Mix("Mix 2", 1240, 3, 120, "m2"),
];

@Options({
  components: {
    LogoHeader,
    Navigate,
    LoginState,
    FrontPage,
    MixCreate,
    SongList,
    MixList
  },
})

export default class App extends Vue {
  viewState = 0;
  songs = songs_stub;
  mixes = mixes_stub;
  username = username_stub;
  authState = false;

  doLogin(newState: boolean):void {
    this.authState = newState
  }
  switchViewState(newState: number):void {
    this.viewState = newState
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.one {
  align-content: center;
  display: inline-block;
  vertical-align: middle;
}
.two {
  align-content: center;
  display: inline-block;
  vertical-align: middle;
}


</style>
