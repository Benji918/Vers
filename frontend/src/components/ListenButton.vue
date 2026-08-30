<template>
  <div class="listen-button-container">
    <!-- Animated Radar Waves when in Listening Mode -->
    <div v-if="isListening" class="radar-aura" aria-hidden="true">
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
      <div class="wave wave-3"></div>
    </div>

    <!-- Main Pill Button (Snappy & Fast Transitions) -->
    <button 
      class="master-listen-button"
      :class="{ 
        'is-listening': isListening,
        'is-matching': isMatching 
      }"
      @click="handleToggle"
      :aria-label="isListening ? 'Stop listening to verse' : 'Start speaking verse'"
    >
      <!-- Background Ambient Glow Layer -->
      <div class="btn-ambient-glow"></div>

      <!-- State 1: Idle / Speak State -->
      <div v-if="!isListening && !isMatching" class="btn-content idle-state">
        <div class="mic-icon-circle">
          <svg class="mic-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" x2="12" y1="19" y2="22" />
          </svg>
        </div>

        <div class="btn-text-group">
          <span class="btn-primary-label">Tap to Speak</span>
          <span class="btn-sub-label">Say any Bible verse</span>
        </div>

        <div class="keyboard-badge" title="Press Spacebar to speak">
          <span class="key-tag">Space</span>
        </div>
      </div>

      <!-- State 2: Active Listening State -->
      <div v-else-if="isListening" class="btn-content listening-state">
        <div class="live-dot-wrapper">
          <span class="live-recording-dot"></span>
        </div>

        <div class="btn-text-group">
          <span class="btn-primary-label listening-title">Listening...</span>
          <span class="btn-sub-label live-prompt">Tap button to finish</span>
        </div>

        <!-- Equalizer Sound Frequency Bars -->
        <div class="audio-equalizer-bars">
          <span 
            v-for="(bar, i) in 5" 
            :key="i" 
            class="eq-bar" 
            :style="{ 
              '--bar-scale': getBarHeight(i),
              '--anim-delay': `${i * 0.1}s`
            }"
          ></span>
        </div>
      </div>

      <!-- State 3: Matching State -->
      <div v-else class="btn-content matching-state">
        <div class="spinner-ring"></div>
        <div class="btn-text-group">
          <span class="btn-primary-label">Matching scripture...</span>
          <span class="btn-sub-label">Searching local FTS5</span>
        </div>
      </div>
    </button>

    <!-- Sub-Helper Text beneath Button -->
    <div class="button-footer-helper">
      <p v-if="!isListening && !isMatching" class="helper-text">
        <span class="sparkle-icon">✦</span>
        Works with partial quotes, full passages, or translations
      </p>
      <p v-else-if="isListening" class="helper-text active-prompt">
        <span class="pulse-text-icon">●</span>
        Listening to your microphone... speak your verse now
      </p>
      <p v-else class="helper-text">
        Running trigram search against local Bible database...
      </p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  isListening: {
    type: Boolean,
    default: false
  },
  isMatching: {
    type: Boolean,
    default: false
  },
  audioLevel: {
    type: Number,
    default: 0.3
  }
})

const emit = defineEmits(['toggle-listen'])

function handleToggle() {
  emit('toggle-listen')
}

function getBarHeight(index) {
  if (!props.isListening) return 0.25
  const base = Math.max(0.35, props.audioLevel)
  const multipliers = [0.85, 1.45, 1.75, 1.35, 0.95]
  const variation = (index % 2 === 0 ? 1 : 0.85)
  const scale = Math.min(1.8, Math.max(0.25, base * multipliers[index] * variation))
  return scale.toFixed(2)
}
</script>

<style scoped>
.listen-button-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 2.2rem 0 1.4rem;
}

/* Radar Wave Aura */
.radar-aura {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 140px;
  height: 140px;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 1;
}

.wave {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-pill);
  border: 1.5px solid rgba(217, 70, 239, 0.5);
  background: radial-gradient(circle, rgba(240, 215, 255, 0.4) 0%, rgba(228, 228, 208, 0) 70%);
}

.wave-1 {
  animation: radarWave1 2.2s cubic-bezier(0.1, 0.7, 0.4, 1) infinite;
}

