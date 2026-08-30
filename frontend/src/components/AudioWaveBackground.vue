<template>
  <div class="wave-bg-canvas-container" aria-hidden="true">
    <canvas ref="canvasRef" class="wave-canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  isListening: {
    type: Boolean,
    default: false
  },
  audioLevel: {
    type: Number,
    default: 0
  }
})

const canvasRef = ref(null)
let ctx = null
let animationId = null
let step = 0

function resizeCanvas() {
  if (!canvasRef.value) return
  canvasRef.value.width = window.innerWidth
  canvasRef.value.height = window.innerHeight
}

function drawWave() {
  if (!ctx || !canvasRef.value) return
  const width = canvasRef.value.width
  const height = canvasRef.value.height

  ctx.clearRect(0, 0, width, height)

  const isListen = props.isListening
  const level = props.audioLevel || 0

  // Multi-layered organic sine waves
  const waveConfigs = [
    {
      color: 'rgba(240, 215, 255, 0.42)',
      amplitude: isListen ? 45 + level * 65 : 20,
      frequency: 0.0028,
      speed: isListen ? 0.035 : 0.012,
      baseY: height * 0.72
    },
    {
      color: 'rgba(228, 228, 208, 0.48)',
      amplitude: isListen ? 38 + level * 50 : 16,
      frequency: 0.0035,
      speed: isListen ? -0.028 : -0.009,
      baseY: height * 0.76
    },
    {
      color: 'rgba(240, 215, 255, 0.25)',
      amplitude: isListen ? 55 + level * 80 : 25,
      frequency: 0.002,
      speed: isListen ? 0.02 : 0.007,
      baseY: height * 0.82
    }
  ]

  step += 1

  waveConfigs.forEach(wave => {
    ctx.beginPath()
    ctx.moveTo(0, height)

    for (let x = 0; x <= width; x += 6) {
      const y = Math.sin(x * wave.frequency + step * wave.speed) * wave.amplitude + wave.baseY
      ctx.lineTo(x, y)
    }

    ctx.lineTo(width, height)
    ctx.closePath()
    ctx.fillStyle = wave.color
    ctx.fill()
  })

  animationId = requestAnimationFrame(drawWave)
}

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d')
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    drawWave()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCanvas)
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.wave-bg-canvas-container {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.wave-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
