
      // ==========================================================================
      // LIVE MATCH-CONFIDENCE METER
      // Measures the real time interval between keystrokes in the password
      // field and maps a rolling average of those intervals to a confidence
      // percentage. This is a lightweight, client-side illustration of the same
      // kind of timing signal the backend's behavior-matching engine compares
      // against the enrolled profile — purely illustrative, nothing is sent
      // anywhere or used to make the actual authentication decision.
      // ==========================================================================
      (function () {
        const passwordInput = document.getElementById("password");
        const matchFill = document.getElementById("matchFill");
        const matchValue = document.getElementById("matchValue");
        const MAX_SAMPLES = 12;

        let startTypingTime = null;
        let lastKeyTime = null;
        let intervals = [];

        let holdTimes = [];
        let keyDownTimes = {};

        function updateMeter() {
          if (intervals.length === 0) {
            matchFill.style.width = "0%";
            matchValue.textContent = "--%";
            return;
          }

          const avg = intervals.reduce((a, b) => a + b, 0) / intervals.length;
          // Steadier, moderate-paced typing (around 90-260ms between keys) maps
          // to a higher illustrative confidence; very erratic timing maps lower.
          const variance =
            intervals.reduce((sum, v) => sum + Math.abs(v - avg), 0) /
            intervals.length;
          const steadiness = Math.max(0, 100 - variance / 3);
          const confidence = Math.round(Math.min(98, Math.max(35, steadiness)));

          matchFill.style.width = confidence + "%";
          matchValue.textContent = confidence + "%";
        }

        passwordInput.addEventListener("keydown", function (e) {
          const now = performance.now();

          if (!startTypingTime) {
            startTypingTime = performance.now();
          }

          keyDownTimes[e.key] = now;

          if (lastKeyTime !== null) {
            const intervalMs = now - lastKeyTime;

            intervals.push(intervalMs);

            if (intervals.length > MAX_SAMPLES) {
              intervals.shift();
            }

            updateMeter();
          }

          lastKeyTime = now;
        });
        passwordInput.addEventListener("keyup", function (e) {
          const now = performance.now();

          if (keyDownTimes[e.key]) {
            const holdTime = now - keyDownTimes[e.key];

            holdTimes.push(holdTime);

            if (holdTimes.length > MAX_SAMPLES) {
              holdTimes.shift();
            }
          }
        });

        passwordInput.addEventListener("blur", function () {
          lastKeyTime = null;
        });

        document.querySelector("form").addEventListener("submit", function () {
          const avgHold =
            holdTimes.length > 0
              ? holdTimes.reduce((a, b) => a + b, 0) / holdTimes.length
              : 0;

          const avgFlight =
            intervals.length > 0
              ? intervals.reduce((a, b) => a + b, 0) / intervals.length
              : 0;

          const typingSpeed =
            holdTimes.length / ((performance.now() - startTypingTime) / 1000);

          document.getElementById("hold_time").value = avgHold.toFixed(2);

          document.getElementById("flight_time").value = avgFlight.toFixed(2);

          document.getElementById("typing_speed").value =
            typingSpeed.toFixed(2);
        });
      })();

      // ==========================================================================
      // SHOW / HIDE PASSWORD TOGGLE
      // Swaps the password field's type between "password" and "text", and
      // swaps the button's icon between an open eye (hidden, click to reveal)
      // and a slashed eye (visible, click to hide). Icons are inline SVG using
      // currentColor, so they pick up the existing --text-dim / --cyan hover
      // colors automatically — no separate icon theming needed.
      // ==========================================================================
      (function () {
        const ICON_EYE = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"></path>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>`;

        const ICON_EYE_OFF = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a18.5 18.5 0 0 1 4.22-5.94"></path>
        <path d="M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 7 11 7a18.5 18.5 0 0 1-2.16 3.19"></path>
        <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"></path>
        <line x1="1" y1="1" x2="23" y2="23"></line>
      </svg>`;

        const passwordInput = document.getElementById("password");
        const toggle = document.getElementById("togglePassword");
        const caps = document.getElementById("capsWarning");
        console.log(passwordInput);
        console.log(toggle);
        console.log(caps);

        // Start in the "hidden" state, showing the open-eye icon (click to reveal).
        toggle.innerHTML = ICON_EYE;

        toggle.addEventListener("click", function () {
          console.log("Button clicked");
          const isHidden = passwordInput.type === "password";
          passwordInput.type = isHidden ? "text" : "password";
          
          toggle.innerHTML = isHidden ? ICON_EYE_OFF : ICON_EYE;
          toggle.setAttribute(
            "aria-label",
            isHidden ? "Hide password" : "Show password",
          );
          toggle.setAttribute("aria-pressed", isHidden ? "true" : "false");
        });

        passwordInput.addEventListener("keyup", function (e) {
          if (e.getModifierState("CapsLock")) {
            caps.style.display = "block";
          } else {
            caps.style.display = "none";
          }
        });
      })();
    