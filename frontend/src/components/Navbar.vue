<template>
  <header class="navbar-wrapper">
    <nav class="navbar-container">
      <!-- Brand Logo: Bible with Microphone at top-right corner (No circle background) -->
      <a href="/" class="brand-link" title="Vers — Scripture by Voice">
        <div class="brand-icon-wrapper">
          <svg class="brand-icon" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Bible Book Body -->
            <rect x="3.5" y="8" width="20" height="23" rx="3" fill="#FFFFFF" stroke="#1A1A1A" stroke-width="2" />
            <!-- Book Spine Accent -->
            <path d="M7 8V31" stroke="#1A1A1A" stroke-width="1.5" opacity="0.4" />
            <!-- Book Spine Ribbon / Bookmark -->
            <path d="M10 8V14L12 12.5L14 14V8" fill="#E4E4D0" stroke="#1A1A1A" stroke-width="1" />
            <!-- Scripture Cross Symbol on Bible Cover -->
            <path d="M12 19V26" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" />
            <path d="M9 21.5H15" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" />
            <!-- Pages Bottom Layer -->
            <path d="M7 28H20" stroke="#1A1A1A" stroke-width="1.2" stroke-dasharray="1.5 2" opacity="0.35" />

            <!-- Microphone Badge at Top-Right Corner -->
            <g class="mic-badge-group">
              <!-- Glow Aura & Circle Background -->
              <circle cx="26" cy="10" r="8.5" fill="#F0D7FF" stroke="#1A1A1A" stroke-width="1.8" />
              <!-- Microphone Capsule -->
              <rect x="24.2" y="5.5" width="3.6" height="5.8" rx="1.8" fill="#1A1A1A" />
              <!-- Microphone Pickup Arc -->
              <path d="M22.5 8.8C22.5 10.7 24.1 12.2 26 12.2C27.9 12.2 29.5 10.7 29.5 8.8" stroke="#1A1A1A" stroke-width="1.4" stroke-linecap="round" />
              <!-- Microphone Stem -->
              <line x1="26" y1="12.2" x2="26" y2="14.2" stroke="#1A1A1A" stroke-width="1.4" stroke-linecap="round" />
              <line x1="24.2" y1="14.2" x2="27.8" y2="14.2" stroke="#1A1A1A" stroke-width="1.4" stroke-linecap="round" />
            </g>
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
  padding: 0.55rem 1.15rem;
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

/* Transparent wrapper with no background circle */
.brand-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  padding: 0;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.brand-link:hover .brand-icon-wrapper {
  transform: scale(1.08) rotate(-3deg);
}

.brand-icon {
  width: 34px;
  height: 34px;
  overflow: visible;
  display: block;
}

.brand-meta {
  display: flex;
  align-items: center;
}

.brand-name {
  font-family: var(--font-heading);
  font-size: 1.6rem;
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
  padding: 0.45rem 1.1rem;
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
  width: 38px;
  height: 38px;
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
