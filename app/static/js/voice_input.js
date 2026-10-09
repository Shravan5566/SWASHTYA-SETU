/**
 * voice_input.js — Speech-to-Text input for Swasthya Setu checkup form
 *
 * Captures speech via the browser's Web Speech API, sends the transcript to
 * /ai/voice-parse, and auto-fills the add_checkup form fields for the doctor to review.
 * Also includes real-time medicine spellcheck via /ai/correct-drug.
 *
 * NOTE: Intentionally separate from tts.js (which handles text-to-speech reading).
 */

(function () {
  let recognition = null;
  let isListening = false;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  function updateStatus(text, type = "info") {
    const statusEl = document.getElementById("voice-status");
    if (!statusEl) return;
    statusEl.textContent = text;
    if (type === "error") {
      statusEl.style.color = "#dc2626";
    } else if (type === "success") {
      statusEl.style.color = "#16a34a";
    } else {
      statusEl.style.color = "#64748b";
    }
  }

  function setButtonState(listening) {
    const btn = document.getElementById("voice-start-btn");
    if (!btn) return;
    if (listening) {
      btn.textContent = "⏹ Stop Listening";
      btn.classList.add("btn-danger");
      btn.classList.remove("btn-outline");
    } else {
      btn.textContent = "🎙 Start";
      btn.classList.remove("btn-danger");
      btn.classList.add("btn-outline");
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Web Speech API Voice Dictation
  // ─────────────────────────────────────────────────────────────────────────
  window.startVoiceInput = function () {
    if (isListening) {
      if (recognition) recognition.stop();
      isListening = false;
      setButtonState(false);
      updateStatus("Processing your dictation…", "info");
      return;
    }

    if (!SpeechRecognition) {
      updateStatus(
        "Web Speech API is not supported in this browser. You can type directly into the form.",
        "error"
      );
      // Fallback: prompt for typed transcript to test AI parsing
      const testPrompt = prompt(
        "Voice input not supported in this browser. You may paste or type a dictation here to test AI parsing:"
      );
      if (testPrompt) {
        sendTranscriptToBackend(testPrompt);
      }
      return;
    }

    try {
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-IN"; // Default to English (India) with fallback to en-US

      recognition.onstart = function () {
        isListening = true;
        setButtonState(true);
        updateStatus("🎙 Listening… Speak now (e.g., 'Ward A, viral fever, Paracetamol 500mg TDS for 5 days')");
      };

      recognition.onresult = function (event) {
        if (event.results && event.results.length > 0) {
          const transcript = event.results[0][0].transcript;
          updateStatus(`Transcribed: "${transcript}". Extracting fields with AI…`, "info");
          sendTranscriptToBackend(transcript);
        }
      };

      recognition.onerror = function (event) {
        console.warn("Speech recognition error:", event.error);
        isListening = false;
        setButtonState(false);
        if (event.error === "not-allowed") {
          updateStatus("Microphone access denied. Please check your browser permissions.", "error");
        } else if (event.error === "no-speech") {
          updateStatus("No speech detected. Please try again.", "info");
        } else {
          updateStatus(`Speech error: ${event.error}`, "error");
        }
      };

      recognition.onend = function () {
        isListening = false;
        setButtonState(false);
      };

      recognition.start();
    } catch (err) {
      console.error("Failed to start speech recognition:", err);
      isListening = false;
      setButtonState(false);
      updateStatus("Could not activate microphone.", "error");
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  // Send Transcript to Backend /ai/voice-parse
  // ─────────────────────────────────────────────────────────────────────────
  function sendTranscriptToBackend(transcript) {
    updateStatus("Parsing with AI…", "info");

    fetch("/ai/voice-parse", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ transcript: transcript }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
      })
      .then((json) => {
        if (!json.success || !json.data) {
          updateStatus("Could not parse prescription. Please review form.", "error");
          return;
        }

        const data = json.data;

        // Auto-fill form fields
        if (data.area) {
          const areaEl = document.getElementById("area");
          if (areaEl) areaEl.value = data.area;
        }

        if (data.condition) {
          const condEl = document.getElementById("condition");
          if (condEl) condEl.value = data.condition;
        }

        if (data.diagnosis_notes) {
          const notesEl = document.getElementById("diagnosis_notes");
          if (notesEl) notesEl.value = data.diagnosis_notes;
        }

        if (data.medicine) {
          const medEl = document.getElementById("medicine");
          if (medEl) medEl.value = data.medicine;
          const firstMed = document.querySelector("input[name='medicine[]']");
          if (firstMed) firstMed.value = data.medicine;
        }

        if (data.dosage) {
          const doseEl = document.getElementById("dosage");
          if (doseEl) doseEl.value = data.dosage;
          const firstDose = document.querySelector("input[name='dosage[]']");
          if (firstDose) firstDose.value = data.dosage;
        }

        if (typeof data.refill_restricted === "boolean") {
          const refEl = document.getElementById("refill_restricted");
          if (refEl) refEl.checked = data.refill_restricted;
        }

        // Show correction warning or confirmation
        const hintEl = document.getElementById("medicine-hint");
        const corr = data.corrections || {};
        if (hintEl) {
          if (corr.is_corrected && corr.match) {
            hintEl.innerHTML = `<span style="color:#d97706; font-weight:600;">⚠️ Auto-corrected drug name from "${corr.original}" to "${corr.match}" (${corr.score}% match)</span>`;
          } else if (corr.match) {
            hintEl.innerHTML = `<span style="color:#16a34a;">✓ Formulary match: ${corr.match} (${corr.category || "Verified"})</span>`;
          } else {
            hintEl.textContent = "";
          }
        }

        updateStatus("✓ Form auto-filled from dictation. Please review before saving.", "success");
      })
      .catch((err) => {
        console.error("Voice parse request failed:", err);
        updateStatus("AI voice parse failed. Please enter checkup details manually.", "error");
      });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Live Typing Spellcheck on Medicine Input Field
  // ─────────────────────────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    const medInput = document.getElementById("medicine");
    const hintEl = document.getElementById("medicine-hint");
    if (!medInput || !hintEl) return;

    let debounceTimer = null;

    medInput.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      const query = medInput.value.trim();
      if (query.length < 3) {
        hintEl.textContent = "";
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch("/ai/correct-drug", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ query: query }),
        })
          .then((res) => res.json())
          .then((res) => {
            if (res.is_exact) {
              hintEl.innerHTML = `<span style="color:#16a34a;">✓ Formulary: ${res.match} (${res.category || ""})</span>`;
            } else if (res.is_corrected && res.match) {
              hintEl.innerHTML = `<span style="color:#d97706;">💡 Did you mean: <strong>${res.match}</strong>? (Click to apply)</span>`;
              hintEl.style.cursor = "pointer";
              hintEl.onclick = function () {
                medInput.value = res.match;
                hintEl.innerHTML = `<span style="color:#16a34a;">✓ Selected: ${res.match}</span>`;
                hintEl.onclick = null;
              };
            } else if (res.match === null) {
              hintEl.innerHTML = `<span style="color:#64748b;">ℹ️ Unrecognized medication name</span>`;
              hintEl.onclick = null;
            }
          })
          .catch(() => {});
      }, 350);
    });
  });
})();
