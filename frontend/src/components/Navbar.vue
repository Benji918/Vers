<template>
  <header class="navbar-wrapper">
    <nav class="navbar-container">
      <!-- Brand Logo with Combined Book & Microphone Emblem -->
      <a href="/" class="brand-link" title="Vers — Shazam for Bible Verses">
        <div class="brand-icon-wrapper">
          <svg class="brand-icon" viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <!-- Open Bible Base -->
            <path d="M3 6.5C3 5.4 3.9 4.5 5 4.5H13V22.5H5C3.9 22.5 3 21.6 3 20.5V6.5Z" />
            <path d="M25 6.5C25 5.4 24.1 4.5 23 4.5H15V22.5H23C24.1 22.5 25 21.6 25 20.5V6.5Z" />
            <!-- Center Spine -->
            <line x1="14" y1="4.5" x2="14" y2="22.5" />
            <!-- Integrated Microphone Emblem in Center -->
            <rect x="12" y="8" width="4" height="6.5" rx="2" fill="currentColor" />
            <path d="M10 11.5a4 4 0 0 0 8 0" stroke-width="1.5" />
            <line x1="14" y1="15.5" x2="14" y2="18" stroke-width="1.5" />
          </svg>
        </div>
        <div class="brand-meta">
          <span class="brand-name">Vers</span>
        </div>
      </a>

      <!-- Right Navigation Actions -->
      <div class="navbar-actions">
        <button 
          class="nav-pill-btn" 
          @click="$emit('open-architecture')"
          title="View how Vers works"
        >
          <span>How It Works</span>
        </button>

        <a 
          href="https://github.com/Benji918/Vers" 
          target="_blank" 
          rel="noopener noreferrer" 
          class="nav-icon-link"
          title="View Source on GitHub (Benji918/Vers)"
        >
          <svg viewBox="0 0 24 24" width="19" height="19" fill="currentColor">
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
  padding: 1.1rem 1.5rem;
  display: flex;
  justify-content: center;
  pointer-events: none;
}

.navbar-container {
  pointer-events: auto;
  width: 100%;
  max-width: 760px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 1.1rem;
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
  gap: 0.65rem;
  text-decoration: none;
  color: var(--color-text-primary);
}

.brand-icon-wrapper {
  width: 38px;
  height: 38px;
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
  width: 21px;
  height: 21px;
}

.brand-meta {
  display: flex;
  align-items: center;
}

.brand-name {
  font-family: var(--font-heading);
  font-size: 1.45rem;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--color-text-primary);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-pill-btn {
  padding: 0.45rem 1.05rem;
  border-radius: var(--radius-pill);
  background: var(--color-accent);
  color: var(--color-text-primary);
  font-size: 0.88rem;
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
}
</style>
