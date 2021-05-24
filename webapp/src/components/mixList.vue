<template>
  <div id="mixList">
    <div class="container px-lg-5">
      <div id="listHeader" class="row mx-lg-n5 jest-list-item">
        <div id="mixTextHeaderDiv" class="col py-md-3 border bg-light">
          <p>Todo</p>
        </div>
        <div id="belongingHeaderDiv" class="col-2 py-md-3 border bg-light">
          <p>belongsTo</p>
        </div>
        <div id="createdAtHeaderDiv" class="col-2 py-md-3 border bg-light">
          <p>createdAt</p>
        </div>
        <div id="modifiedAtHeaderDiv" class="col-2 py-md-3 border bg-light">
          <p>modifiedAt</p>
        </div>
        <div id="buttonsHeaderDiv" class="col-2 py-md-3 border bg-light">
          <p></p>
        </div>
      </div>
      <todo
          @deleteMix="deleteMix"
          @toggleEditMode="toggleEditMode"
          v-for="mix in mixes"
          :mix="mix"
          :key="mix.id"
      ></todo>
      <div>
        <div class="row mx-lg-n5 jest-list-item">
          <div class="col py-3 border bg-light">
            <label size="6" class="infoLabel">Add ToDo:</label>
            <button id="buttonAdd" class="btn btn-success" type="button" @click="createMix">Add</button>
          </div>
          <div class="col py-3 border bg-light">
            <label size="8" class="infoLabel">Pagination:</label>
            <button id="previousPageButton" class="btn btn-success" type="button" @click="previousPage">prev
            </button>
            <label id="pageField" size="4">{{page}}</label>
            <button id="nextPageButton" class="btn btn-success" type="button" @click="nextPage">next</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import mix from "./mix.vue";
import {DELETE_TODO, CREATE_TODO, UPDATE_TODO} from "../queries/graphql.js";
import {USER} from "../constants/settings";

export default {
  name: "mixList",
  data: function () {
    return {
      page: 0,
    }
  },
  props: {
    mixes: Array,
  },
  components: {
    mix
  },
  methods: {
    createMix: function () {
      // TODO switch to create mix page
    },
    deleteMix: function (id) {
      // TODO ask for confirmation, as file is large
      // TODO if confirmation is given, remove mix from list and database
    },
    toggleEditMode: function (entry) {
      if (entry.editMode) {
        // TODO rename mix in database
      }

      this.mixes.forEach(i => {
        if (i.id === entry.id) i.editMode = !i.editMode;
      });
    },
    previousPage: function () {
      if (this.page > 0) {
        this.page -= 1;
        this.$emit('changePage', this.page);
      }

    },
    nextPage: function () {
      this.page += 1;
      this.$emit('changePage', this.page)
    },
  }
};
</script>

<style scoped>
.btn-success {
  margin-right: 30px;
  margin-left: 30px;
}
.infoLabel {
  margin-left: 30px;
}
#listHeader {
  font-size: 120%;
  margin: auto
}
</style>
