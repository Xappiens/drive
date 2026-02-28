<template>
  <div class="flex flex-col h-full bg-surface-white">
    <!-- Header with breadcrumb -->
    <div class="flex items-center justify-between p-4 border-b border-outline-gray-2">
      <div class="flex items-center gap-2 flex-wrap">
        <router-link
          :to="{ name: 'Attachments' }"
          class="flex items-center gap-1 text-ink-gray-5 hover:text-ink-gray-7"
        >
          <LucidePaperclip class="w-4 h-4" />
          <span>{{ __('Attachments') }}</span>
        </router-link>
        <LucideChevronRight class="w-4 h-4 text-ink-gray-4" />
        <router-link
          :to="{ name: 'AttachmentsDocType', params: { doctype } }"
          class="text-ink-gray-5 hover:text-ink-gray-7"
        >
          {{ doctype }}
        </router-link>
        <LucideChevronRight class="w-4 h-4 text-ink-gray-4" />
        <span class="font-medium text-ink-gray-9 truncate max-w-[200px]">{{ docname }}</span>
      </div>
      <div class="flex items-center gap-2">
        <Button
          variant="subtle"
          :label="__('Open Document')"
          @click="openDocument"
        >
          <template #prefix>
            <LucideExternalLink class="w-4 h-4" />
          </template>
        </Button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center flex-1">
      <LoadingIndicator class="w-6 h-6 text-ink-gray-5" />
    </div>

    <div v-else-if="!files.length" class="flex flex-col items-center justify-center flex-1 gap-4">
      <LucideFiles class="w-16 h-16 text-ink-gray-3" />
      <p class="text-ink-gray-5">{{ __('No files attached to this document') }}</p>
    </div>

    <div v-else class="flex-1 overflow-auto p-4">
      <div class="space-y-2">
        <div
          v-for="file in files"
          :key="file.name"
          class="group flex items-center gap-4 p-3 rounded-lg border border-outline-gray-2 hover:border-outline-gray-3 hover:bg-surface-gray-1 transition-colors"
        >
          <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-surface-gray-2">
            <component :is="getFileIcon(file)" class="w-5 h-5 text-ink-gray-5" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <p class="font-medium text-ink-gray-9 truncate">{{ file.title }}</p>
              <span
                v-if="file.attachment_source === 'field'"
                class="px-2 py-0.5 text-xs rounded bg-surface-gray-2 text-ink-gray-5"
              >
                {{ file.attachment_field }}
              </span>
            </div>
            <p class="text-sm text-ink-gray-5">
              {{ formatSize(file.file_size) }}
              <span v-if="file.modified"> · {{ formatDate(file.modified) }}</span>
            </p>
          </div>
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="sm"
              :title="__('Download')"
              @click.prevent="downloadFile(file)"
            >
              <LucideDownload class="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              :title="__('Preview')"
              @click.prevent="previewFile(file)"
            >
              <LucideEye class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { useRoute } from "vue-router"
import { Button, LoadingIndicator } from "frappe-ui"
import { getDocumentFiles } from "@/resources/files"
import { formatSize, formatDate } from "@/utils/format"
import LucidePaperclip from "~icons/lucide/paperclip"
import LucideChevronRight from "~icons/lucide/chevron-right"
import LucideExternalLink from "~icons/lucide/external-link"
import LucideFiles from "~icons/lucide/files"
import LucideFile from "~icons/lucide/file"
import LucideFileText from "~icons/lucide/file-text"
import LucideFileImage from "~icons/lucide/file-image"
import LucideFileVideo from "~icons/lucide/file-video"
import LucideFileAudio from "~icons/lucide/file-audio"
import LucideFileArchive from "~icons/lucide/file-archive"
import LucideDownload from "~icons/lucide/download"
import LucideEye from "~icons/lucide/eye"

const route = useRoute()
const loading = ref(true)
const files = ref([])

const doctype = computed(() => route.params.doctype)
const docname = computed(() => route.params.docname)

function getFileIcon(file) {
  const mime = file.mime_type || ""
  if (mime.startsWith("image/")) return LucideFileImage
  if (mime.startsWith("video/")) return LucideFileVideo
  if (mime.startsWith("audio/")) return LucideFileAudio
  if (mime.includes("zip") || mime.includes("archive") || mime.includes("tar")) return LucideFileArchive
  if (mime.includes("pdf") || mime.includes("document") || mime.includes("text")) return LucideFileText
  return LucideFile
}

function openDocument() {
  window.open(`/app/${encodeURIComponent(doctype.value)}/${encodeURIComponent(docname.value)}`, "_blank")
}

function downloadFile(file) {
  const url = file.path || file.file_url
  if (url) {
    window.open(url, "_blank")
  }
}

function previewFile(file) {
  const url = file.path || file.file_url
  if (url) {
    window.open(url, "_blank")
  }
}

async function fetchFiles() {
  loading.value = true
  try {
    const result = await getDocumentFiles.fetch({
      doctype: doctype.value,
      docname: docname.value,
      include_referenced: true,
    })
    files.value = result || []
  } catch (e) {
    console.error("Error fetching files:", e)
    files.value = []
  } finally {
    loading.value = false
  }
}

watch([doctype, docname], fetchFiles, { immediate: true })
</script>
