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
        const typingInput =
            document.getElementById("password") ||
            document.getElementById("verificationInput");
        if (!typingInput) return;

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

             if (matchFill)
                matchFill.style.width = "0%";

            if (matchValue)
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

          if (matchFill)
              matchFill.style.width = confidence + "%";

          if (matchValue)
              matchValue.textContent = confidence + "%";
        }

        typingInput.addEventListener("keydown", function (e) {
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
        typingInput.addEventListener("keyup", function (e) {
          const now = performance.now();

          if (keyDownTimes[e.key]) {
            const holdTime = now - keyDownTimes[e.key];

            holdTimes.push(holdTime);

            if (holdTimes.length > MAX_SAMPLES) {
              holdTimes.shift();
            }
          }

          let typingSpeed = 0;

          if (startTypingTime) {
            typingSpeed =
              holdTimes.length /
              ((performance.now() - startTypingTime) / 1000);
          }

          window.behaviorData = {
            holdTimes,
            intervals,
            avgHold:
              holdTimes.length
                ? holdTimes.reduce((a, b) => a + b, 0) / holdTimes.length
                : 0,
            avgFlight:
              intervals.length
                ? intervals.reduce((a, b) => a + b, 0) / intervals.length
                : 0,
            typingSpeed,
          };
        });

        typingInput.addEventListener("blur", function () {
          lastKeyTime = null;
        });

        const form = document.querySelector("form");

        if (form) {

            form.addEventListener("submit", function () {

          const avgHold =
            holdTimes.length > 0
              ? holdTimes.reduce((a, b) => a + b, 0) / holdTimes.length
              : 0;

          const avgFlight =
            intervals.length > 0
              ? intervals.reduce((a, b) => a + b, 0) / intervals.length
              : 0;

          let typingSpeed = 0;

          if (startTypingTime) {

            typingSpeed =
            holdTimes.length /
            ((performance.now() - startTypingTime) / 1000);

          }

          document.getElementById("hold_time").value = avgHold.toFixed(2);

          document.getElementById("flight_time").value = avgFlight.toFixed(2);

          document.getElementById("typing_speed").value =
            typingSpeed.toFixed(2);
            });
        }
      })();
     