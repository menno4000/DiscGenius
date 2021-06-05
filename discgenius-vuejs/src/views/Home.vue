<template>
  <div>
    <LogoHeader/>
    <section class="flexContainer">
      <div class="one">
        <Navigate v-on:switch="switchViewState($event)"/>
      </div>
      <div class="two">
        <LoginState/>
      </div>
    </section>
    <section>
      <div v-if="viewState===0">
        <FrontPage ref="frontPage"/>
      </div>
      <div v-if="viewState===1">
        <MixCreate/>
      </div>
      <div v-if="viewState===2">
        <MixList/>
      </div>
      <div v-if="viewState===3">
        <SongList/>
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



export default {
  data() {
    return {
      viewState: 0,
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
    switchViewState(newState) {
      this.viewState = newState;
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
