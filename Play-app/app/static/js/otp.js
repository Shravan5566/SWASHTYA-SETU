/**
 * otp.js
 * Handles AJAX submission of the 6-digit OTP form.
 * On success, follows the server's redirect to the patient history page.
 */

(function () {
  const form = document.getElementById("otp-form");
  const input = document.getElementById("otp-input");
  const statusEl = document.getElementById("otp-status");
  const submitBtn = document.getElementById("otp-submit-btn");

  function setStatus(msg, isError = false) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.className = "otp-status " + (isError ? "otp-status--error" : "otp-status--info");
  }

  // Auto-advance: only allow digits and auto-submit at 6 chars
  if (input) {
    input.addEventListener("input", () => {
      input.value = input.value.replace(/\D/g, "").slice(0, 6);
      if (input.value.length === 6) {
        submitOtp();
      }
    });
  }

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      submitOtp();
    });
  }

  async function submitOtp() {
    const code = input ? input.value.trim() : "";
    if (code.length !== 6) {
      setStatus("Please enter all 6 digits.", true);
      return;
    }

    if (submitBtn) submitBtn.disabled = true;
    setStatus("Verifying…");

    try {
      const resp = await fetch("/ajax/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      const data = await resp.json();

      if (data.ok) {
        setStatus("Verified! Loading patient history…");
        window.location.href = data.redirect;
      } else {
        setStatus("Error: " + data.error, true);
        if (submitBtn) submitBtn.disabled = false;
      }
    } catch (err) {
      setStatus("Network error. Please try again.", true);
      if (submitBtn) submitBtn.disabled = false;
    }
  }
})();
