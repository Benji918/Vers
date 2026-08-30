<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <div class="header-titles">
          <span class="eyebrow-badge">Architecture & Engine</span>
          <h2 class="modal-title">How Vers Works</h2>
        </div>
        <button class="close-btn" @click="$emit('close')" aria-label="Close modal">
          ✕
        </button>
      </div>

      <div class="modal-content">
        <p class="summary-lead">
          <strong>"Shazam for Bible verses."</strong> Speak a verse aloud, and Vers identifies the exact book, chapter, and verse in real-time — with no LLM or vector embeddings involved in the matching.
        </p>

        <!-- Pipeline Steps -->
        <div class="pipeline-grid">
          <div class="step-card">
            <div class="step-num">01</div>
            <h4 class="step-title">Voice Streaming</h4>
            <p class="step-desc">Microphone audio captures at 16kHz and streams over WebSocket directly to the FastAPI server.</p>
          </div>

          <div class="step-card">
            <div class="step-num">02</div>
            <h4 class="step-title">Deepgram Nova-3</h4>
            <p class="step-desc">Server relays raw audio chunks to Deepgram streaming STT, returning instant transcript events.</p>
          </div>

          <div class="step-card">
            <div class="step-num">03</div>
            <h4 class="step-title">FTS5 Shortlist</h4>
            <p class="step-desc">Classic full-text search queries local Bible DB to shortlist matching candidate verse candidates.</p>
          </div>

          <div class="step-card">
            <div class="step-num">04</div>
            <h4 class="step-title">Trigram Ranking</h4>
            <p class="step-desc">Fuzzy trigram matching scores and ranks the shortlist to return the exact book, chapter, and verse.</p>
          </div>
        </div>

        <div class="principles-banner">
          <div class="principle-item">
            <strong>✓ Zero Latency Overhead</strong>
            <span>Local SQLite/PostgreSQL database eliminates third-party API hops</span>
          </div>
          <div class="principle-item">
            <strong>✓ Deterministic & Explainable</strong>
            <span>Pure text matching algorithms instead of hallucinations</span>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="primary-btn" @click="$emit('close')">Got It</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(26, 26, 26, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  animation: fadeIn 0.25s ease forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  width: 100%;
  max-width: 680px;
  background: #FFFFF2;
  border-radius: var(--radius-card);
  border: 1px solid var(--color-border-accent);
  box-shadow: 0 24px 60px rgba(26, 26, 26, 0.15);
  overflow: hidden;
  animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes scaleUp {
  from { transform: scale(0.95) translateY(10px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.75rem 2rem 1rem;
}

.eyebrow-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #9C27B0;
  display: block;
  margin-bottom: 0.25rem;
}

.modal-title {
  font-size: 1.75rem;
  font-weight: 600;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(26, 26, 26, 0.05);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(26, 26, 26, 0.1);
  color: var(--color-text-primary);
}

.modal-content {
  padding: 0 2rem 1.5rem;
}

.summary-lead {
  font-size: 0.96rem;
  color: var(--color-text-secondary);
  line-height: 1.55;
  margin-bottom: 1.5rem;
}

.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}

.step-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
}

.step-num {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 700;
  color: #9C27B0;
  margin-bottom: 0.25rem;
}

.step-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.step-desc {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.principles-banner {
  background: rgba(240, 215, 255, 0.4);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.principle-item {
  display: flex;
  flex-direction: column;
  font-size: 0.82rem;
  color: var(--color-text-primary);
}

.principle-item span {
  color: var(--color-text-secondary);
}

.modal-footer {
  padding: 1rem 2rem 1.75rem;
  display: flex;
  justify-content: flex-end;
}

.primary-btn {
  padding: 0.55rem 1.5rem;
  border-radius: var(--radius-pill);
  background: var(--color-text-primary);
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.88rem;
  transition: all 0.2s ease;
}

.primary-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

@media (max-width: 600px) {
  .pipeline-grid {
    grid-template-columns: 1fr;
  }
}
</style>
