<template>
  <div class="embed-container">
    <div v-if="loading" class="embed-loading">
      <LoadingIndicator class="w-5 h-5 text-ink-gray-5" />
    </div>

    <div v-else-if="error" class="embed-error">
      <LucideAlertCircle class="w-8 h-8 text-ink-red-5" />
      <p class="text-sm text-ink-gray-5">{{ error }}</p>
    </div>

    <div v-else-if="!files.length" class="embed-empty">
      <LucideFiles class="w-8 h-8 text-ink-gray-3" />
      <p class="text-sm text-ink-gray-5">{{ __('No attachments') }}</p>
    </div>

    <div v-else class="embed-content">
      <div class="embed-header">
        <span class="text-xs font-medium text-ink-gray-5 uppercase">
          {{ files.length }} {{ files.length === 1 ? __('file') : __('files') }}
        </span>
        <button
          class="embed-expand-btn"
          :title="__('Open in Drive')"
          @click="openInDrive"
        >
          <LucideExternalLink class="w-3.5 h-3.5" />
        </button>
      </div>

      <div class="embed-list">
        <div
          v-for="file in files"
          :key="file.name"
          class="embed-file-item"
          @click="downloadFile(file)"
        >
          <component :is="getFileIcon(file)" class="w-4 h-4 text-ink-gray-5 shrink-0" />
          <span class="embed-file-name">{{ file.title }}</span>
          <span class="embed-file-size">{{ formatSize(file.file_size) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue"
import { useRoute } from "vue-router"
import { LoadingIndicator } from "frappe-ui"
import { getDocumentFiles } from "@/resources/files"
import { formatSize } from "@/utils/format"
import LucideFiles from "~icons/lucide/files"
import LucideFile from "~icons/lucide/file"
import LucideFileText from "~icons/lucide/file-text"
import LucideFileImage from "~icons/lucide/file-image"
import LucideExternalLink from "~icons/lucide/external-link"
import LucideAlertCircle from "~icons/lucide/alert-circle"

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const files = ref([])

const doctype = computed(() => decodeURIComponent(route.params.doctype || ""))
const docname = computed(() => decodeURIComponent(route.params.docname || ""))

function getFileIcon(file) {
  const mime = file.mime_type || ""
  if (mime.startsWith("image/")) return LucideFileImage
  if (mime.includes("pdf") || mime.includes("document") || mime.includes("text")) return LucideFileText
  return LucideFile
}

function openInDrive() {
  window.open(`/drive/attachments/${encodeURIComponent(doctype.value)}/${encodeURIComponent(docname.value)}`, "_blank")
}

function downloadFile(file) {
  const url = file.path || file.file_url
  if (url) {
    window.open(url, "_blank")
  }
}

function sendHeightToParent() {
  const height = document.body.scrollHeight
  const targetOrigin = window.location.origin
  window.parent.postMessage({ type: "drive-resize", height }, targetOrigin)
}

async function fetchFiles() {
  if (!doctype.value || !docname.value) {
    error.value = __("Invalid document reference")
    loading.value = false
    return
  }

  loading.value = true
  error.value = null
  
  try {
    const result = await getDocumentFiles.fetch({
      doctype: doctype.value,
      docname: docname.value,
      include_referenced: true,
    })
    files.value = result || []
    
    setTimeout(sendHeightToParent, 100)
  } catch (e) {
    console.error("Error fetching files:", e)
    error.value = __("Could not load attachments")
    files.value = []
  } finally {
    loading.value = false
  }
}

watch([doctype, docname], fetchFiles, { immediate: true })

function handleParentMessage(event) {
  if (event.data?.type === "drive-refresh") {
    fetchFiles()
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
  font-family: var(--font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
  font-size: 13px;
  color: var(--text-color, #1e293b);
  background: var(--bg-color, #ffffff);
  min-height: 100px;
}

.embed-loading,
.embed-error,
.embed-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  text-align: center;
}

.embed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
  background: var(--surface-gray-1, #f8fafc);
}

.embed-expand-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  color: var(--text-muted, #64748b);
}

.embed-expand-btn:hover {
  background: var(--surface-gray-2, #f1f5f9);
  color: var(--text-color, #1e293b);
}

.embed-list {
  max-height: 200px;
  overflow-y: auto;
}

.embed-file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: background 0.15s;
}

.embed-file-item:hover {
  background: var(--surface-gray-1, #f8fafc);
}

.embed-file-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.embed-file-size {
  font-size: 11px;
  color: var(--text-muted, #64748b);
  white-space: nowrap;
}
</style>
