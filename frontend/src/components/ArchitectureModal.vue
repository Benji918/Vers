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
          <strong>"Shazam for Bible verses."</strong> Speak a verse aloud, and Vers identifies the exact book, chapter, and verse in real time, with no LLMs or vector embeddings involved in the matching.
        </p>

        <!-- Pipeline Steps with Bigger Readable Typography -->
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
            <p class="step-desc">Classic full-text search queries local Bible DB to shortlist candidate verse candidates.</p>
          </div>

          <div class="step-card">
            <div class="step-num">04</div>
            <h4 class="step-title">Trigram Ranking</h4>
            <p class="step-desc">Fuzzy trigram matching scores and ranks the shortlist to return the exact book, chapter, and verse.</p>
          </div>
        </div>

        <div class="principles-banner">
          <div class="principle-item">
            <strong class="principle-title">✓ Zero Network API Latency</strong>
            <span class="principle-desc">Local SQLite/PostgreSQL database eliminates third-party database network hops.</span>
          </div>
          <div class="principle-item">
            <strong class="principle-title">✓ 100% Deterministic & Explainable</strong>
            <span class="principle-desc">Pure text search and trigram algorithms with no hallucinations.</span>
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
  background: rgba(26, 26, 26, 0.45);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
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
  max-width: 740px;
  background: #FFFFF4;
  border-radius: var(--radius-card);
  border: 1px solid var(--color-border-accent);
  box-shadow: 0 24px 60px rgba(26, 26, 26, 0.18);
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
  padding: 2rem 2.25rem 1.25rem;
}

.eyebrow-badge {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9C27B0;
  display: block;
  margin-bottom: 0.35rem;
}

.modal-title {
  font-family: var(--font-heading);
  font-size: 2.1rem;
  font-weight: 600;
  line-height: 1.1;
  color: var(--color-text-primary);
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(26, 26, 26, 0.06);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(26, 26, 26, 0.12);
  color: var(--color-text-primary);
}

.modal-content {
  padding: 0 2.25rem 1.5rem;
}

.summary-lead {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 1.6rem;
}

.summary-lead strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.step-card {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(26, 26, 26, 0.03);
}

.step-num {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 700;
  color: #9C27B0;
  margin-bottom: 0.35rem;
}

.step-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
  color: var(--color-text-primary);
}

.step-desc {
  font-size: 0.92rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.principles-banner {
  background: rgba(240, 215, 255, 0.45);
  border: 1px solid rgba(217, 70, 239, 0.2);
  border-radius: 14px;
  padding: 1.2rem 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.principle-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.principle-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.principle-desc {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.45;
}

.modal-footer {
  padding: 1rem 2.25rem 2rem;
  display: flex;
  justify-content: flex-end;
}

.primary-btn {
  padding: 0.65rem 1.75rem;
  border-radius: var(--radius-pill);
  background: var(--color-text-primary);
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.primary-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(26, 26, 26, 0.15);
}

@media (max-width: 640px) {
  .modal-backdrop {
    padding: 0;
    align-items: stretch;
  }

  .modal-card {
    max-height: 85vh;
    height: 85vh;
    border-radius: var(--radius-card);
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    padding: 0.75rem 1rem 0.5rem;
    flex-shrink: 0;
    text-align: center;
  }

  .eyebrow-badge {
    font-size: 0.6rem;
    margin-bottom: 0.15rem;
  }

  .modal-title {
    font-size: 1.1rem;
  }

  .close-btn {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }

  .modal-content {
    padding: 0 1rem;
    flex: 1;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .summary-lead {
    font-size: 0.85rem;
    line-height: 1.4;
    margin-bottom: 0.7rem;
    text-align: center;
    max-width: 95%;
  }

  .pipeline-grid {
    grid-template-columns: 1fr;
    gap: 0.45rem;
    margin-bottom: 0.6rem;
    width: 100%;
  }

  .step-card {
    padding: 0.55rem 0.7rem;
  }

  .step-num {
    font-size: 0.8rem;
    margin-bottom: 0.05rem;
  }

  .step-title {
    font-size: 0.8rem;
    margin-bottom: 0.1rem;
  }

  .step-desc {
    font-size: 0.73rem;
    line-height: 1.3;
  }

  .principles-banner {
    padding: 0.55rem 0.7rem;
    gap: 0.35rem;
    margin-bottom: 0.6rem;
    width: 100%;
  }

  .principle-title {
    font-size: 0.75rem;
  }

  .principle-desc {
    font-size: 0.7rem;
    line-height: 1.25;
  }

  .modal-footer {
    padding: 0.6rem 1rem;
    flex-shrink: 0;
    border-top: 1px solid var(--color-border);
    background: #FFFFF4;
  }

  .primary-btn {
    padding: 0.55rem 1.5rem;
    font-size: 0.85rem;
  }
}
</style>
