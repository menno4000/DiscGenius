<template>
  <div class="loginDiv" v-if="!authState">
    <button class="loginButton" v-on:click="doLogin">Login</button>
  </div>
  <div class="loginDiv" v-if="authState">
    <label class="loginLabel">
      Logged in as {{username}}
    </label>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    username: String
  }
})

export default class LoginState extends Vue{
  authState!: boolean;
  username!: string;

  doLogin():void {
    this.authState = true;
    this.$emit('login', true);
  }
}
</script>

<style scoped>

.loginDiv{
  text-align: center;
  align-content: center;
}
.loginButton{
  margin: 20px;
}
.loginLabel{
  margin: 20px;
  align-content: center;
  align-self: center;
}

</style>