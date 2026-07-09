
      // ==========================================================================
      // LIVE KEYSTROKE-CADENCE VISUALIZER
      // Measures the real time interval between keystrokes in the password
      // field and renders each interval as a bar height (shorter interval =
      // taller bar = faster typing). This is a lightweight, client-side preview
      // of the same kind of signal (keystroke timing) the backend's behavior
      // profile is built from — purely illustrative, no data is sent anywhere.
      // ==========================================================================
      (function () {
        const passwordInput = document.getElementById("password");
        const cadenceTrack = document.getElementById("cadence");
        const MAX_BARS = 28;
        let lastKeyTime = null;
        let bars = [];

        function renderBars() {
          cadenceTrack.innerHTML = "";
          bars.forEach((heightPct) => {
            const bar = document.createElement("span");
            bar.className = "cadence-bar active";
            bar.style.height = heightPct + "%";
            cadenceTrack.appendChild(bar);
          });
        }

        passwordInput.addEventListener("keydown", function () {
          const now = performance.now();

          if (lastKeyTime !== null) {
            const intervalMs = now - lastKeyTime;
            // Map interval to a bar height: faster keystrokes (small interval)
            // produce taller bars, clamped to a sensible visual range.
            const clamped = Math.min(Math.max(intervalMs, 40), 500);
            const heightPct = 100 - ((clamped - 40) / (500 - 40)) * 85;

            bars.push(heightPct);
            if (bars.length > MAX_BARS) {
              bars.shift();
            }
            renderBars();
          }

          lastKeyTime = now;
        });

        passwordInput.addEventListener("blur", function () {
          lastKeyTime = null;
        });
      })();
      // ===============================
      // Behavioral Biometrics Collection
      // ===============================

      let keyDownTimes = {};
      let holdTimes = [];
      let flightTimes = [];

      let previousKeyTime = null;
      let startTypingTime = null;

      const passwordField = document.getElementById("password");

      passwordField.addEventListener("keydown", function (event) {
        const now = performance.now();

        if (startTypingTime === null) {
          startTypingTime = now;
        }

        keyDownTimes[event.key] = now;

        if (previousKeyTime !== null) {
          flightTimes.push(now - previousKeyTime);
        }

        previousKeyTime = now;
      });

      passwordField.addEventListener("keyup", function (event) {
        const now = performance.now();

        if (keyDownTimes[event.key]) {
          holdTimes.push(now - keyDownTimes[event.key]);
        }

        updateBehaviorFields();
      });

      function average(arr) {
        if (arr.length === 0) {
          return 0;
        }

        return arr.reduce((a, b) => a + b, 0) / arr.length;
      }

      function updateBehaviorFields() {
        const avgHold = average(holdTimes);

        const avgFlight = average(flightTimes);

        const typingSpeed =
          holdTimes.length / ((performance.now() - startTypingTime) / 1000);

        document.getElementById("hold_time").value = avgHold.toFixed(2);

        document.getElementById("flight_time").value = avgFlight.toFixed(2);

        document.getElementById("typing_speed").value = typingSpeed.toFixed(2);
      }
    