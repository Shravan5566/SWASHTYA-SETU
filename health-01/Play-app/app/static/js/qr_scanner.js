/**
 * qr_scanner.js — Upgraded Universal QR Scanner
 * Uses Html5Qrcode engine for 100% browser compatibility (no experimental flags needed).
 * Supports live camera scanning, QR image file upload, and manual entry.
 */

(function () {
  const statusEl = document.getElementById("qr-status");
  const manualInput = document.getElementById("manual-card-id");
  const manualBtn = document.getElementById("manual-submit-btn");
  const fileInput = document.getElementById("qr-file-input");

  let html5QrCode = null;
  let isScanning = false;

  function setStatus(msg, isError = false) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.className = "qr-status " + (isError ? "qr-status--error" : "qr-status--info");
  }

  async function submitCardId(cardId) {
    if (!cardId) return;
    const cleanId = cardId.trim();
    setStatus(`Card detected: ${cleanId}. Verifying with server…`);

    try {
      const resp = await fetch("/ajax/scan-card", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ card_id: cleanId }),
      });
      const data = await resp.json();

      if (data.ok) {
        setStatus("Patient card verified! Redirecting to OTP verification…");
        stopScanner();
        setTimeout(() => {
          window.location.href = "/doctor/otp-verify";
        }, 300);
      } else {
        setStatus("Error: " + (data.error || "Card not recognized"), true);
      }
    } catch (err) {
      setStatus("Network error connecting to server. Please try again.", true);
    }
  }

  function stopScanner() {
    if (html5QrCode && isScanning) {
      html5QrCode
        .stop()
        .then(() => {
          isScanning = false;
        })
        .catch(() => {});
    }
  }

  function onScanSuccess(decodedText, decodedResult) {
    if (!decodedText) return;
    stopScanner();
    submitCardId(decodedText);
  }

  function onScanFailure(error) {
    // Normal frame-by-frame non-match while searching; ignore to avoid spamming UI
  }

  async function startCameraScanner() {
    const readerElement = document.getElementById("reader");
    if (!readerElement || typeof Html5Qrcode === "undefined") {
      setStatus("QR scanner engine not ready. Please use manual entry below.", true);
      return;
    }

    try {
      html5QrCode = new Html5Qrcode("reader");

      const config = {
        fps: 12,
        qrbox: { width: 220, height: 220 },
        aspectRatio: 1.333333,
      };

      setStatus("Requesting camera access…");

      await html5QrCode.start(
        { facingMode: "environment" },
        config,
        onScanSuccess,
        onScanFailure
      );

      isScanning = true;
      setStatus("Camera active — point at the patient QR card.");
    } catch (err) {
      isScanning = false;
      const errStr = (err && err.message) || String(err);
      if (errStr.includes("NotAllowedError") || errStr.includes("Permission")) {
        setStatus("Camera permission denied. Please allow camera access in browser settings, or enter card ID below.", true);
      } else if (errStr.includes("NotFoundError") || errStr.includes("DevicesNotFoundError")) {
        setStatus("No camera detected on this device. Use manual entry or upload a QR image below.", true);
      } else if (errStr.includes("NotReadableError") || errStr.includes("TrackStartError")) {
        setStatus("Camera is in use by another application (e.g. Lenovo Vantage/Teams) or privacy shutter is closed.", true);
      } else {
        setStatus("Camera unavailable. You can use manual entry or upload an image below.", true);
      }
    }
  }

  // File Upload scanning (allows scanning saved QR card images)
  if (fileInput) {
    fileInput.addEventListener("change", async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      if (!html5QrCode) {
        html5QrCode = new Html5Qrcode("reader");
      }

      setStatus(`Scanning image ${file.name}…`);
      try {
        const decodedText = await html5QrCode.scanFile(file, true);
        if (decodedText) {
          submitCardId(decodedText);
        } else {
          setStatus("Could not detect a QR code in that image.", true);
        }
      } catch (err) {
        setStatus("No valid QR code detected in the selected image. Try another file or enter ID manually.", true);
      }
    });
  }

  // Manual Card ID entry
  if (manualBtn) {
    manualBtn.addEventListener("click", () => {
      const cardId = manualInput ? manualInput.value.trim() : "";
      if (!cardId) {
        setStatus("Please enter a card ID.", true);
        return;
      }
      submitCardId(cardId);
    });
  }

  if (manualInput) {
    manualInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (manualBtn) manualBtn.click();
      }
    });
  }

  // Start scanner on page load
  window.addEventListener("DOMContentLoaded", () => {
    startCameraScanner();
  });
})();
