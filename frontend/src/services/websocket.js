/**
 * WebSocket Audio Streaming & Verse Matching Service
 * Connects frontend mic audio to the FastAPI backend at /ws/listen.
 * Sample prompts are fetched dynamically from the backend (no hardcoded Bible data).
 */

const API_BASE = `http://${window.location.hostname}:9000`
const WS_URL = `ws://${window.location.hostname}:9000/ws/listen`

export async function fetchSampleVerses(n = 6) {
  try {
    const res = await fetch(`${API_BASE}/api/samples?n=${n}`)
    if (!res.ok) throw new Error(`Request failed: ${res.status}`)
    const data = await res.json()
    return Array.isArray(data.samples) ? data.samples : []
  } catch (e) {
    console.warn('Failed to load sample verses from backend:', e)
    return []
  }
}

export class AudioWebSocketService {
  constructor(options = {}) {
    this.wsUrl = options.wsUrl || WS_URL
    this.socket = null
    this.audioContext = null
    this.mediaStream = null
    this.analyser = null
    this.processorNode = null
    this._silentGain = null
    this.accumulatedText = ''
    this.isListening = false
    this.onStatusChange = options.onStatusChange || (() => {})
    this.onTranscript = options.onTranscript || (() => {})
    this.onVerseMatch = options.onVerseMatch || (() => {})
    this.onAudioLevel = options.onAudioLevel || (() => {})
    this.onError = options.onError || (() => {})
    this.animationFrameId = null
  }

