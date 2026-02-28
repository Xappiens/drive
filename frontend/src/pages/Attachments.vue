<template>
  <div class="flex flex-col h-full bg-surface-white">
    <div class="flex items-center justify-between p-4 border-b border-outline-gray-2">
      <div class="flex items-center gap-3">
        <LucidePaperclip class="w-5 h-5 text-ink-gray-5" />
        <h1 class="text-lg font-semibold text-ink-gray-9">{{ __('Attachments') }}</h1>
      </div>
      <div class="flex items-center gap-2">
        <Input
          v-model="search"
          type="text"
          :placeholder="__('Search DocTypes...')"
          class="w-64"
        >
          <template #prefix>
            <LucideSearch class="w-4 h-4 text-ink-gray-4" />
          </template>
        </Input>
      </div>
    </div>

    <div v-if="getAttachmentDocTypes.loading" class="flex items-center justify-center flex-1">
      <LoadingIndicator class="w-6 h-6 text-ink-gray-5" />
    </div>

    <div v-else-if="!filteredDocTypes.length" class="flex flex-col items-center justify-center flex-1 gap-4">
      <LucideFolderOpen class="w-16 h-16 text-ink-gray-3" />
      <p class="text-ink-gray-5">{{ __('No attachments found') }}</p>
    </div>

    <div v-else class="flex-1 overflow-auto p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <router-link
          v-for="dt in filteredDocTypes"
          :key="dt.doctype"
          :to="{ name: 'AttachmentsDocType', params: { doctype: dt.doctype } }"
          class="group flex items-center gap-4 p-4 rounded-lg border border-outline-gray-2 hover:border-outline-gray-3 hover:bg-surface-gray-1 transition-colors"
        >
          <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-surface-gray-2 group-hover:bg-surface-gray-3">
            <LucideFolder class="w-6 h-6 text-ink-gray-5" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-ink-gray-9 truncate">{{ dt.title }}</p>
            <p class="text-sm text-ink-gray-5">
              {{ dt.children }} {{ dt.children === 1 ? __('file') : __('files') }}
            </p>
          </div>
          <LucideChevronRight class="w-5 h-5 text-ink-gray-4 opacity-0 group-hover:opacity-100 transition-opacity" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { Input, LoadingIndicator } from "frappe-ui"
import { getAttachmentDocTypes } from "@/resources/files"
import LucidePaperclip from "~icons/lucide/paperclip"
import LucideSearch from "~icons/lucide/search"
import LucideFolder from "~icons/lucide/folder"
import LucideFolderOpen from "~icons/lucide/folder-open"
import LucideChevronRight from "~icons/lucide/chevron-right"

const search = ref("")

const filteredDocTypes = computed(() => {
  const data = getAttachmentDocTypes.data || []
  if (!search.value) return data
  const searchLower = search.value.toLowerCase()
  return data.filter(
    (dt) =>
      dt.doctype.toLowerCase().includes(searchLower) ||
      dt.title.toLowerCase().includes(searchLower)
  )
})

onMounted(() => {
  getAttachmentDocTypes.fetch()
})
</script>
