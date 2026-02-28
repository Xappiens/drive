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

store.commit("setCurrentFolder", { name: docname.value, team: "" })

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
      data.map((k) => ({
        ...k,
        name: k.name,
        title: k.file_name,
        is_group: false,
        file_size: k.file_size || 0,
        modified: k.modified,
        path: k.file_url,
        owner: k.owner || "",
        is_attachment: true,
        attachment_source: k.source,
        attachment_field: k.field,
        attachment_doctype: doctype.value,
        attachment_docname: docname.value,
      }))
    )
  },
})

watch([doctype, docname], () => {
  if (doctype.value && docname.value) {
    documentFiles.fetch()
  }
}, { immediate: true })
</script>
