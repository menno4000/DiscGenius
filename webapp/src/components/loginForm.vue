<template>
  <div>
    <form>
      <div class="container px-lg-5">
        <h2>Login</h2>
        <div class="form-group">
          <input
              type="email"
              class="form-control"
              id="inputMail"
              aria-describedby="emailHelp"
              placeholder="Email"
              v-model="input.email"
          />
        </div>
        <div class="form-group">
          <input type="password" v-model="input.password" class="form-control" id="inputPassword" placeholder="Password" />
        </div>
      </div>
    </form>
    <button id="loginButton" class="btn btn-primary" @click="login">Login</button>
    <button id="logoutButton" class="btn btn-primary" @click="logout">Logout</button>
  </div>
</template>

<script>
import { LOGIN } from "../queries/graphql.js";
import { AUTH_TOKEN, USER } from "../constants/settings.js";

export default {
  name: "loginForm",
  data() {
    return {
      input: {
        email: "",
        password: ""
      }
    }
  },
  methods: {
    login: function() {
      this.$apollo
          .mutate({
            mutation: LOGIN,
            variables: {
              email: this.input.email,
              password: this.input.password
            }
          })
          .then((data) => {
            localStorage.setItem(AUTH_TOKEN, data.data.login.token);
            localStorage.setItem(USER, data.data.login.user);
            this.$emit("successfulLogin")
          }).catch(error => {
        alert(error);
      });
    },
    logout: function () {
      localStorage.removeItem(AUTH_TOKEN);
      localStorage.removeItem(USER);
      this.$emit("successfulLogout")

    }
  }
};
</script>

<style scoped>
</style>
