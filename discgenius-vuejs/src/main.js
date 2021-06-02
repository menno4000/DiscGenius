import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import VueEllipseProgress from 'vue-ellipse-progress'
import vuetify from './plugins/vuetify'

Vue.config.productionTip = false
Vue.use(VueEllipseProgress);

new Vue({
  router,
  store,
  vuetify,
  render: function (h) { return h(App) }
}).$mount('#app')
