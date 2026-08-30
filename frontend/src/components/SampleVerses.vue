<template>
  <div class="sample-prompts-container">
    <span class="sample-label">Or try speaking a classic scripture:</span>
    <div class="sample-chips-grid">
      <button 
        v-for="(item, idx) in sampleVerses" 
        :key="idx" 
        class="verse-chip"
        @click="$emit('select-sample', item)"
        :title="`Test voice lookup with ${item.book} ${item.chapter}:${item.verse}`"
      >
        <span class="chip-reference">{{ item.book }} {{ item.chapter }}:{{ item.verse }}</span>
        <span class="chip-preview">"{{ getSnippet(item.text) }}"</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { SAMPLE_VERSES_DB } from '@/services/websocket.js'

defineProps({
  sampleVerses: {
    type: Array,
    default: () => SAMPLE_VERSES_DB.slice(0, 4)
  }
})

defineEmits(['select-sample'])

function getSnippet(text) {
  const words = text.split(' ')
  if (words.length > 5) {
    return words.slice(0, 5).join(' ') + '...'
  }
  return text
}
</script>

<style scoped>
.sample-prompts-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  width: 100%;
  max-width: 780px;
}

.sample-label {
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  margin-bottom: 0.85rem;
}

.sample-chips-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
}

.verse-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.95rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid var(--color-border);
  backdrop-filter: blur(8px);
  color: var(--color-text-secondary);
  font-size: 0.86rem;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.verse-chip:hover {
  background: #FFFFFF;
  border-color: rgba(26, 26, 26, 0.2);
  color: var(--color-text-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(26, 26, 26, 0.06);
}

.chip-reference {
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: var(--font-heading);
  font-size: 1rem;
}

.chip-preview {
  font-style: italic;
  color: var(--color-text-muted);
}
</style>