.wave-2 {
  animation: radarWave2 2.2s cubic-bezier(0.1, 0.7, 0.4, 1) infinite 0.6s;
}

.wave-3 {
  animation: radarWave3 2.2s cubic-bezier(0.1, 0.7, 0.4, 1) infinite 1.2s;
}

/* Master Pill Button (Fast 0.15s transition) */
.master-listen-button {
  position: relative;
  z-index: 5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 340px;
  height: 84px;
  padding: 0.65rem 2rem;
  background-color: var(--color-accent);
  color: var(--color-text-primary);
  border-radius: var(--radius-pill);
  border: 1px solid rgba(26, 26, 26, 0.08);
  box-shadow: var(--shadow-button-idle);
  transition: background-color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
  overflow: hidden;
  user-select: none;
}

.master-listen-button:hover {
  transform: translateY(-2px) scale(1.025);
  background-color: #dedec8;
  box-shadow: 0 12px 32px -4px rgba(26, 26, 26, 0.14), 0 0 0 1px rgba(26, 26, 26, 0.12);
}

.master-listen-button:active {
  transform: translateY(1px) scale(0.98);
}

/* Listening Mode Button Visuals */
.master-listen-button.is-listening {
  background-color: #FFFFFF;
  border-color: rgba(217, 70, 239, 0.5);
  box-shadow: var(--shadow-glow-active);
  transform: scale(1.04);
}

.master-listen-button.is-matching {
  background-color: #FAF9EB;
  border-color: rgba(228, 228, 208, 0.9);
}

.btn-ambient-glow {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-pill);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(240, 215, 255, 0) 100%);
  pointer-events: none;
}

/* Button Internal Content */
.btn-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  width: 100%;
}

.mic-icon-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary);
  box-shadow: 0 3px 10px rgba(26, 26, 26, 0.08);
  transition: transform 0.2s ease;
}

.master-listen-button:hover .mic-icon-circle {
  transform: scale(1.08) rotate(4deg);
}

.mic-icon {
  width: 25px;
  height: 25px;
}

.btn-text-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  flex: 1;
}

.btn-primary-label {
  font-family: var(--font-heading);
  font-size: 1.55rem;
  font-weight: 600;
  line-height: 1.1;
  color: var(--color-text-primary);
}

.btn-sub-label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  letter-spacing: 0.02em;
}

.keyboard-badge {
  display: flex;
  align-items: center;
  padding: 0.3rem 0.75rem;
  border-radius: 8px;
  background: rgba(26, 26, 26, 0.06);
  border: 1px solid rgba(26, 26, 26, 0.1);
}

.key-tag {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-text-muted);
  letter-spacing: 0.04em;
}

/* Active State Elements */
.live-dot-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(240, 215, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.live-recording-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #D946EF;
  box-shadow: 0 0 14px #D946EF;
  animation: pulseGlow 1.2s infinite;
}

.listening-title {
  color: #1A1A1A;
}

.live-prompt {
  color: #D946EF;
  font-weight: 600;
}

/* Audio Equalizer Bars */
.audio-equalizer-bars {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  padding: 0 0.5rem;
}

.eq-bar {
  width: 4px;
  height: 28px;
  background: #D946EF;
  border-radius: 4px;
  transform-origin: bottom;
  transform: scaleY(var(--bar-scale, 0.4));
  transition: transform 0.08s ease-out;
  animation: audioBarBounce 0.8s ease-in-out infinite alternate var(--anim-delay, 0s);
}

/* Spinner for matching state */
.spinner-ring {
  width: 36px;
  height: 36px;
  border: 3.5px solid rgba(26, 26, 26, 0.1);
  border-top-color: var(--color-text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Footer Helper */
.button-footer-helper {
  margin-top: 1rem;
  text-align: center;
}

.helper-text {
  font-size: 0.88rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
}

.sparkle-icon {
  color: #9C27B0;
  font-size: 0.85rem;
}

.pulse-text-icon {
  color: #D946EF;
  animation: pulseGlow 1s infinite;
}

.active-prompt {
  color: #83279B;
  font-weight: 500;
}

@media (max-width: 480px) {
  .master-listen-button {
    min-width: 290px;
    height: 76px;
    padding: 0.5rem 1.4rem;
  }
  .btn-primary-label {
    font-size: 1.35rem;
  }
}
</style>
