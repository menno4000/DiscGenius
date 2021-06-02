<template>
  <div>
    <div class="loginDiv" v-if="!authState">
      <button class="loginButton" v-on:click="doLogin">Login</button>
    </div>
    <div class="loginDiv" v-else-if="authState">
      <div>
        <label class="loginLabel">Logged in as {{username}}</label>
      </div>
    </div>
  </div>
</template>

<script>

export default{
  props: {
    authState: {
      default: false
    },
    username: {
      default: 'john die'
    }
  },
  methods: {
    doLogin() {
      this.authState = true;
      this.$emit('login')
    }
  }
}
</script>

<style scoped>

.loginDiv{
  text-align: center;
  align-content: center;
}
.loginButton{
  color: white;
  font-size: 16px;
  background-color: #00b9ff;
  margin: 20px;
  padding: 15px 30px;
  border-radius: 4px;
}
.loginLabel{
  margin: 20px;
  align-content: center;
  align-self: center;
}

</style>