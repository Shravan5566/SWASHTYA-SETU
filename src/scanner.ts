import jsQR from 'jsqr'

export function extractCardId(raw: string): string {
  if (!raw) return ''
  // Support standard SS format (e.g., SS-TEST-001, SS-XXXX-XXXX-XXXX)
  const match = raw.match(/SS-[A-Z0-9-]{3,24}/i)
  return match ? match[0].toUpperCase() : raw.trim().toUpperCase()
}

/**
 * Robustly decodes a QR code from any image file (PNG, JPG, WebP)
 * handles transparency, high-res camera photos, and color inversion.
 */
export function decodeQrFromImageFile(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const objectUrl = URL.createObjectURL(file)
    img.onload = () => {
      URL.revokeObjectURL(objectUrl)
      try {
        // Cap max dimensions to 1200px to maintain crispness and optimize jsQR performance
        const maxDim = 1200
        let w = img.naturalWidth || img.width
        let h = img.naturalHeight || img.height
        if (w > maxDim || h > maxDim) {
          if (w > h) {
            h = Math.round((h * maxDim) / w)
            w = maxDim
          } else {
            w = Math.round((w * maxDim) / h)
            h = maxDim
          }
        }

        const canvas = document.createElement('canvas')
        canvas.width = w
        canvas.height = h
        const ctx = canvas.getContext('2d', { willReadFrequently: true })
        if (!ctx) {
          return reject(new Error('Canvas context not available'))
        }

        // Fill solid white background so transparent PNGs don't blend into black
        ctx.fillStyle = '#FFFFFF'
        ctx.fillRect(0, 0, w, h)
        ctx.drawImage(img, 0, 0, w, h)

        const imgData = ctx.getImageData(0, 0, w, h)
        // First attempt with attemptBoth
        let code = jsQR(imgData.data, imgData.width, imgData.height, {
          inversionAttempts: 'attemptBoth',
        })

        // If not found in full image, try scanning the top 60% (where QR card back is located)
        if (!code) {
          const topH = Math.round(h * 0.6)
          const topData = ctx.getImageData(0, 0, w, topH)
          code = jsQR(topData.data, topData.width, topData.height, {
            inversionAttempts: 'attemptBoth',
          })
        }

        if (code && code.data) {
          resolve(extractCardId(code.data))
        } else {
          reject(new Error('No legible QR code found in uploaded image. Please enter or verify Card ID.'))
        }
      } catch (err: any) {
        reject(err)
      }
    }
    img.onerror = () => {
      URL.revokeObjectURL(objectUrl)
      reject(new Error('Failed to load card image.'))
    }
    img.src = objectUrl
  })
}

/**
 * Scans a video stream frame for a QR code.
 */
export function scanQrFromVideo(video: HTMLVideoElement, canvas: HTMLCanvasElement): string | null {
  if (!video || video.readyState < 2) return null
  const vw = video.videoWidth || 640
  const vh = video.videoHeight || 480
  canvas.width = vw
  canvas.height = vh
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) return null

  ctx.drawImage(video, 0, 0, vw, vh)
  const imgData = ctx.getImageData(0, 0, vw, vh)
  const code = jsQR(imgData.data, imgData.width, imgData.height, {
    inversionAttempts: 'attemptBoth',
  })
  if (code && code.data) {
    return extractCardId(code.data)
  }
  return null
}
