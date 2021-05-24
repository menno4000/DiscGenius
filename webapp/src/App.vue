<template>
  <div id="app">
    <h1>DiscGenius Webapp</h1>
    <hr/>
    <loginForm @successfulLogin="successfulLogin" @successfulLogout="successfulLogout"></loginForm>
    <!-- <hr>
    <register-form></register-form>-->
    <hr/>
    <h5>{{ infoMessage }}</h5>
    <hr/>
    <todoList @changePage="changePageApp" :mixes="mixes" v-if="loggedIn"/>
  </div>
</template>

<script>
import todoList from "./components/todoList.vue";
import loginForm from "./components/loginForm.vue";
import {ALL_TODOS_QUERY} from "./queries/graphql.js";
import {USER, AUTH_TOKEN} from "./constants/settings";

export default {
  name: "app",
  data: function () {
    return {
      mixes: [],
      loggedIn: false,
      infoMessage: "You are not logged in.",
      pageSize: 5
    }
  },
  components: {
    mixList,
    loginForm,

  },
  methods: {
    successfulLogin: function () {
      this.loggedIn = true;
      this.infoMessage = `You are logged in as '${localStorage.getItem(USER)}'`;
      this.mixes = [];
      //query mixes
    },
    successfulLogout: function () {
      this.loggedIn = false;
      this.infoMessage = "You are not logged in."
    },
    changePageApp: function (newPage) {
      //query mixes
    },
  },
  beforeMount() {
    localStorage.removeItem(AUTH_TOKEN);
    localStorage.removeItem(USER);
  }
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
