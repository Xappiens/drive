<template>
  <GenericPage
    :get-entities="getPersonal"
    :empty="emptyState"
    :verify="{
      data: {
        write: 1,
        upload: 1,
      },
    }"
  />
</template>

<script setup>
import { computed, onMounted } from "vue"
import GenericPage from "@/components/GenericPage.vue"
import { getPersonal, loadDemoFiles } from "@/resources/files"
import { useStore } from "vuex"
import { allUsers } from "@/resources/permissions"
import LucideHome from "~icons/lucide/home"
import emitter from "@/emitter"
import { toast } from "@/utils/toasts"

const store = useStore()
store.commit("setCurrentFolder", { name: "", team: "" })
allUsers.fetch(null)

// Forzar recarga limpia al entrar en Inicio: limpiar datos cacheados y volver a pedir al servidor
onMounted(() => {
  getPersonal.setData([])
  getPersonal.fetch({ personal: 1, team: "" })
})

async function loadDemoAndRefresh() {
  const out = await loadDemoFiles.submit()
  if (out?.message) toast({ title: __('Done'), text: out.message })
  emitter.emit('refresh')
}

const emptyState = computed(() => ({
  icon: LucideHome,
  title: __('No files yet'),
  description: __('Upload to get started!'),
  button: {
    label: __('Load sample files'),
    loading: loadDemoFiles.loading,
    action: loadDemoAndRefresh,
  },
}))
</script>
