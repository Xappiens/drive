<template>
  <GenericPage
    :get-entities="getFavourites"
    :empty="{
      icon: LucideStar,
      title: __('No favourites yet'),
      description: 'You can save your favourites here.',
    }"
  />
</template>

<script setup>
import GenericPage from "@/components/GenericPage.vue"
import { getFavourites } from "@/resources/files"
import LucideStar from "~icons/lucide/star"
</script>
