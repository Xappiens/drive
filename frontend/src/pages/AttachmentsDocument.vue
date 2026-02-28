<template>
  <GenericPage
    :get-entities="documentFiles"
    :show-sort="true"
    :empty="{
      icon: LucideFiles,
      title: __('No files attached'),
      description: __('Files attached to this document will appear here.'),
    }"
  />
</template>

<script setup>
import GenericPage from "@/components/GenericPage.vue"
import { createResource } from "frappe-ui"
import { watch, computed } from "vue"
import { useRoute } from "vue-router"
import { useStore } from "vuex"
import { prettyData } from "@/utils/files"
import LucideFiles from "~icons/lucide/files"

const route = useRoute()
const store = useStore()

const doctype = computed(() => route.params.doctype)
const docname = computed(() => route.params.docname)

function updateBreadcrumbs() {
  store.commit("setCurrentFolder", { name: docname.value, team: "" })
  store.commit("setBreadcrumbs", [
    {
      label: __("Attachments"),
      name: "Attachments",
      route: { name: "Attachments" },
    },
    {
      label: doctype.value,
      name: doctype.value,
      route: { name: "AttachmentsDocType", params: { doctype: doctype.value } },
    },
    {
      label: docname.value,
      name: docname.value,
    },
  ])
}

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
    updateBreadcrumbs()
    documentFiles.fetch()
  }
}, { immediate: true })
</script>
