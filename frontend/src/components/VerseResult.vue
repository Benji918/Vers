<template>
  <div class="verse-result-card" :class="{ 'is-revealed': !!verse }">
    <!-- Header Reference Badge & Engine Metadata -->
    <div class="card-header">
      <div class="reference-badge">
        <span class="book-name">{{ verse.book }}</span>
        <span class="chapter-verse">{{ referenceLabel }}</span>
        <span class="version-tag">{{ verse.version || 'WEB' }}</span>
      </div>

      <div class="match-meta-pill" v-if="avgConfidence != null">
        <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span>{{ Math.round(avgConfidence * 100) }}% Match · Local FTS5</span>
      </div>
    </div>

    <!-- The Scripture Quotation(s) -->
    <div class="verse-body">
      <div v-for="(v, idx) in verseList" :key="`${v.chapter}:${v.verse}`" class="verse-block">
        <p class="verse-text"><span class="quote-mark left-quote">&ldquo;</span>{{ v.text }}<span class="quote-mark right-quote">&rdquo;</span></p>
        <span v-if="verseList.length > 1" class="verse-num-label">
          {{ verse.book }} {{ v.chapter }}:{{ v.verse }}
        </span>
        <div class="verse-confidence" v-if="v.confidence != null">
          <span class="conf-label">match confidence</span>
          <span class="conf-value">{{ Math.round(v.confidence * 100) }}%</span>
        </div>
      </div>
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
        <span>{{ copied ? 'Copied to Clipboard' : 'Copy Verses' }}</span>
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
import { ref, computed } from 'vue'

const props = defineProps({
  verse: {
    type: Object,
    required: true
  }
})

defineEmits(['dismiss'])

const copied = ref(false)
const isSpeaking = ref(false)

const verseList = computed(() => {
  if (Array.isArray(props.verse.verses) && props.verse.verses.length > 0) {
    return props.verse.verses.map((v) => ({
      ...v,
      version: v.version || props.verse.version || 'WEB'
    }))
  }
  return [{ ...props.verse }]
})

const referenceLabel = computed(() => {
  const chapter = props.verse.chapter || (verseList.value[0] && verseList.value[0].chapter)
  const range = props.verse.range
  if (range && range.start !== range.end) {
    return `${chapter}:${range.start}-${range.end}`
  }
  if (verseList.value.length > 1) {
    const verses = verseList.value.map((v) => v.verse)
    return `${chapter}:${verses.join(',')}`
  }
  return `${chapter}:${verseList.value[0]?.verse}`
})

const textForCopy = computed(() =>
  verseList.value
    .map((v) => `"${v.text}"`)
    .join(' ')
)

const avgConfidence = computed(() => {
  const confs = verseList.value.map((v) => v.confidence).filter((c) => c != null)
  if (confs.length === 0) return null
  return confs.reduce((a, b) => a + b, 0) / confs.length
})

function copyVerse() {
  const fullText = `${textForCopy.value} — ${props.verse.book} ${referenceLabel.value} (${props.verse.version || 'WEB'})`
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
  const utterance = new SpeechSynthesisUtterance(
    verseList.value
      .map((v) => `${props.verse.book} chapter ${v.chapter} verse ${v.verse}. ${v.text}`)
      .join(' ')
  )
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

.verse-block {
  position: relative;
  padding: 1rem 0;
  border-bottom: 1px dashed rgba(26, 26, 26, 0.12);
}

.verse-block:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.verse-num-label {
  display: block;
  margin-top: 0.35rem;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #9C27B0;
}

.verse-confidence {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.3rem;
}

.conf-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.conf-value {
  font-size: 0.75rem;
  font-weight: 700;
  color: #2E7D32;
}

.quote-mark {
  font-family: var(--font-heading);
  font-size: 2.4rem;
  line-height: 1;
  color: rgba(26, 26, 26, 0.35);
  user-select: none;
  vertical-align: text-top;
}

.left-quote {
  margin-right: 0.15rem;
}

.right-quote {
  margin-left: 0.15rem;
  vertical-align: text-bottom;
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
