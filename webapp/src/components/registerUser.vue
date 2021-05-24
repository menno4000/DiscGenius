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
        <div class="form-group">
          <input type="password" v-model="input.password" class="form-control" id="confirmPassword" placeholder="Password" />
        </div>
      </div>
    </form>
    <button id="registerButton" class="btn btn-primary" @click="register">Register</button>
  </div>
</template>

<script>
import { LOGIN } from "../queries/graphql.js";
import { AUTH_TOKEN, USER } from "../constants/settings.js";

export default {
  name: "registerUser",
  data() {
    return {
      input: {
        email: "",
        password: "",
      }
    }
  },
  methods: {
    register: function() {
      // TODO check if passwords match, reject and show error if they dont
      // TODO create user with new details in login form
      // TODO return to login form
    }
  }
};
</script>

<style scoped>
</style>
