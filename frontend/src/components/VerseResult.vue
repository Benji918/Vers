<template>
  <div class="verse-result-card" :class="{ 'is-revealed': !!verse }">
    <!-- Header Reference Badge & Engine Metadata -->
    <div class="card-header">
      <div class="reference-badge">
        <span class="book-name">{{ verse.book }}</span>
        <span class="chapter-verse">{{ verse.chapter }}:{{ verse.verse }}</span>
        <span class="version-tag">{{ verse.version || 'KJV' }}</span>
      </div>

      <div class="match-meta-pill" v-if="verse.confidence">
        <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span>{{ Math.round(verse.confidence * 100) }}% Match · Local FTS5</span>
      </div>
    </div>

    <!-- The Scripture Quotation Text in EB Garamond -->
    <div class="verse-body">
      <span class="quote-mark left-quote">“</span>
      <p class="verse-text">{{ verse.text }}</p>
      <span class="quote-mark right-quote">”</span>
    </div>

    <!-- Interactive Action Toolbar -->
    <div class="card-actions">
      <button class="action-btn" @click="copyVerse" :title="copied ? 'Copied!' : 'Copy verse scripture'">
        <svg v-if="!copied" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#2E7D32" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span>{{ copied ? 'Copied to Clipboard' : 'Copy Verse' }}</span>
      </button>

      <button class="action-btn" @click="speakVerseText" :title="'Read scripture aloud'">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
          <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
        </svg>
        <span>{{ isSpeaking ? 'Playing...' : 'Listen' }}</span>
      </button>

      <button class="dismiss-btn" @click="$emit('dismiss')" title="Clear match result">
        <span>Clear</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  verse: {
    type: Object,
    required: true
  }
})

defineEmits(['dismiss'])

const copied = ref(false)
const isSpeaking = ref(false)

function copyVerse() {
  const fullText = `"${props.verse.text}" — ${props.verse.book} ${props.verse.chapter}:${props.verse.verse} (${props.verse.version || 'KJV'})`
  navigator.clipboard.writeText(fullText).then(() => {
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2200)
  })
}

function speakVerseText() {
  if (!('speechSynthesis' in window)) return
  if (isSpeaking.value) {
    window.speechSynthesis.cancel()
    isSpeaking.value = false
    return
  }

  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(`${props.verse.book} chapter ${props.verse.chapter} verse ${props.verse.verse}. ${props.verse.text}`)
  utterance.rate = 0.95
  utterance.pitch = 1.0

  utterance.onend = () => {
    isSpeaking.value = false
  }
  utterance.onerror = () => {
    isSpeaking.value = false
  }

  isSpeaking.value = true
  window.speechSynthesis.speak(utterance)
}
</script>

<style scoped>
.verse-result-card {
  width: 100%;
  max-width: 720px;
  background: var(--color-surface-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-accent);
  border-radius: var(--radius-card);
  padding: 2rem 2.25rem;
  box-shadow: var(--shadow-elevated);
  margin: 1.5rem auto 0;
  animation: cardFadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  transition: all 0.3s ease;
}

@keyframes cardFadeUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.reference-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 0.5rem;
  background: var(--color-accent);
  padding: 0.35rem 0.9rem;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(26, 26, 26, 0.08);
}

.book-name {
  font-family: var(--font-heading);
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--color-text-primary);
}

.chapter-verse {
  font-family: var(--font-heading);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.version-tag {
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(26, 26, 26, 0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  color: var(--color-text-secondary);
  letter-spacing: 0.05em;
}

.match-meta-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: #2E7D32;
  background: rgba(76, 175, 80, 0.12);
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-pill);
}

.check-icon {
  width: 14px;
  height: 14px;
}

.verse-body {
  position: relative;
  margin: 1.2rem 0 1.6rem;
  padding: 0 0.5rem;
}

.quote-mark {
  font-family: var(--font-heading);
  font-size: 3rem;
  line-height: 0;
  color: rgba(26, 26, 26, 0.18);
  user-select: none;
}

.left-quote {
  position: absolute;
  top: 0.5rem;
  left: -0.75rem;
}

.right-quote {
  display: inline-block;
  vertical-align: sub;
  margin-left: 0.25rem;
}

.verse-text {
  font-family: var(--font-heading);
  font-size: 1.65rem;
  line-height: 1.45;
  font-style: italic;
  font-weight: 500;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.75rem;
  border-top: 1px solid var(--color-border);
  padding-top: 1.1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.95rem;
  border-radius: var(--radius-pill);
  background: rgba(26, 26, 26, 0.04);
  border: 1px solid var(--color-border);
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--color-text-primary);
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--color-accent);
  transform: translateY(-1px);
}

.dismiss-btn {
  margin-left: auto;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-muted);
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-pill);
  transition: all 0.2s ease;
}

.dismiss-btn:hover {
  color: var(--color-text-primary);
  background: rgba(26, 26, 26, 0.05);
}

@media (max-width: 640px) {
  .verse-result-card {
    padding: 1.5rem 1.25rem;
  }
  .verse-text {
    font-size: 1.35rem;
  }
}
</style>
