<template>
  <div :class="['embed-container', { 'embed-modal': isModal }]">
    <GenericPage
      v-if="doctype && docname"
      :get-entities="documentFiles"
      :show-sort="true"
      :empty="{
        icon: LucideFiles,
        title: __('No attachments'),
        description: __('Files attached to this document will appear here.'),
      }"
    />
  </div>
</template>

<script setup>
import { computed, watch, onMounted, onBeforeUnmount } from "vue"
import { useRoute } from "vue-router"
import { useStore } from "vuex"
import { createResource } from "frappe-ui"
import { prettyData } from "@/utils/files"
import GenericPage from "@/components/GenericPage.vue"
import LucideFiles from "~icons/lucide/files"

const route = useRoute()
const store = useStore()

const doctype = computed(() => decodeURIComponent(route.params.doctype || ""))
const docname = computed(() => decodeURIComponent(route.params.docname || ""))
const isModal = computed(() => route.query.modal === "1")

store.commit("setCurrentFolder", { name: docname.value, team: "" })
store.commit("setBreadcrumbs", [
  {
    label: docname.value,
    name: docname.value,
  },
])

function getFileTypeFromMime(mimeType) {
  if (!mimeType) return "Unknown"
  if (mimeType.startsWith("image/")) return "Image"
  if (mimeType.startsWith("video/")) return "Video"
  if (mimeType.startsWith("audio/")) return "Audio"
  if (mimeType.includes("pdf")) return "PDF"
  if (mimeType.includes("spreadsheet") || mimeType.includes("excel")) return "Spreadsheet"
  if (mimeType.includes("presentation") || mimeType.includes("powerpoint")) return "Presentation"
  if (mimeType.includes("document") || mimeType.includes("word")) return "Document"
  if (mimeType.includes("text/")) return "Text"
  if (mimeType.includes("zip") || mimeType.includes("archive") || mimeType.includes("compressed")) return "Archive"
  return "Unknown"
}

const documentFiles = createResource({
  url: "drive.api.attachments.get_document_files",
  method: "GET",
  makeParams: () => ({
    doctype: doctype.value,
    docname: docname.value,
    include_referenced: true,
  }),
  transform(data) {
    return prettyData(
      data.map((k) => {
        const isImage = k.mime_type?.startsWith("image/")
        const fileType = getFileTypeFromMime(k.mime_type)
        return {
          ...k,
          name: k.name,
          title: k.file_name,
          is_group: false,
          file_type: fileType,
          file_size: k.file_size || 0,
          modified: k.modified,
          path: k.file_url,
          owner: k.owner || "",
          is_attachment: true,
          attachment_source: k.source,
          attachment_field: k.field,
          attachment_doctype: doctype.value,
          attachment_docname: docname.value,
          thumbnail: isImage ? k.file_url : null,
        }
      })
    )
  },
})

watch([doctype, docname], () => {
  if (doctype.value && docname.value) {
    documentFiles.fetch()
  }
}, { immediate: true })

function handleParentMessage(event) {
  if (event.origin !== window.location.origin) return
  if (event.data?.type === "drive-refresh") {
    documentFiles.fetch()
  }
}

onMounted(() => {
  window.addEventListener("message", handleParentMessage)
})

onBeforeUnmount(() => {
  window.removeEventListener("message", handleParentMessage)
})
</script>

<style scoped>
.embed-container {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.embed-modal {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.embed-modal :deep(.generic-page) {
  flex: 1;
  overflow: hidden;
}
</style>
