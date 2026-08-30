<template>
  <div class="app-root">
    <!-- Animated Ethereal Background Waves -->
    <AudioWaveBackground 
      :isListening="isListening" 
      :audioLevel="audioLevel" 
    />

    <!-- Navigation Bar -->
    <Navbar 
      :isListening="isListening"
      @open-architecture="showArchitectureModal = true"
    />

    <!-- Main Landing Viewport (Top-anchored so headline never shifts) -->
    <main class="hero-main-container">
      <section class="hero-content">
        <!-- Static Hero Headline (Always rock-solid in place) -->
        <h1 class="hero-headline">
          Speak a verse.<br />
          <span class="headline-italic">Discover where it is written.</span>
        </h1>

        <!-- Subtitle -->
        <p class="hero-subtitle">
          Say any scripture aloud. Vers pinpoints the exact book, chapter, and verse in real time.
        </p>

        <!-- The Central Listen/Speak Master Button -->
        <ListenButton 
          :isListening="isListening"
          :isMatching="isMatching"
          :audioLevel="audioLevel"
          @toggle-listen="toggleListening"
        />

        <!-- Stable Reserved Slot for Live Transcript Bubble (Zero layout shift) -->
        <div class="transcript-slot-wrapper">
          <transition name="transcript-fade">
            <div v-if="isListening && transcriptText" class="live-transcript-bubble">
              <span class="transcript-dot">●</span>
              <span class="transcript-label">Transcribing:</span>
              <span class="transcript-words">“{{ transcriptText }}”</span>
            </div>
          </transition>
        </div>

        <!-- Matched Verse Result Card -->
        <transition name="result-slide">
          <VerseResult 
            v-if="matchedVerse" 
            :verse="matchedVerse"
            @dismiss="matchedVerse = null"
          />
        </transition>

        <!-- Interactive Sample Verses Chips -->
        <SampleVerses 
          v-if="!matchedVerse"
          :sampleVerses="sampleVerses"
          @select-sample="handleSampleSelected" 
        />
      </section>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p class="footer-text">
        <span>Vers</span> · Voice Scripture Recognition · Built with Vue.js, Deepgram Streaming & Local FTS5
      </p>
    </footer>

    <!-- Architecture / How It Works Modal -->
    <ArchitectureModal 
      :isOpen="showArchitectureModal"
      @close="showArchitectureModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import Navbar from './components/Navbar.vue'
import ListenButton from './components/ListenButton.vue'
import AudioWaveBackground from './components/AudioWaveBackground.vue'
import VerseResult from './components/VerseResult.vue'
import SampleVerses from './components/SampleVerses.vue'
import ArchitectureModal from './components/ArchitectureModal.vue'
import { AudioWebSocketService, fetchSampleVerses } from './services/websocket.js'

// State
const isListening = ref(false)
const isMatching = ref(false)
const audioLevel = ref(0.3)
const transcriptText = ref('')
const matchedVerse = ref(null)
const showArchitectureModal = ref(false)
const sampleVerses = ref([])

let audioService = null

function initializeAudioService() {
  audioService = new AudioWebSocketService({
    onStatusChange: (status) => {
      if (status.state === 'listening') {
        isListening.value = true
        isMatching.value = false
      } else if (status.state === 'matching') {
        isListening.value = false
        isMatching.value = true
      } else if (status.state === 'idle') {
        isListening.value = false
        isMatching.value = false
      }
    },
    onTranscript: (text) => {
      transcriptText.value = text
    },
    onVerseMatch: (verseData) => {
      matchedVerse.value = verseData
      isListening.value = false
      isMatching.value = false
      nextTick(() => {
        const card = document.querySelector('.verse-result-card')
        if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      })
    },
    onAudioLevel: (level) => {
      audioLevel.value = level
    },
    onError: (err) => {
      console.warn('Audio service notification:', err)
      isListening.value = false
      isMatching.value = false
    }
  })
}

function toggleListening() {
  if (isListening.value || isMatching.value) {
    isListening.value = false
    isMatching.value = false
    if (audioService) {
      if (audioService.accumulatedText) {
        audioService.finalize()
      } else {
        audioService.stopListening()
      }
    }
  } else {
    isListening.value = true
    isMatching.value = false
    transcriptText.value = ''
    matchedVerse.value = null
    if (audioService) audioService.startListening()
  }
}

function handleSampleSelected(sample) {
  isListening.value = false
  isMatching.value = true
  transcriptText.value = sample.text
  matchedVerse.value = null
  if (audioService) {
    audioService.sendTextQuery(sample.text)
  }
}

function handleKeyDown(event) {
  if (event.code === 'Space' && event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
    event.preventDefault()
    toggleListening()
  } else if (event.code === 'Escape') {
    if (showArchitectureModal.value) {
      showArchitectureModal.value = false
    } else if (isListening.value) {
      toggleListening()
    }
  }
}

onMounted(async () => {
  initializeAudioService()
  window.addEventListener('keydown', handleKeyDown)
  sampleVerses.value = await fetchSampleVerses(6)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  if (audioService) audioService.stopListening()
})
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* Top-anchored layout: No vertical re-centering jump */
.hero-main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 7rem 1.5rem 3rem;
  position: relative;
  z-index: 10;
}

.hero-content {
  width: 100%;
  max-width: 880px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* Hero Typography */
.hero-headline {
  font-family: var(--font-heading);
  font-size: clamp(2.8rem, 6vw, 4.2rem);
  font-weight: 500;
  line-height: 1.08;
  letter-spacing: -0.025em;
  color: var(--color-text-primary);
  margin-bottom: 1.1rem;
}

.headline-italic {
  font-style: italic;
  font-weight: 400;
  color: #2b2b2b;
}

/* Hero Subtitle */
.hero-subtitle {
  font-family: var(--font-body);
  font-size: clamp(1.1rem, 2vw, 1.25rem);
  font-weight: 400;
  color: var(--color-text-secondary);
  max-width: 580px;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

/* Stable Slot for Live Transcript */
.transcript-slot-wrapper {
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.live-transcript-bubble {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 1.35rem;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--color-border-accent);
  border-radius: var(--radius-pill);
  box-shadow: var(--shadow-soft);
}

.transcript-dot {
  color: #D946EF;
  font-size: 0.8rem;
  animation: pulseGlow 1.2s infinite;
}

.transcript-label {
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #D946EF;
}

.transcript-words {
  font-family: var(--font-heading);
  font-size: 1.15rem;
  font-style: italic;
  color: var(--color-text-primary);
}

/* Transitions */
.transcript-fade-enter-active,
.transcript-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.transcript-fade-enter-from,
.transcript-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.result-slide-enter-active,
.result-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.result-slide-enter-from,
.result-slide-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
}

/* Footer */
.app-footer {
  position: relative;
  z-index: 10;
  padding: 1.5rem 2rem;
  text-align: center;
  border-top: 1px solid var(--color-border);
}

.footer-text {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.footer-text span {
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: var(--font-heading);
}

@media (max-width: 640px) {
  .hero-main-container {
    padding-top: 5.5rem;
  }
}
</style>