  async startListening() {
    if (this.isListening) return

    this.isListening = true
    this.accumulatedText = ''
    this.onStatusChange({ state: 'listening', message: 'Listening... speak your verse now' })
    this._simulateAudioLevel()

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      }).then((stream) => {
        if (!this.isListening) {
          stream.getTracks().forEach(t => t.stop())
          return
        }
        this.mediaStream = stream
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 })
        const source = this.audioContext.createMediaStreamSource(this.mediaStream)
        this.analyser = this.audioContext.createAnalyser()
        this.analyser.fftSize = 128
        source.connect(this.analyser)

        this.processorNode = this.audioContext.createScriptProcessor(4096, 1, 1)
        source.connect(this.processorNode)
        this._silentGain = this.audioContext.createGain()
        this._silentGain.gain.value = 0
        this.processorNode.connect(this._silentGain)
        this._silentGain.connect(this.audioContext.destination)
        this.processorNode.onaudioprocess = this._handleAudioProcess

        if (this.animationFrameId) cancelAnimationFrame(this.animationFrameId)
        this._trackAudioLevel()
      }).catch((err) => {
        this.onError({ message: 'Microphone access denied', detail: err.message })
      })
    } else {
      this.onError({ message: 'Microphone not supported in this browser' })
    }

    try {
      this.socket = new WebSocket(this.wsUrl)
      this.socket.binaryType = 'arraybuffer'

      this.socket.onopen = () => {
        this.onStatusChange({ state: 'listening', message: 'Connected to live voice backend' })
      }

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'transcript') {
            this._accumulateTranscript(data.text, data.is_final)
            this.onTranscript(data.text, data.is_final)
          } else if (data.type === 'match') {
            this.onVerseMatch(data)
            this.stopListening()
          } else if (data.type === 'no_match') {
            this.onError(data)
            this.stopListening()
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message', e)
        }
      }

      this.socket.onerror = () => {
        this.onStatusChange({ state: 'listening', message: 'Backend connection lost' })
      }

      this.socket.onclose = () => {
        if (this.isListening) {
          this.onStatusChange({ state: 'idle', message: 'Backend unavailable' })
        }
      }
    } catch (e) {
      this.onError(e)
    }
  }

  async sendTextQuery(text) {
    if (!text) return
    this.isListening = true
    this.onStatusChange({ state: 'matching', message: 'Matching against Bible database...' })

    const send = () => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ type: 'text_query', text }))
      } else {
        this.onError({ message: 'Backend not connected, cannot process query' })
      }
    }

    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this.socket = new WebSocket(this.wsUrl)
      this.socket.binaryType = 'arraybuffer'
      this.socket.onopen = send
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'match') {
            this.onVerseMatch(data)
            this.stopListening()
          } else if (data.type === 'no_match') {
            this.onError(data)
            this.stopListening()
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message', e)
        }
      }
      this.socket.onerror = () => this.onError({ message: 'Backend not connected' })
    } else {
      send()
    }
  }

  _accumulateTranscript(text, isFinal) {
    if (!text || !isFinal) return
    const cleaned = text.trim()
    if (!cleaned) return

    if (!this.accumulatedText) {
      this.accumulatedText = cleaned
      return
    }

    const current = this.accumulatedText.replace(/\s+$/, '')

    // Case 1: within-utterance cumulative growth — new text starts with what we have.
    if (cleaned.startsWith(current)) {
      this.accumulatedText = cleaned
      return
    }

    // Case 2: cross-utterance, the tail of current repeats at the head of cleaned.
    const overlap = this._overlapWords(current, cleaned)
    if (overlap >= 2) {
      const tail = cleaned.split(' ').slice(overlap).join(' ')
      this.accumulatedText = tail ? `${current} ${tail}` : current
      return
    }

    // Case 3: distinct chunks, just concatenate.
    this.accumulatedText = `${current} ${cleaned}`
  }

  _overlapWords(current, next) {
    const a = current.split(' ')
    const b = next.split(' ')
    let overlap = 0
    const max = Math.min(a.length, b.length)
    for (let len = max; len >= 1; len--) {
      if (a.slice(-len).join(' ') === b.slice(0, len).join(' ')) {
        overlap = len
        break
      }
    }
    return overlap
  }

  finalize() {
    const text = this.accumulatedText.trim()
    if (!text) return
    this._stopCapture()
    this.sendTextQuery(text)
  }

  _trackAudioLevel() {
    if (!this.analyser) return
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount)

    const update = () => {
      if (!this.isListening) return
      this.analyser.getByteFrequencyData(dataArray)
      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i]
      }
      const avg = sum / dataArray.length
      const normalized = Math.min(1, avg / 70)
      this.onAudioLevel(Math.max(0.15, normalized))
      this.animationFrameId = requestAnimationFrame(update)
    }

    update()
  }

  _handleAudioProcess = (event) => {
    if (!this.isListening) return
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return

    const input = event.inputBuffer.getChannelData(0)
    const targetRate = 16000
    const sourceRate = this.audioContext ? this.audioContext.sampleRate : targetRate
    const pcm = this._encodeLinear16(input, sourceRate, targetRate)
    if (pcm && pcm.byteLength > 0 && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(pcm)
    }
  }

  _encodeLinear16(input, sourceRate, targetRate) {
    if (!input || input.length === 0) return null

    let samples = input
    if (sourceRate !== targetRate && sourceRate > 0) {
      const ratio = sourceRate / targetRate
      const outLength = Math.max(1, Math.floor(input.length / ratio))
      samples = new Float32Array(outLength)
      for (let i = 0; i < outLength; i++) {
        const idx = Math.min(input.length - 1, Math.floor(i * ratio))
        samples[i] = input[idx]
      }
    }

    const pcm = new Int16Array(samples.length)
    for (let i = 0; i < samples.length; i++) {
      const s = Math.max(-1, Math.min(1, samples[i]))
      pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff
    }
    return pcm.buffer
  }

  _simulateAudioLevel() {
    const update = () => {
      if (!this.isListening) return
      const time = Date.now() / 160
      const level = 0.4 + Math.sin(time) * 0.25 + Math.sin(time * 2.1) * 0.15 + Math.random() * 0.12
      this.onAudioLevel(Math.max(0.2, Math.min(1, level)))
      this.animationFrameId = requestAnimationFrame(update)
    }
    update()
  }

  _stopCapture() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }

    if (this.processorNode) {
      try {
        this.processorNode.disconnect()
      } catch (e) {}
      this.processorNode.onaudioprocess = null
      this.processorNode = null
    }

    if (this._silentGain) {
      try {
        this._silentGain.disconnect()
      } catch (e) {}
      this._silentGain = null
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop())
      this.mediaStream = null
    }

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close().catch(() => {})
      this.audioContext = null
    }
    this.analyser = null
  }

  stopListening() {
    this.isListening = false
    this.accumulatedText = ''
    this._stopCapture()

    if (this.socket) {
      try {
        this.socket.close()
      } catch (e) {}
      this.socket = null
    }

    this.onStatusChange({ state: 'idle', message: 'Tap to speak' })
    this.onAudioLevel(0)
  }
}
