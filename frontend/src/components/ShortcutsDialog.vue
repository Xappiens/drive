<template>
  <Dialog
    v-model="open"
    :options="{ title: __('Keyboard Shortcuts'), size: '4xl' }"
  >
    <template #body-content>
      <div
        v-focus
        class="w-full grid grid-cols-2 gap-10 py-1"
      >
        <div
          v-for="group in shortcutGroups"
          :key="group.title"
          class="border-b pb-4"
        >
          <h2 class="text-lg font-semibold text-ink-gray-8 mb-4">
            {{ group.title }}
          </h2>
          <ul class="space-y-2">
            <li
              v-for="(shortcut, index) in group.shortcuts"
              :key="index"
              class="flex items-start justify-between"
            >
              <div class="text-ink-gray-7 text-base">
                {{ shortcut[1] }}
              </div>
              <div class="flex space-x-1 w-[9rem] gap-1 justify-start">
                <span
                  v-for="(key, kIndex) in shortcut[0]"
                  :key="kIndex"
                  class="px-2 py-0.5 bg-surface-gray-2 border border-outline-gray-2 text-xs rounded-sm font-mono text-ink-gray-8 shadow-sm"
                >
                  {{ key }}
                </span>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { Dialog } from "frappe-ui"
import { computed } from "vue"
const props = defineProps({
  modelValue: Boolean,
})
const emit = defineEmits(["update:modelValue"])

const getLabel = (key) =>
  document.querySelector(`[accesskey='${key}']`)?.accessKeyLabel

const metaKey = computed(() => {
  const platform = navigator.platform.toLowerCase()
  if (platform.includes("mac")) {
    return "⌘" // Command key
  } else if (platform.includes("win")) {
    return "⊞" // Windows key
  }
  return "Meta"
})
const shortcutGroups = [
  {
    title: __("General"),
    shortcuts: [
      [[metaKey.value, "K"], __("Find Files")],
      [["Ctrl", ","], __("Open Settings")],
    ],
  },
  {
    title: __("Navigation"),
    shortcuts: [
      [getLabel("i"), __("Inbox")],
      [getLabel("h"), __("Home")],
      [getLabel("t"), __("Team")],
      [getLabel("r"), __("Recents")],
      [getLabel("f"), __("Favourites")],
      [getLabel("s"), __("Shared")],
      [getLabel("d"), __("Shared")],
    ],
  },
  {
    title: __("List"),
    shortcuts: [
      [[metaKey.value, "A"], __("Select all")],
      [["Esc"], __("Unselect all")],
      [getLabel("s"), __("Share selected file(s)")],
      [getLabel("m"), __("Move selected file(s)")],
      [[metaKey.value, "Delete"], __("Delete selected file(s)")],
      [getLabel("u"), __("Upload a file")],
      [getLabel("n"), __("Create a folder")],
    ],
  },
]

const open = computed({
  get() {
    return props.modelValue
  },
  set(newValue) {
    emit("update:modelValue", newValue)
  },
})
</script>
