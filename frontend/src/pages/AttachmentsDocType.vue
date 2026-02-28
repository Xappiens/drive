<template>
  <div class="flex flex-col h-full bg-surface-white">
    <!-- Header with breadcrumb -->
    <div class="flex items-center justify-between p-4 border-b border-outline-gray-2">
      <div class="flex items-center gap-2">
        <router-link
          :to="{ name: 'Attachments' }"
          class="flex items-center gap-1 text-ink-gray-5 hover:text-ink-gray-7"
        >
          <LucidePaperclip class="w-4 h-4" />
          <span>{{ __('Attachments') }}</span>
        </router-link>
        <LucideChevronRight class="w-4 h-4 text-ink-gray-4" />
        <span class="font-medium text-ink-gray-9">{{ doctype }}</span>
      </div>
      <div class="flex items-center gap-2">
        <Input
          v-model="search"
          type="text"
          :placeholder="__('Search documents...')"
          class="w-64"
        >
          <template #prefix>
            <LucideSearch class="w-4 h-4 text-ink-gray-4" />
          </template>
        </Input>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center flex-1">
      <LoadingIndicator class="w-6 h-6 text-ink-gray-5" />
    </div>

    <div v-else-if="!filteredDocuments.length" class="flex flex-col items-center justify-center flex-1 gap-4">
      <LucideFileText class="w-16 h-16 text-ink-gray-3" />
      <p class="text-ink-gray-5">{{ __('No documents with attachments') }}</p>
    </div>

    <div v-else class="flex-1 overflow-auto p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <router-link
          v-for="doc in filteredDocuments"
          :key="doc.document_name"
          :to="{ name: 'AttachmentsDocument', params: { doctype, docname: doc.document_name } }"
          class="group flex items-center gap-4 p-4 rounded-lg border border-outline-gray-2 hover:border-outline-gray-3 hover:bg-surface-gray-1 transition-colors"
        >
          <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-surface-gray-2 group-hover:bg-surface-gray-3">
            <LucideFile class="w-6 h-6 text-ink-gray-5" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-ink-gray-9 truncate">{{ doc.title }}</p>
            <p class="text-sm text-ink-gray-5">
              {{ doc.children }} {{ doc.children === 1 ? __('file') : __('files') }}
              <span v-if="doc.file_size"> · {{ formatSize(doc.file_size) }}</span>
            </p>
          </div>
          <LucideChevronRight class="w-5 h-5 text-ink-gray-4 opacity-0 group-hover:opacity-100 transition-opacity" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { useRoute } from "vue-router"
import { Input, LoadingIndicator } from "frappe-ui"
import { getAttachmentDocuments } from "@/resources/files"
import { formatSize } from "@/utils/format"
import LucidePaperclip from "~icons/lucide/paperclip"
import LucideSearch from "~icons/lucide/search"
import LucideFile from "~icons/lucide/file"
import LucideFileText from "~icons/lucide/file-text"
import LucideChevronRight from "~icons/lucide/chevron-right"

const route = useRoute()
const search = ref("")
const loading = ref(true)
const documents = ref([])

const doctype = computed(() => route.params.doctype)

const filteredDocuments = computed(() => {
  if (!search.value) return documents.value
  const searchLower = search.value.toLowerCase()
  return documents.value.filter(
    (doc) =>
      doc.document_name.toLowerCase().includes(searchLower) ||
      doc.title.toLowerCase().includes(searchLower)
  )
})

async function fetchDocuments() {
  loading.value = true
  try {
    const result = await getAttachmentDocuments.fetch({ doctype: doctype.value })
    documents.value = result || []
  } catch (e) {
    console.error("Error fetching documents:", e)
    documents.value = []
  } finally {
    loading.value = false
  }
}

watch(doctype, fetchDocuments, { immediate: true })

onMounted(fetchDocuments)
</script>
