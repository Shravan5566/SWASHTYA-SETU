/**
 * qr_scanner.js — Official Html5QrcodeScanner Integration
 * Uses the proven Html5QrcodeScanner engine for 100% camera compatibility across laptops,
 * webcams, and mobile devices.
 */

(function () {
  const statusEl = document.getElementById("qr-status");
  const manualInput = document.getElementById("manual-card-id");
  const manualBtn = document.getElementById("manual-submit-btn");
  let scannerInstance = null;

  function setStatus(msg, isError = false) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.className = "qr-status " + (isError ? "qr-status--error" : "qr-status--info");
  }

  async function submitCardId(cardId) {
    if (!cardId) return;
    const cleanId = cardId.trim();
    setStatus(`Card identified: ${cleanId}. Requesting OTP…`);

    try {
      const resp = await fetch("/ajax/scan-card", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ card_id: cleanId }),
      });
      const data = await resp.json();

      if (data.ok) {
        setStatus("Patient card verified! Opening OTP verification…");
        if (scannerInstance) {
          try {
            await scannerInstance.clear();
          } catch (e) {}
        }
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

  // Global helper for 1-click quick-select demo buttons
  window.quickSelectPatient = submitCardId;

  function onScanSuccess(decodedText) {
    if (!decodedText) return;
    console.log("QR Code Decoded:", decodedText);
    submitCardId(decodedText);
  }

  function onScanError(errorMessage) {
    // Normal frame-by-frame non-match while searching; do not spam
  }

  function initScanner() {
    const readerEl = document.getElementById("reader");
    if (!readerEl) return;

    if (typeof Html5QrcodeScanner === "undefined") {
      setStatus("QR Scanner library loading or unavailable. Use 1-click buttons or manual entry.", true);
      return;
    }

    try {
      scannerInstance = new Html5QrcodeScanner(
        "reader",
        {
          fps: 15,
          qrbox: { width: 250, height: 250 },
          rememberLastUsedCamera: true,
          aspectRatio: 1.25,
          showTorchButtonIfSupported: true,
          showZoomSliderIfSupported: true,
        },
        /* verbose= */ false
      );

      scannerInstance.render(onScanSuccess, onScanError);
      setStatus("Point your webcam at the QR code, or click 'Request Camera Permissions' if prompted.");
    } catch (e) {
      console.error("Scanner init error:", e);
      setStatus("Could not initialize camera scanner: " + e.message, true);
    }
  }

  // Manual Card ID entry
  if (manualBtn) {
    manualBtn.addEventListener("click", () => {
      const cardId = manualInput ? manualInput.value.trim() : "";
      if (!cardId) {
        setStatus("Please enter a card ID (e.g. SS-TEST-001).", true);
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

  window.addEventListener("DOMContentLoaded", initScanner);
})();
