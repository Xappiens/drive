<template>
  <div
    class="flex flex-col items-center m-auto gap-4"
    style="transform: translate(0, -88.5px)"
  >
    <div class="flex flex-col items-center gap-2">
      <div v-if="icon">
        <component
          :is="icon"
          class="size-10 text-ink-gray-5"
        />
      </div>
      <p class="text-base text-ink-gray-6 font-medium">
        {{ __(title) }}
      </p>
    </div>
    <p class="text-sm text-ink-gray-5">
      {{ __(description) }}
    </p>
    <Button
      v-if="button?.label"
      :loading="button.loading"
      :disabled="button.loading"
      class="mt-2"
      @click="onButtonClick"
    >
      {{ __(button.label) }}
    </Button>
  </div>
</template>
<script setup>
import { Button } from "frappe-ui"

const props = defineProps({
  icon: {
    type: Object,
    default: null,
  },
  title: {
    type: String,
    default: "Nothing here",
  },
  description: {
    type: String,
    default: "",
  },
  button: {
    type: Object,
    required: false,
  },
})

async function onButtonClick() {
  if (props.button?.action) await props.button.action()
}
</script>
