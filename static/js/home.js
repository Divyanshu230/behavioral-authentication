/* ==========================================================================
   BBA-PATP :: Homepage interactions
   - Fixed nav scroll state + mobile menu toggle
   - Animated "signal grid" canvas background (cyber telemetry motif)
   - Hero score ring count-up (echoes the dashboard's live behavior score)
   - Scroll-reveal for feature / step / stack cards
   ========================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    initNavbar();
    initMobileMenu();
    initSignalGrid();
    initRingScore();
    initScrollReveal();
    initFooterYear();
  });

  /* ------------------------------------------------------------------ */
  /* Navbar: add solid background once the page is scrolled             */
  /* ------------------------------------------------------------------ */
  function initNavbar() {
    var navbar = document.getElementById('navbar');
    if (!navbar) return;

    function onScroll() {
      if (window.scrollY > 12) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    }

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------------------------------------------ */
  /* Mobile nav toggle                                                   */
  /* ------------------------------------------------------------------ */
  function initMobileMenu() {
    var toggle = document.getElementById('navToggle');
    var links = document.getElementById('navLinks');
    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
      var isOpen = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close the menu whenever a link is tapped
    links.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Ambient background: a faint drifting grid of nodes and connecting   */
  /* lines, evoking a live behavioral-signal / network-monitoring feed.  */
  /* ------------------------------------------------------------------ */
  function initSignalGrid() {
    var canvas = document.getElementById('signal-grid');
    if (!canvas || !canvas.getContext) return;

    var ctx = canvas.getContext('2d');
    var nodes = [];
    var width, height;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var CYAN = '52, 229, 196';
    var NODE_COUNT_DIVISOR = 22000; // lower = more nodes
    var MAX_LINK_DIST = 150;

    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      seedNodes();
    }

    function seedNodes() {
      var count = Math.max(24, Math.min(70, Math.floor((width * height) / NODE_COUNT_DIVISOR)));
      nodes = [];
      for (var i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.18,
          vy: (Math.random() - 0.5) * 0.18,
          r: Math.random() * 1.4 + 0.6
        });
      }
    }

    function step() {
      ctx.clearRect(0, 0, width, height);

      // Update positions
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx;
        n.y += n.vy;

        if (n.x < 0 || n.x > width) n.vx *= -1;
        if (n.y < 0 || n.y > height) n.vy *= -1;
      }

      // Draw links between nearby nodes
      for (var a = 0; a < nodes.length; a++) {
        for (var b = a + 1; b < nodes.length; b++) {
          var dx = nodes[a].x - nodes[b].x;
          var dy = nodes[a].y - nodes[b].y;
          var dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < MAX_LINK_DIST) {
            var alpha = (1 - dist / MAX_LINK_DIST) * 0.16;
            ctx.strokeStyle = 'rgba(' + CYAN + ', ' + alpha + ')';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(nodes[a].x, nodes[a].y);
            ctx.lineTo(nodes[b].x, nodes[b].y);
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      for (var j = 0; j < nodes.length; j++) {
        var node = nodes[j];
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + CYAN + ', 0.5)';
        ctx.fill();
      }

      if (!reduceMotion) {
        requestAnimationFrame(step);
      }
    }

    window.addEventListener('resize', debounce(resize, 200));
    resize();
    step();
  }

  /* ------------------------------------------------------------------ */
  /* Hero score ring: animate the stroke + numeric readout on load,      */
  /* mirroring the "Behavior Match Score" ring on the dashboard.         */
  /* ------------------------------------------------------------------ */
  function initRingScore() {
    var progress = document.getElementById('ringProgress');
    var scoreLabel = document.getElementById('ringScore');
    if (!progress || !scoreLabel) return;

    var CIRCUMFERENCE = 540; // matches stroke-dasharray in CSS
    var TARGET_SCORE = 91.4; // decorative target, distinct from a live session
    var duration = 1600;
    var startTime = null;

    function easeOutCubic(t) {
      return 1 - Math.pow(1 - t, 3);
    }

    function tick(timestamp) {
      if (startTime === null) startTime = timestamp;
      var elapsed = timestamp - startTime;
      var t = Math.min(elapsed / duration, 1);
      var eased = easeOutCubic(t);
      var currentScore = TARGET_SCORE * eased;

      var offset = CIRCUMFERENCE - (currentScore / 100) * CIRCUMFERENCE;
      progress.style.strokeDashoffset = offset;
      scoreLabel.firstChild.nodeValue = currentScore.toFixed(1);

      if (t < 1) {
        requestAnimationFrame(tick);
      }
    }

    requestAnimationFrame(tick);
  }

  /* ------------------------------------------------------------------ */
  /* Scroll reveal: fade/rise cards into view as the user scrolls        */
  /* ------------------------------------------------------------------ */
  function initScrollReveal() {
    var targets = document.querySelectorAll(
      '.feature-card, .step-card, .stack-card'
    );
    if (!targets.length) return;

    if (!('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.style.opacity = 1; });
      return;
    }

    targets.forEach(function (el) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(14px)';
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, index) {
        if (entry.isIntersecting) {
          var el = entry.target;
          setTimeout(function () {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
          }, (index % 6) * 60);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    targets.forEach(function (el) { observer.observe(el); });
  }

  /* ------------------------------------------------------------------ */
  /* Footer year                                                         */
  /* ------------------------------------------------------------------ */
  function initFooterYear() {
    var el = document.getElementById('footerYear');
    if (el) el.textContent = new Date().getFullYear();
  }

  /* ------------------------------------------------------------------ */
  /* Utility: debounce                                                    */
  /* ------------------------------------------------------------------ */
  function debounce(fn, wait) {
    var timeout;
    return function () {
      var args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(function () { fn.apply(null, args); }, wait);
    };
  }
})();