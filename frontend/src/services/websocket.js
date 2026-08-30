/**
 * WebSocket Audio Streaming & Verse Matching Service
 * Connects frontend mic audio to the FastAPI backend at /ws/listen.
 * Sample prompts are fetched dynamically from the backend (no hardcoded Bible data).
 */

const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws'

const API_BASE = isDev
  ? `http://${window.location.hostname}:9000`
  : `${window.location.protocol}//${window.location.host}`

const WS_URL = isDev
  ? `ws://${window.location.hostname}:9000/ws/listen`
  : `${wsProtocol}://${window.location.host}/ws/listen`

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
    this.silenceTimer = null
    this.autoStopMs = options.autoStopMs || 1500
    this._hadSpeech = false
    this.lastTranscript = ''
  }

  async startListening() {
    if (this.isListening) return

    this.isListening = true
    this.accumulatedText = ''
    this.lastTranscript = ''
    this._hadSpeech = false
    this._clearSilenceTimer()
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
            if (data.text) this.lastTranscript = data.text.trim()
            const accumulated = this._accumulateTranscript(data.text, data.is_final)
            this.onTranscript(this._buildDisplayText(data.text, data.is_final, accumulated))
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
    // Deepgram sends smooth interim results during speech and a clean
    // `speech_final` transcript after each pause (low endpointing). We append
    // those clean finals to build the full passage, de-duplicating any shared
    // boundary words between utterances so sentences join without repetition.
    if (!text) return this.accumulatedText
    const cleaned = text.trim()
    if (!cleaned) return this.accumulatedText

    if (!this.accumulatedText) {
      this.accumulatedText = cleaned
      return this.accumulatedText
    }

    const current = this.accumulatedText.replace(/\s+$/, '')

    // Within-utterance cumulative growth — replace with the longer transcript.
    if (cleaned.startsWith(current)) {
      this.accumulatedText = cleaned
      return this.accumulatedText
    }

    // Cross-utterance: drop the shared tail/head so we don't repeat words.
    const overlap = this._overlapWords(current, cleaned)
    if (overlap >= 2) {
      const tail = cleaned.split(' ').slice(overlap).join(' ')
      this.accumulatedText = tail ? `${current} ${tail}` : current
      return this.accumulatedText
    }

    // Distinct chunk — just concatenate.
    this.accumulatedText = `${current} ${cleaned}`
    return this.accumulatedText
  }

  _buildDisplayText(text, isFinal, accumulated) {
    // Surface the full accumulated passage so prior sentences stay visible.
    let base = (accumulated || '').trim()

    // Also reflect the live words currently being spoken if they aren't yet in
    // the accumulated passage (e.g. during an interim result mid-sentence).
    const partial = (text || '').trim()
    if (partial && !isFinal) {
      base = this._mergePartial(base, partial)
    }
    return base
  }

  _mergePartial(base, partial) {
    const baseWords = base ? base.split(' ') : []
    const partialWords = partial.split(' ')

    if (base.endsWith(partial) || base === partial) return base

    if (baseWords.length > 0 && partialWords.length > 0 && partial.includes(baseWords[0])) {
      const overlap = this._overlapWords(base, partial)
      const tail = partialWords.slice(overlap).join(' ')
      return tail ? `${base} ${tail}` : base
    }

    return base ? `${base} ${partial}` : partial
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
    const text = (this.accumulatedText || this.lastTranscript || '').trim()
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

    let rms = 0
    for (let i = 0; i < input.length; i++) rms += input[i] * input[i]
    rms = Math.sqrt(rms / input.length)

    if (rms > 0.02) {
      this._hadSpeech = true
      this._clearSilenceTimer()
    } else if (this._hadSpeech && !this.silenceTimer) {
      this.silenceTimer = setTimeout(() => this._autoFinalize(), this.autoStopMs)
    }

    if (pcm && pcm.byteLength > 0 && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(pcm)
    }
  }

  _clearSilenceTimer() {
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer)
      this.silenceTimer = null
    }
  }

  _autoFinalize() {
    if (!this.isListening) return
    this._clearSilenceTimer()
    if (this.accumulatedText || this.lastTranscript) {
      this.finalize()
    } else {
      this.stopListening()
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
    this._clearSilenceTimer()
    this._hadSpeech = false

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
    this.lastTranscript = ''
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
