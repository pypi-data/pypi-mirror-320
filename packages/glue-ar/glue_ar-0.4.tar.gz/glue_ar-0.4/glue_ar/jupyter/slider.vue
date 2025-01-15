<template>
  <v-slider
    v-model="value"
    :min="min"
    :max="max"
    :step="step"
  >
    <template v-slot:append>
      <v-tooltip :disabled="!doc_text">
        <template v-slot:activator="{ props }">
          <v-icon
            v-bind="props"
            :src="icon_src"
          >
          </v-icon>
        </template>
        {{ doc_text }}
      </v-tooltip>
    </template>
  </v-slider>
</template>
