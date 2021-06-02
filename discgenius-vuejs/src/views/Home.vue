<template>
  <div>
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
  </div>
</template>

<script lang="ts">
import LogoHeader from '../components/LogoHeader.vue';
import Navigate from '../components/Navigate.vue';
import LoginState from "../components/LoginState.vue";
import FrontPage from "../components/FrontPage.vue";
import MixCreate from "../components/MixCreate.vue";
import SongList from "../components/SongList.vue";
import MixList from "../components/MixList.vue";
import Song from '../model/Song';
import Mix from '../model/Mix';

let username_stub = "Test User";

let songs_stub = [
  new Song("Song 1", 361, 130, "s1"),
  new Song("Song 2", 382, 134, "s2"),
  new Song("Song 3", 304, 127, "s3"),
];
let mixes_stub = [
  new Mix("Mix 1", 702, 2, 130, "m1", 100),
  new Mix("Mix 2", 1240, 3, 120, "m2", 55),
];

export default{
  data () {
    return {
      viewState: 0,
      songs: songs_stub,
      mixes: mixes_stub,
      username: username_stub,
      authState: false,
    }
  },
  components: {
    LogoHeader,
    Navigate,
    LoginState,
    FrontPage,
    MixCreate,
    SongList,
    MixList
  },
  methods: {
    doLogin(newState) {
      this.authState = newState
    },
    switchViewState(newState) {
      this.viewState = newState
    }
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
