<template>
  <div>
    <b-form inline>
    <b-input-group prepend="Red" class='pr-1'>
        <b-form-select v-model="datavalue.red" :options="light_options"></b-form-select>
    </b-input-group>
    <b-input-group prepend="Yellow" class='pr-1'>
        <b-form-select v-model="datavalue.yellow" :options="light_options"></b-form-select>
    </b-input-group>
    <b-input-group prepend="Green" class='pr-1'>
        <b-form-select v-model="datavalue.green" :options="light_options"></b-form-select>
    </b-input-group>
    <b-input-group prepend="Blue" class='pr-1'>
        <b-form-select v-model="datavalue.blue" :options="light_options"></b-form-select>
    </b-input-group>
    <b-input-group prepend="White">
        <b-form-select v-model="datavalue.white" :options="light_options"></b-form-select>
    </b-input-group>
    </b-form>
  </div>
</template>

<script>

import Base from './Base.vue'

var default_patlite = {red: 'off', yellow: 'off', green: 'off', blue: 'off', white: 'off'}

export default {
  extends: Base,
  name: 'Patlite',
  props: {
    value: {type: Object, default: () => Object.assign({}, default_patlite) },
    options: {type: Object},
  },
  data() {
    return {
      light_options: ['off', 'on', 'blink1', 'blink2'],
      datavalue: this.value,
    }
  },
  watch: {
    datavalue: {
      handler(v) { this.$emit('input', this.datavalue) },
      deep: true,
      immediate: true
    },
  },
}

</script>
