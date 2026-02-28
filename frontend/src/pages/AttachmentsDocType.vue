<template>
  <GenericPage
    :get-entities="attachmentDocuments"
    :show-sort="true"
    :empty="{
      icon: LucideFileText,
      title: __('No documents with attachments'),
      description: __('Documents with attached files will appear here.'),
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
import LucideFileText from "~icons/lucide/file-text"

const route = useRoute()
const store = useStore()

const doctype = computed(() => route.params.doctype)

store.commit("setCurrentFolder", { name: doctype.value, team: "" })

const attachmentDocuments = createResource({
  url: "drive.api.attachments.get_documents_with_attachments",
  method: "GET",
  makeParams: () => ({
    doctype: doctype.value,
  }),
  transform(data) {
    return prettyData(data.map((k) => ({
      ...k,
      name: k.document_name,
      title: k.title || k.document_name,
      is_group: true,
      mime_type: "folder",
      file_type: "Document",
      file_size: k.total_size || 0,
      children: k.file_count,
      modified: k.last_modified,
      owner: "",
      is_attachment_document: true,
      attachment_doctype: doctype.value,
    })))
  },
})

watch(doctype, () => {
  if (doctype.value) {
    attachmentDocuments.fetch()
  }
}, { immediate: true })
</script>
