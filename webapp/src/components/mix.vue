<template>
  <div class="row mx-lg-n5 jest-list-item">
    <div id="mixTextDiv" class="col py-md-3 border bg-light">
      <form class="text">
        <p id="mixText" v-if="!mix.editMode">{{ mix.text }}</p>
        <input id="mixTextEdited" type="text" v-if="mix.editMode" v-model="mix.text"/>
      </form>
    </div>
    <div id="belongingDiv" class="col-2 py-md-3 border bg-light">
      <form class="text">
        <p id="username" >{{ mix.user.name }}</p>
      </form>
    </div>
    <div id="createdAtDiv" class="col-2 py-md-3 border bg-light">
      <form class="text">
        <p id="createdAt" >{{ mix.createdAt }}</p>
      </form>
    </div>
    <div id="modifiedAtDiv" class="col-2 py-md-3 border bg-light">
      <form class="text">
        <p id="modifiedAt" >{{ mix.modifiedAt }}</p>
      </form>
    </div>
    <div id="editSaveButtonDiv" class="col-1 py-md-3 border bg-light">
      <button
          @click="$emit('toggleEditMode', mix)"
          class="btn btn-primary"
          id="buttonEdit"
          name="edit-button"
          type="button"
          v-if="!mix.editMode"
      >Edit
      </button>
      <button
          @click="$emit('toggleEditMode', mix)"
          class="btn btn-success"
          id="buttonSave"
          name="save-button"
          type="button"
          v-if="mix.editMode"
      >Save
      </button>
    </div>
    <div id="deleteButtonDiv" class="col-1 py-md-3 border bg-light">
      <button
          @click="$emit('deleteMix', mix.id)"
          class="btn btn-danger"
          id="buttonDelete"
          name="delete-button"
          type="button"
      >Delete
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "mix",
  props: {
    mix: Object,
    deleteMix: Function
  },
  data: function () {
    return {counter: 0};
  }
};
</script>

<style>
.text {
  text-align: left;
}
.btn-danger {
  margin: auto;
}
</style>