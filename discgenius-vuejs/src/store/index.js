import Vue from 'vue'
import Vuex from 'vuex'
import Song from "@/model/Song";
import Mix from "@/model/Mix";

Vue.use(Vuex)

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
let available_mixes = [mixes_stub[0]]
export default new Vuex.Store({
  state: {
    currentProgress: 0,
    songs: songs_stub,
    mixes: mixes_stub,
    username: username_stub,
    authState: false,
    availableMixes: available_mixes
  },
  mutations: {
    login(state){
      state.authState = true
    },
    logout(state){
      state.authState = false
    },
    incrementProgress(state){
      state.currentProgress++;
    },
    setMixes(state, {current_mixes}){
      state.mixes = current_mixes;
    },
    setAvailableMixes(state, {available_mixes}){
      state.availableMixes = available_mixes;
    },
    addMix(state, mix){
      state.mixes.push(mix);
    },
    addSong(state, song){
      state.songs.push(song);
    },
    deleteMix(state, mix){
      state.mixes.splice(state.mixes.indexOf(mix), 1);
    },
    deleteSong(state, song){
      state.songs.splice(state.songs.indexOf(song), 1);
    }
  },
  actions: {
    submitMix(context, payload){
      const {mix} = payload
      context.commit("addMix", mix)
    },
    deleteMix(context, payload){
      const {mix} = payload
      context.commit("deleteMix", mix)
    },
    fakeProgress(context){
      function fakeProgressLoop(){
        setTimeout(function(){
          context.commit('incrementProgress')
          if(this.state.currentProgress < 100){
            fakeProgressLoop()
          }
        },100)
      }
      fakeProgressLoop();
    }
  },
  modules: {
  },
  getters: {
    getMixes(state){
      return state.mixes
    },
    getAvailableMixes(state){
      return state.availableMixes
    }
  }
})
