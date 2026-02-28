<template>
  <GenericPage
    :get-entities="attachmentDocTypes"
    :show-sort="true"
    :empty="{
      icon: LucidePaperclip,
      title: __('No attachments'),
      description: __('Files attached to documents will appear here.'),
    }"
  />
</template>

<script setup>
import GenericPage from "@/components/GenericPage.vue"
import { createResource } from "frappe-ui"
import { onMounted } from "vue"
import { useStore } from "vuex"
import LucidePaperclip from "~icons/lucide/paperclip"

const store = useStore()
store.commit("setCurrentFolder", { name: "", team: "" })

const attachmentDocTypes = createResource({
  url: "drive.api.attachments.get_doctypes_with_attachments",
  method: "GET",
  cache: "attachment-doctypes",
  transform(data) {
    return data.map((k) => ({
      ...k,
      name: k.doctype,
      title: k.doctype_label || k.doctype,
      is_group: true,
      mime_type: "folder",
      file_type: "DocType",
      file_size: 0,
      children: k.file_count,
      modified: k.last_modified,
      owner: "",
      is_attachment_doctype: true,
    }))
  },
})

onMounted(() => {
  attachmentDocTypes.fetch()
})
</script>
