<template>
  <div>
    <div class="spacer"/>
    <section>
      <h2>
        Welcome to DiscGenius!
      </h2>
      <div class="frontPageDiv">
        DiscGenius is a tool for creating DJ-style music mixes from your Audio Files (.mp3, .wav).
      </div>
      <div class="frontPageDiv">
        You can upload Songs and combine them into Mixes, which you also extend with more songs.
      </div>
      <div class="frontPageDiv">
        DiscGenius will adjust the tempo of the second song of any Mix to the first, but you can also take full control
        and set the tempo of produced mix.
      </div>
      <div class="frontPageDiv">
        Last but not least, DiscGenius offers multiple transition styles for any mix which you can select from at mix
        creation.
      </div>
      <div class="frontPageDiv" v-if="!authState">
        To get started, log in to or create an account and start creating mixes in your user storage (Under Construction).
      </div>
      <div class="frontPageDiv" v-else-if="authState">
        You are logged in! Happy mixing.
      </div>
    </section>
  </div>
</template>

<script>
export default{
  computed:{
    authState(){
      return this.$store.state.authState;
    },
  }
}
</script>
<style scoped>
.frontPageDiv {
  margin-top: 10px;
  margin-bottom: 10px;
  margin-right: 10%;
  margin-left: 10%;
}
.spacer {
  width: 100%;
  height: 50px;
}
</style>