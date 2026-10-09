/**
 * tts.js  — Text-To-Speech (output only)
 * Separate from voice_input.js (speech-to-text input) so the two features
 * cannot get tangled in one file (per the implementation plan).
 *
 * Exposes: readSummary(text)
 * Called by the "🔊 Read summary" button on the patient history page.
 */

(function () {
  let currentUtterance = null;

  function readSummary(text) {
    if (!window.speechSynthesis) {
      alert("Text-to-speech is not supported in this browser.");
      return;
    }

    // If already speaking, stop first
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      if (currentUtterance && currentUtterance._text === text) {
        return; // Toggle off — already reading this text
      }
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance._text = text;
    utterance.lang = "en-IN";
    utterance.rate = 0.95;
    utterance.pitch = 1;

    const readBtn = document.getElementById("tts-read-btn");

    utterance.onstart = () => {
      if (readBtn) readBtn.textContent = "⏹ Stop Reading";
    };
    utterance.onend = () => {
      if (readBtn) readBtn.textContent = "🔊 Read Summary";
      currentUtterance = null;
    };
    utterance.onerror = () => {
      if (readBtn) readBtn.textContent = "🔊 Read Summary";
      currentUtterance = null;
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  }

  // Attach to global so the inline onclick can call it
  window.readSummary = readSummary;
})();
