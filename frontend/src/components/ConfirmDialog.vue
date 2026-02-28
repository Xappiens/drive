<template>
  <Dialog
    v-model="open"
    :options="dialogOptions"
    @close="dialogType = ''"
  >
    <template #body-content>
      <div class="flex items-center justify-start">
        <div class="text-base text-ink-gray-6">
          <template v-if="props.entities.length">
            {{ dialogData.prefix }}
          </template>
          <span v-html="dialogData.message" />
        </div>
      </div>
      <ErrorMessage
        class="my-1 text-center"
        :message="updateResource.error"
      />
    </template>
  </Dialog>
</template>
<script setup>
import { ref, computed } from "vue"
import { createResource, Dialog, ErrorMessage, toast } from "frappe-ui"
import { useTimeAgo } from "@vueuse/core"

import {
  mutate,
  getTrash,
  toggleFav,
  clearRecent,
  clearTrash,
} from "@/resources/files.js"
import { sortEntities, getTimeAgoOptions } from "@/utils/files.js"

import LucideRotateCcw from "~icons/lucide/rotate-ccw"
import {} from "@/resources/files"

const props = defineProps({
  entities: {
    type: Array,
    required: true,
  },
})
const emit = defineEmits(["success"])
const dialogType = defineModel()
const open = ref(true)

const dialogData = computed(() => {
  const n = props.entities.length
  const one = n === 1
  const MAP = {
    restore: {
      prefix: one ? `"${props.entities[0].title}" ` : window.__("These items "),
      title: one
        ? window.__("Restore an item")
        : window.__("Restore %s items").replace("%s", n),
      message: one
        ? window.__("will be restored to its original location.")
        : window.__("will be restored to their original locations."),
      url: "drive.api.files.remove_or_restore",
      onSuccess: () => {
        getTrash.setData((d) =>
          d.filter((k) => !props.entities.map((l) => l.name).includes(k.name))
        )
      },
      button: {
        variant: "solid",
        label: window.__("Restore"),
        iconLeft: LucideRotateCcw,
      },
      toastMessage: one
        ? window.__("Restored an item.")
        : window.__("Restored %s items.").replace("%s", n),
    },
    remove: {
      prefix: one ? `"${props.entities[0].title}" ` : window.__("These items "),
      title: one
        ? window.__("Move an item to Trash")
        : window.__("Move %s items to Trash").replace("%s", n),
      message: window.__(
        "will be moved to Trash.<br/><br/> Items in trash are deleted forever after 30 days."
      ),
      url: "drive.api.files.remove_or_restore",
      button: {
        label: window.__("Move to Trash"),
        theme: "red",
        variant: "subtle",
      },
      onSuccess: () => {
        getTrash.setData(
          sortEntities([
            ...getTrash.data,
            ...props.entities.map((k) => {
              k.modified = Date()
              k.relativeModified = useTimeAgo(k.modified, getTimeAgoOptions())
              return k
            }),
          ])
        )
      },
      toastMessage: one
        ? window.__("Moved an item to Trash.")
        : window.__("Moved %s items to Trash.").replace("%s", n),
    },
    d: {
      prefix: one ? `"${props.entities[0].title}" ` : window.__("These items "),
      title: one
        ? window.__("Delete an item")
        : window.__("Delete %s items").replace("%s", n),
      url: "drive.api.files.delete_entities",
      message: window.__(
        "will be deleted - you can no longer access it.<br/><br/> <span class=font-semibold>This is an irreversible action.</span>"
      ),
      button: {
        label: window.__("Delete — forever."),
        theme: "red",
        iconLeft: LucideTrash,
        variant: "solid",
      },
      toastMessage: one
        ? window.__("Deleted an item.")
        : window.__("Deleted %s items.").replace("%s", n),
    },
    "cta-recents": {
      prefix: "",
      title: window.__("Are you sure?"),
      message: window.__("All your recently viewed files will be cleared."),
      button: { label: window.__("Clear") },
      resource: clearRecent,
    },
    "cta-favourites": {
      prefix: "",
      title: window.__("Are you sure?"),
      message: window.__("All your favourite items will be cleared."),
      button: { label: window.__("Clear") },
      resource: toggleFav,
    },
    "cta-trash": {
      prefix: "",
      title: window.__("Clear your Trash"),
      message: window.__("All items in your Trash will be deleted forever. <br/><br/> <span class=font-semibold>This is an irreversible process.</span>"),
      button: { label: window.__("Delete"), variant: "solid", iconLeft: LucideTrash },
      resource: clearTrash,
    },
  }
  return MAP[dialogType.value]
})

const loading = computed(
  () => (dialogData.value.resource || updateResource).loading
)
const dialogOptions = computed(() => {
  return {
    title: dialogData.value.title,
    size: "sm",
    actions: [
      {
        onClick: async () => {
          if (dialogData.value.resource) {
            open.value = false
            await dialogData.value.resource.submit()
            emit("success")
          } else updateResource.submit()
        },
        ...dialogData.value.button,
        disabled: loading.value,
        // loading: loading.value,
      },
    ],
  }
})

const updateResource = createResource({
  url: dialogData.value.url,
  makeParams: () => {
    open.value = ""
    return {
      entity_names:
        typeof props.entities === "string"
          ? JSON.stringify([props.entities])
          : JSON.stringify(props.entities.map((entity) => entity.name)),
    }
  },
  onSuccess(data) {
    emit("success", data)
    updateResource.reset()
    if (dialogData.value.mutate) mutate(props.entities, props.dialogData.mutate)
    if (dialogData.value.onSuccess)
      dialogData.value.onSuccess(props.entities, data)
    toast.success(dialogData.value.toastMessage)
  },
})
</script>
