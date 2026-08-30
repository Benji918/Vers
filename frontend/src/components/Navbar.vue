<template>
  <header class="navbar-wrapper">
    <nav class="navbar-container">
      <!-- Brand / Logo -->
      <a href="/" class="brand-link" title="Vers — Shazam for Bible Verses">
        <div class="brand-icon-wrapper">
          <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-0.5-.05" />
            <path d="M6 6h10" />
            <path d="M6 10h10" />
            <path d="M6 14h6" />
          </svg>
        </div>
        <div class="brand-meta">
          <span class="brand-name">Vers</span>
          <span class="brand-tagline">Scripture by Voice</span>
        </div>
      </a>

      <!-- Center Status / Mode Pill -->
      <div class="mode-status-pill">
        <span class="status-dot" :class="{ 'is-active': isListening }"></span>
        <span class="status-label">
          {{ isListening ? 'Listening Mode Active' : 'Voice Engine Ready' }}
        </span>
      </div>

      <!-- Right Navigation Actions -->
      <div class="navbar-actions">
        <button 
          class="nav-pill-btn" 
          @click="$emit('open-architecture')"
          title="View how Vers matches verses without LLMs"
        >
          <span class="nav-pill-text">How It Works</span>
        </button>

        <a 
          href="https://github.com" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="nav-icon-link"
          title="View Source on GitHub"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
          </svg>
        </a>
      </div>
    </nav>
  </header>
</template>

<script setup>
defineProps({
  isListening: {
    type: Boolean,
    default: false
  }
})

defineEmits(['open-architecture'])
</script>

<style scoped>
.navbar-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 1.25rem 2rem;
  display: flex;
  justify-content: center;
  pointer-events: none;
}

.navbar-container {
  pointer-events: auto;
  width: 100%;
  max-width: 1120px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1.2rem;
  background: var(--color-surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-pill);
  box-shadow: var(--shadow-soft);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: var(--color-text-primary);
}

.brand-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary);
  box-shadow: 0 2px 6px rgba(26, 26, 26, 0.06);
  transition: transform 0.2s ease;
}

.brand-link:hover .brand-icon-wrapper {
  transform: scale(1.06) rotate(-2deg);
}

.brand-icon {
  width: 18px;
  height: 18px;
}

.brand-meta {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-family: var(--font-heading);
  font-size: 1.35rem;
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

.brand-tagline {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.mode-status-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-pill);
  background: rgba(26, 26, 26, 0.03);
  border: 1px solid var(--color-border);
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #8BC34A;
  transition: all 0.3s ease;
}

.status-dot.is-active {
  background: #D946EF;
  box-shadow: 0 0 8px #D946EF;
  animation: pulseGlow 1.5s infinite;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-pill-btn {
  padding: 0.45rem 1rem;
  border-radius: var(--radius-pill);
  background: var(--color-accent);
  color: var(--color-text-primary);
  font-size: 0.84rem;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.nav-pill-btn:hover {
  background: #dbdbc5;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(26, 26, 26, 0.06);
}

.nav-icon-link {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  text-decoration: none;
  background: rgba(26, 26, 26, 0.03);
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
}

.nav-icon-link:hover {
  color: var(--color-text-primary);
  background: rgba(26, 26, 26, 0.06);
  transform: scale(1.05);
}

@media (max-width: 640px) {
  .navbar-wrapper {
    padding: 0.75rem 1rem;
  }
  .mode-status-pill {
    display: none;
  }
  .brand-tagline {
    display: none;
  }
}
</style>
