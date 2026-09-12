/**
 * VUCA Axloq — Gamified EdTech App JS
 * Features:
 *  - Rotating Motivational Panda Quotes (waving hand animation)
 *  - Upgraded Microlearning Slider (Autoplay toggle, Lightbox Fullscreen viewer)
 *  - Dark Mode Toggle & Persistence
 *  - Kahoot Interactive Test Selection
 *  - Celebratory Confetti System
 *  - Mobile Navigation
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. DARK MODE TOGGLE (Synchronized across desktop and mobile)
  // =========================================================================
  try {
    const themeToggles = document.querySelectorAll("[data-theme-toggle]");
    const currentTheme = localStorage.getItem("theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

    function setTheme(theme) {
      document.documentElement.setAttribute("data-theme", theme);
      localStorage.setItem("theme", theme);
      themeToggles.forEach(function (btn) {
        const icon = btn.querySelector("i");
        if (icon) {
          icon.className = theme === "dark" ? "fas fa-sun" : "fas fa-moon";
        }
      });
    }

    setTheme(currentTheme);

    themeToggles.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const now = document.documentElement.getAttribute("data-theme");
        setTheme(now === "dark" ? "light" : "dark");
        if (typeof playPopSound === "function") {
          playPopSound(520);
        }
      });
    });
  } catch (err) {
    console.error("Theme toggle error:", err);
  }

  // =========================================================================
  // 1.1 DUOLINGO-STYLE WEB AUDIO SYNTHESIZER (Pure Native Browser API)
  // =========================================================================
  let audioCtx = null;
  let soundEnabled = localStorage.getItem("duoSound") !== "false";

  function getAudioContext() {
    if (!audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) {
        audioCtx = new AudioCtxClass();
      }
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playPopSound(freq) {
    if (!soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const baseFreq = freq || 440;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      const now = ctx.currentTime;
      osc.frequency.setValueAtTime(baseFreq, now);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.5, now + 0.035);
      osc.frequency.exponentialRampToValueAtTime(baseFreq * 0.6, now + 0.08);

      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.085);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.09);
    } catch (e) {}
  }

  function playSuccessChime() {
    if (!soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      // Duolingo iconic 4-note ascending major arpeggio: C5, E5, G5, C6
      const notes = [523.25, 659.25, 783.99, 1046.50];
      const now = ctx.currentTime;

      notes.forEach(function (freq, i) {
        const startTime = now + i * 0.075;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, startTime);

        gain.gain.setValueAtTime(0, startTime);
        gain.gain.linearRampToValueAtTime(0.22, startTime + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.32);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + 0.35);
      });
    } catch (e) {}
  }

  function playChestFanfare() {
    if (!soundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const notes = [523.25, 659.25, 783.99, 1046.50, 1318.51];
      const now = ctx.currentTime;

      notes.forEach(function (freq, i) {
        const startTime = now + i * 0.06;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, startTime);

        gain.gain.setValueAtTime(0.18, startTime);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.65);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + 0.7);
      });
    } catch (e) {}
  }

  // Sound Toggle Buttons
  const soundToggles = document.querySelectorAll("[data-sound-toggle]");
  function updateSoundUI() {
    soundToggles.forEach(function (btn) {
      btn.classList.toggle("is-muted", !soundEnabled);
      const icon = btn.querySelector("i");
      if (icon) {
        icon.className = soundEnabled ? "fas fa-volume-high" : "fas fa-volume-xmark";
      }
    });
  }
  updateSoundUI();

  soundToggles.forEach(function (btn) {
    btn.addEventListener("click", function () {
      soundEnabled = !soundEnabled;
      localStorage.setItem("duoSound", soundEnabled ? "true" : "false");
      updateSoundUI();
      if (soundEnabled) {
        playPopSound(580);
      }
    });
  });

  // =========================================================================
  // 1.2 DUOLINGO FLOATING TOAST PARTICLES
  // =========================================================================
  function spawnFloatingParticle(x, y, text) {
    const el = document.createElement("div");
    el.className = "duo-float-particle";
    el.textContent = text;
    el.style.left = x + "px";
    el.style.top = y + "px";
    document.body.appendChild(el);
    setTimeout(function () {
      el.remove();
    }, 1150);
  }

  // =========================================================================
  // 2. MOBILE MENU TOGGLE
  // =========================================================================
  try {
    const toggle = document.querySelector("[data-menu-toggle]");
    const mobileNav = document.querySelector("[data-mobile-nav]");
    if (toggle && mobileNav) {
      toggle.addEventListener("click", function (e) {
        e.stopPropagation();
        const open = mobileNav.classList.toggle("open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        toggle.textContent = open ? "✕" : "☰";
        if (typeof playPopSound === "function") {
          playPopSound(480);
        }
      });

      mobileNav.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
          mobileNav.classList.remove("open");
          toggle.setAttribute("aria-expanded", "false");
          toggle.textContent = "☰";
        });
      });

      document.addEventListener("click", function (e) {
        if (!mobileNav.contains(e.target) && !toggle.contains(e.target) && mobileNav.classList.contains("open")) {
          mobileNav.classList.remove("open");
          toggle.setAttribute("aria-expanded", "false");
          toggle.textContent = "☰";
        }
      });
    }
  } catch (err) {
    console.error("Mobile menu error:", err);
  }

  // =========================================================================
  // 3. REVEAL ANIMATIONS
  // =========================================================================
  document.querySelectorAll(".reveal").forEach(function (el, i) {
    el.style.animationDelay = (i * 60) + "ms";
  });

  // =========================================================================
  // 4. CELEBRATORY CONFETTI
  // =========================================================================
  window.triggerConfetti = function () {
    if (typeof confetti === "function") {
      confetti({
        particleCount: 110,
        spread: 80,
        origin: { y: 0.65 }
      });
      setTimeout(function () {
        confetti({
          particleCount: 70,
          angle: 60,
          spread: 55,
          origin: { x: 0.1, y: 0.7 }
        });
        confetti({
          particleCount: 70,
          angle: 120,
          spread: 55,
          origin: { x: 0.9, y: 0.7 }
        });
      }, 220);
    }
  };

  if (document.querySelector(".celebrate")) {
    window.addEventListener("load", function () {
      window.triggerConfetti();
    });
  }

  // =========================================================================
  // 5. PANDA MOTIVATIONAL SPEECH BUBBLE (ROTATING QUOTES)
  // =========================================================================
  const pandaBubble = document.querySelector("[data-mascot-bubble]");
  const pandaBox = document.querySelector("[data-mascot-box]");
  const quoteText = document.querySelector("[data-mascot-quote]");
  const quoteTag = document.querySelector("[data-bubble-tag]");
  const dotsWrap = document.querySelector("[data-bubble-dots]");

  const motivationalQuotes = [
    { text: "Salom do‘stim! Bugun yangi bilimlar sari olg‘a! 🚀", tag: "Salomlashuv" },
    { text: "O‘zgaruvchan (VUCA) dunyoda eng katta boylik — mustahkam axloq va bilim! 💎", tag: "Qadriyat" },
    { text: "Noaniqlikdan aslo qo‘rqma, bilim va qat’iyat uni yengadi! 💡", tag: "Qat’iyat" },
    { text: "Halollik va mas’uliyat — zamonaviy liderlikning asl kalitidir! 🌟", tag: "Yetakchilik" },
    { text: "Har bir kichik qadam va yakunlangan dars seni katta marralarga yetaklaydi! 🎯", tag: "Maqsad sari" },
    { text: "Bugungi to‘plagan XP ballaring — ertangi muvaffaqiyating poydevori! ⚡", tag: "Shijoat" },
    { text: "Qiyinchiliklar va murakkabliklar seni yanada kuchli va dono qiladi! 💪", tag: "Matonat" },
    { text: "Kelajak — bugun o‘rganishdan to‘xtamagan yoshlarga tegishli! 🏆", tag: "Kelajak" }
  ];

  if (quoteText && motivationalQuotes.length) {
    let quoteIndex = 0;
    let quoteTimer = null;

    // Render dots if container exists
    if (dotsWrap) {
      dotsWrap.innerHTML = motivationalQuotes.map(function (_, i) {
        return '<span class="' + (i === 0 ? 'is-active' : '') + '"></span>';
      }).join('');
    }

    function showQuote(i) {
      quoteIndex = (i + motivationalQuotes.length) % motivationalQuotes.length;
      const q = motivationalQuotes[quoteIndex];

      quoteText.classList.add("fade-out");
      setTimeout(function () {
        quoteText.textContent = q.text;
        if (quoteTag) {
          quoteTag.innerHTML = '<i class="fas fa-sparkles"></i> ' + q.tag;
        }
        quoteText.classList.remove("fade-out");

        if (dotsWrap) {
          dotsWrap.querySelectorAll("span").forEach(function (dot, idx) {
            dot.classList.toggle("is-active", idx === quoteIndex);
          });
        }
      }, 250);
    }

    function startQuoteRotation() {
      clearInterval(quoteTimer);
      quoteTimer = setInterval(function () {
        showQuote(quoteIndex + 1);
      }, 4500);
    }

    startQuoteRotation();

    // Duolingo Mascot Click (Squish & Stretch, Wobble, Sound & Floating Particles)
    const pandaClickables = [pandaBubble, pandaBox].filter(Boolean);
    const encouragementPhrases = [
      "⚡ +10 XP",
      "🔥 Zo‘r ketmoqdasiz!",
      "🐼 Barakalla!",
      "💎 +1 Olmos!",
      "🌟 Super natija!",
      "🎯 Olg‘a!",
      "🚀 Yangi marra!"
    ];

    pandaClickables.forEach(function (elem) {
      elem.addEventListener("click", function (e) {
        if (e.target.closest("[data-next-quote]")) return;
        showQuote(quoteIndex + 1);
        startQuoteRotation();

        // 1. Duolingo Mascot Squish & Stretch
        if (pandaBox) {
          pandaBox.classList.remove("is-squished");
          void pandaBox.offsetWidth;
          pandaBox.classList.add("is-squished");
          setTimeout(function () {
            pandaBox.classList.remove("is-squished");
          }, 650);
        }

        // 2. Duolingo Speech Bubble Wobble
        if (pandaBubble) {
          pandaBubble.classList.remove("is-wobbling");
          void pandaBubble.offsetWidth;
          pandaBubble.classList.add("is-wobbling");
          setTimeout(function () {
            pandaBubble.classList.remove("is-wobbling");
          }, 500);
        }

        // 3. Tactile Audio Pop
        playPopSound(520);

        // 4. Floating XP / Praise Particle
        const rect = elem.getBoundingClientRect();
        const randText = encouragementPhrases[Math.floor(Math.random() * encouragementPhrases.length)];
        const clickX = e.clientX || (rect.left + rect.width / 2);
        const clickY = e.clientY || (rect.top + 20);
        spawnFloatingParticle(clickX, clickY, randText);
      });
    });

    const nextQuoteBtn = document.querySelector("[data-next-quote]");
    if (nextQuoteBtn) {
      nextQuoteBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        const icon = nextQuoteBtn.querySelector("i");
        if (icon) {
          icon.style.transform = "rotate(360deg)";
          icon.style.transition = "transform 0.4s ease";
          setTimeout(function () {
            icon.style.transform = "";
            icon.style.transition = "";
          }, 400);
        }
        showQuote(quoteIndex + 1);
        startQuoteRotation();
      });
    }
  }


  // =========================================================================
  // 6. KAHOOT INTERACTIVE TEST SELECTION
  // =========================================================================
  const kahootChoices = document.querySelectorAll(".kahoot-choice");
  kahootChoices.forEach(function (label) {
    label.addEventListener("click", function () {
      const parentGrid = label.closest(".kahoot-answers-grid");
      if (parentGrid) {
        parentGrid.querySelectorAll(".kahoot-choice").forEach(function (other) {
          other.classList.remove("is-selected");
        });
      }
      label.classList.add("is-selected");
      const radio = label.querySelector('input[type="radio"]');
      if (radio) radio.checked = true;
    });

    const radio = label.querySelector('input[type="radio"]');
    if (radio && radio.checked) {
      label.classList.add("is-selected");
    }
  });

  // =========================================================================
  // 7. UPGRADED MICROLEARNING SLIDER & LIGHTBOX MODAL
  // =========================================================================
  const root = document.querySelector("[data-slider]");
  if (root) {
    const viewport = root.querySelector(".slider-viewport");
    const track = root.querySelector(".slider-track");
    const cards = Array.from(root.querySelectorAll(".slider-card"));
    const thumbs = Array.from(root.querySelectorAll("[data-thumbs] .thumb"));
    const timerBar = root.querySelector("[data-timer]");
    const currentEl = root.querySelector("[data-current]");
    const playToggleBtn = root.querySelector("[data-toggle-play]");
    const openModalBtn = root.querySelector("[data-open-modal]");

    // Lightbox modal elements
    const modal = document.getElementById("infographicModal");
    const modalTitle = document.getElementById("modalTitle");
    const modalImg = document.getElementById("modalImg");
    const modalCaption = document.getElementById("modalCaption");
    const modalCount = document.getElementById("modalCount");
    const modalDownload = document.getElementById("modalDownload");
    const modalCloseBtn = modal ? modal.querySelector("[data-close-modal]") : null;
    const modalPrevBtn = modal ? modal.querySelector("[data-modal-prev]") : null;
    const modalNextBtn = modal ? modal.querySelector("[data-modal-next]") : null;

    if (viewport && track && cards.length) {
      let index = 0;
      let timer = null;
      let isAutoplay = true;
      let startX = 0;
      let deltaX = 0;
      let dragging = false;
      const INTERVAL = 5000;

      function layout() {
        const card = cards[index];
        if (!card) return;
        const gap = parseFloat(getComputedStyle(track).gap) || 22;
        const cardW = cards[0].offsetWidth;
        const offset = viewport.clientWidth / 2 - cardW / 2 - index * (cardW + gap);
        track.style.transform = "translateX(" + offset + "px)";
        cards.forEach(function (c, i) {
          const dist = Math.abs(i - index);
          c.classList.toggle("is-active", i === index);
          c.classList.toggle("is-side", dist === 1);
          c.classList.toggle("is-far", dist > 1);
        });
        thumbs.forEach(function (t, i) {
          t.classList.toggle("is-active", i === index);
        });
        if (currentEl) currentEl.textContent = String(index + 1);
        const activeThumb = thumbs[index];
        if (activeThumb) {
          const thumbsContainer = activeThumb.parentElement;
          if (thumbsContainer) {
            const scrollLeftTarget = activeThumb.offsetLeft - (thumbsContainer.clientWidth / 2) + (activeThumb.clientWidth / 2);
            thumbsContainer.scrollTo({ left: Math.max(0, scrollLeftTarget), behavior: "smooth" });
          }
        }
      }

      function restartTimer() {
        if (!timerBar) return;
        timerBar.classList.remove("is-run");
        void timerBar.offsetWidth;
        if (isAutoplay) {
          timerBar.classList.add("is-run");
        }
      }

      function go(next) {
        index = (next + cards.length) % cards.length;
        layout();
        restartTimer();
        if (modal && modal.classList.contains("is-open")) {
          populateModal(index);
        }
      }

      function play() {
        if (!isAutoplay) return;
        clearInterval(timer);
        timer = setInterval(function () {
          go(index + 1);
        }, INTERVAL);
        restartTimer();
      }

      function pause() {
        clearInterval(timer);
        if (timerBar) timerBar.classList.remove("is-run");
      }

      // Prev / Next buttons
      const prevBtn = root.querySelector("[data-prev]");
      if (prevBtn) {
        prevBtn.addEventListener("click", function () {
          go(index - 1);
          play();
        });
      }
      const nextBtn = root.querySelector("[data-next]");
      if (nextBtn) {
        nextBtn.addEventListener("click", function () {
          go(index + 1);
          play();
        });
      }

      // Thumbnails click
      thumbs.forEach(function (thumb) {
        thumb.addEventListener("click", function () {
          go(Number(thumb.getAttribute("data-goto") || 0));
          play();
        });
      });

      // Play / Pause Toggle
      if (playToggleBtn) {
        playToggleBtn.addEventListener("click", function () {
          isAutoplay = !isAutoplay;
          const icon = playToggleBtn.querySelector("i");
          const textSpan = playToggleBtn.querySelector("[data-play-text]");
          if (isAutoplay) {
            if (icon) icon.className = "fas fa-pause";
            if (textSpan) textSpan.textContent = "Pauza";
            play();
          } else {
            if (icon) icon.className = "fas fa-play";
            if (textSpan) textSpan.textContent = "Davom ettirish";
            pause();
          }
        });
      }

      // Hover pauses on desktop
      viewport.addEventListener("mouseenter", function () {
        if (isAutoplay) pause();
      });
      viewport.addEventListener("mouseleave", function () {
        if (isAutoplay) play();
      });

      // Touch Drag on mobile
      viewport.addEventListener("touchstart", function (e) {
        dragging = true;
        startX = e.touches[0].clientX;
        deltaX = 0;
        pause();
      }, { passive: true });

      viewport.addEventListener("touchmove", function (e) {
        if (!dragging) return;
        deltaX = e.touches[0].clientX - startX;
      }, { passive: true });

      viewport.addEventListener("touchend", function () {
        dragging = false;
        if (Math.abs(deltaX) > 40) {
          go(index + (deltaX < 0 ? 1 : -1));
        }
        if (isAutoplay) play();
      });

      // --- Lightbox Modal Logic ---
      function populateModal(i) {
        const card = cards[i];
        if (!card) return;
        const title = card.getAttribute("data-title") || "Infografika";
        const caption = card.getAttribute("data-caption") || "";
        const imgUrl = card.getAttribute("data-img") || "";

        if (modalTitle) modalTitle.textContent = title;
        if (modalImg) {
          modalImg.src = imgUrl;
          modalImg.alt = title;
        }
        if (modalCaption) modalCaption.textContent = caption;
        if (modalCount) modalCount.textContent = (i + 1) + " / " + cards.length + " infografika";
        if (modalDownload) modalDownload.href = imgUrl;
      }

      function openModal(i) {
        populateModal(i);
        if (modal) {
          modal.classList.add("is-open");
          modal.setAttribute("aria-hidden", "false");
          document.body.style.overflow = "hidden";
          pause();
        }
      }

      function closeModal() {
        if (modal) {
          modal.classList.remove("is-open");
          modal.setAttribute("aria-hidden", "true");
          document.body.style.overflow = "";
          if (isAutoplay) play();
        }
      }

      // Click card to open modal
      cards.forEach(function (card, i) {
        card.addEventListener("click", function () {
          if (Math.abs(deltaX) < 10) {
            openModal(i);
          }
        });
      });

      if (openModalBtn) {
        openModalBtn.addEventListener("click", function () {
          openModal(index);
        });
      }

      if (modalCloseBtn) {
        modalCloseBtn.addEventListener("click", closeModal);
      }

      if (modal) {
        modal.addEventListener("click", function (e) {
          if (e.target === modal) closeModal();
        });
      }

      if (modalPrevBtn) {
        modalPrevBtn.addEventListener("click", function () {
          go(index - 1);
        });
      }

      if (modalNextBtn) {
        modalNextBtn.addEventListener("click", function () {
          go(index + 1);
        });
      }

      document.addEventListener("keydown", function (e) {
        if (modal && modal.classList.contains("is-open")) {
          if (e.key === "Escape") closeModal();
          if (e.key === "ArrowLeft") go(index - 1);
          if (e.key === "ArrowRight") go(index + 1);
        }
      });

      window.addEventListener("resize", layout);
      window.addEventListener("load", layout);
      layout();

      if ("IntersectionObserver" in window) {
        const sliderVisibilityObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              if (isAutoplay) play();
            } else {
              pause();
            }
          });
        }, { threshold: 0.1 });
        sliderVisibilityObserver.observe(root);
      } else {
        play();
      }
    }
  }

  // =========================================================================
  // 7b. WORD & PDF DOCUMENTS FILTER TABS
  // =========================================================================
  const docFilters = document.querySelector("[data-doc-filters]");
  const docCards = document.querySelectorAll("[data-doc-grid] .doc-card");
  if (docFilters && docCards.length) {
    docFilters.addEventListener("click", function (e) {
      const btn = e.target.closest(".doc-filter-btn");
      if (!btn) return;
      docFilters.querySelectorAll(".doc-filter-btn").forEach(function (b) {
        b.classList.remove("is-active");
      });
      btn.classList.add("is-active");
      const filter = btn.getAttribute("data-filter");
      docCards.forEach(function (card) {
        const type = card.getAttribute("data-doc-type");
        const format = card.getAttribute("data-doc-format");
        let visible = false;
        if (filter === "all") visible = true;
        else if (filter === "word" && format === "word") visible = true;
        else if (filter === "pdf" && format === "pdf") visible = true;
        else if (filter === type) visible = true;
        card.style.display = visible ? "flex" : "none";
      });
    });
  }

  // =========================================================================
  // 8. DUOLINGO ACTIVE LESSON BEACON PULSE (PATH RADAR)
  // =========================================================================
  const allPathCards = document.querySelectorAll(".path-card");
  let activeLessonFound = false;
  allPathCards.forEach(function (card) {
    if (!card.classList.contains("is-done") && !activeLessonFound) {
      card.classList.add("is-active-lesson");
      activeLessonFound = true;
    }
  });
  if (!activeLessonFound && allPathCards.length) {
    allPathCards[0].classList.add("is-active-lesson");
  }

  // =========================================================================
  // 9. DUOLINGO UNIT CHEST INTERACTION (CONFETTI & FANFARE)
  // =========================================================================
  document.querySelectorAll(".unit-chest").forEach(function (chest) {
    chest.addEventListener("click", function (e) {
      chest.classList.toggle("is-open");
      playChestFanfare();
      if (typeof window.triggerConfetti === "function") {
        window.triggerConfetti();
      }
      const rect = chest.getBoundingClientRect();
      const clickX = e.clientX || (rect.left + rect.width / 2);
      const clickY = e.clientY || (rect.top - 10);
      spawnFloatingParticle(clickX, clickY, "🎁 +25 XP Mukofot!");
    });
  });

  // =========================================================================
  // 10. DUOLINGO TACTILE BUTTON SOUNDS & RIPPLE
  // =========================================================================
  document.addEventListener("click", function (e) {
    try {
      const btn = e.target.closest(".btn, .path-card, .vuca-tile, .stat-pill, .doc-chip, .task-card, .doc-filter-btn, .slider-ctrl-btn");
      if (btn && !btn.closest("[data-sound-toggle]")) {
        playPopSound(440);

        // Tactile ripple without ever blocking clicks or pointer events
        const rect = btn.getBoundingClientRect();
        const ripple = document.createElement("span");
        ripple.className = "duo-ripple";
        ripple.style.pointerEvents = "none";
        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = size + "px";
        ripple.style.left = (e.clientX - rect.left - size / 2) + "px";
        ripple.style.top = (e.clientY - rect.top - size / 2) + "px";
        btn.appendChild(ripple);
        setTimeout(function () {
          if (ripple.parentNode) {
            ripple.parentNode.removeChild(ripple);
          }
        }, 550);
      }
    } catch (err) {
      // Audio or ripple failure must never impede button navigation
    }
  });

  // Check celebration trigger (e.g. Test success result)
  if (document.querySelector(".celebrate, .test-result-success")) {
    window.addEventListener("load", function () {
      setTimeout(function () {
        playSuccessChime();
        if (typeof window.triggerConfetti === "function") {
          window.triggerConfetti();
        }
      }, 400);
    });
  }

  // =========================================================================
  // 11. DUOLINGO 1:1 AUTHENTIC LOTTIE ANIMATIONS & SCROLL DYNAMICS
  // =========================================================================
  window.__duoLottieInstances = [];

  function initDuoShowcaseLottie() {
    if (typeof lottie === "undefined") {
      setTimeout(initDuoShowcaseLottie, 100);
      return;
    }

    const animationsConfig = [
      {
        id: "lottie-effective",
        placeholderId: "placeholder-effective",
        path: "/static/duo_splash/effective_lottie.json"
      },
      {
        id: "lottie-science",
        placeholderId: "placeholder-science",
        path: "/static/duo_splash/science_lottie.json"
      },
      {
        id: "lottie-motivation",
        placeholderId: "placeholder-motivation",
        path: "/static/duo_splash/motivation_lottie.json"
      },
      {
        id: "lottie-personalized",
        placeholderId: "placeholder-personalized",
        path: "/static/duo_splash/personalized_lottie.json"
      },
      {
        id: "lottie-anytime",
        placeholderId: "placeholder-anytime",
        path: "/static/duo_splash/anytime_lottie.json"
      },
      {
        id: "lottie-bottom",
        placeholderId: "placeholder-bottom",
        path: "/static/duo_splash/bottom_lottie.json"
      }
    ];

    animationsConfig.forEach(function (cfg) {
      const container = document.getElementById(cfg.id);
      const placeholder = document.getElementById(cfg.placeholderId);
      if (!container) return;

      if (container.getAttribute("data-lottie-loaded") === "true") return;
      container.setAttribute("data-lottie-loaded", "true");

      try {
        const anim = lottie.loadAnimation({
          container: container,
          renderer: "svg",
          loop: true,
          autoplay: true,
          path: cfg.path
        });

        window.__duoLottieInstances.push(anim);

        anim.addEventListener("DOMLoaded", function () {
          if (placeholder) {
            placeholder.style.opacity = "0";
            setTimeout(function () {
              placeholder.style.display = "none";
              placeholder.style.visibility = "hidden";
            }, 350);
          }
          anim.play();
        });

        anim.addEventListener("data_failed", function () {
          if (placeholder) {
            placeholder.style.opacity = "1";
            placeholder.style.visibility = "visible";
            placeholder.style.display = "block";
          }
        });

        // IntersectionObserver: smoothly pause when off-screen and resume when in-view
        if ("IntersectionObserver" in window) {
          const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
              const card = container.closest(".duo-feature-row, .duo-anytime-card, .duo-bottom-banner");
              if (card) {
                card.setAttribute("data-in-view", entry.isIntersecting ? "true" : "false");
              }

              if (entry.isIntersecting) {
                anim.play();
              } else {
                anim.pause();
              }
            });
          }, { threshold: 0.08 });

          observer.observe(container);
        }
      } catch (err) {
        console.error("Failed to load Lottie animation for " + cfg.id, err);
        if (placeholder) {
          placeholder.style.opacity = "1";
          placeholder.style.visibility = "visible";
          placeholder.style.display = "block";
        }
      }
    });
  }

  // =========================================================================
  // 12. SCROLL DYNAMICS CONTROLLER (UP / DOWN SENSITIVE & PARALLAX)
  // =========================================================================
  function initScrollDynamicsController() {
    let lastScrollY = window.pageYOffset || document.documentElement.scrollTop;
    let ticking = false;

    function onScrollTick() {
      const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;
      const scrollDelta = currentScrollY - lastScrollY;
      const scrollDirection = scrollDelta >= 0 ? "down" : "up";

      const showcase = document.getElementById("duo-showcase");
      if (showcase) {
        showcase.setAttribute("data-scroll-dir", scrollDirection);
      }

      const windowHeight = window.innerHeight || 800;

      // 1. Parallax tilt and shift on all elements with [data-scroll-parallax]
      document.querySelectorAll("[data-scroll-parallax]").forEach(function (card) {
        const rect = card.getBoundingClientRect();
        if (rect.top < windowHeight + 120 && rect.bottom > -120) {
          const centerY = rect.top + rect.height / 2;
          const progress = (centerY - windowHeight / 2) / (windowHeight / 2); // -1 (top) to +1 (bottom)

          const visual = card.querySelector("[data-parallax-target='visual']");
          const text = card.querySelector("[data-parallax-target='text']");

          if (visual) {
            const depth = parseFloat(visual.getAttribute("data-parallax-depth")) || 0.2;
            const translateY = progress * -24 * depth * 5;
            const rotate = progress * 2.5;
            const scale = 1 - Math.min(Math.abs(progress) * 0.02, 0.04);
            visual.style.transform = `translate3d(0, ${translateY.toFixed(1)}px, 0) rotate(${rotate.toFixed(2)}deg) scale(${scale.toFixed(3)})`;
          }

          if (text) {
            const textTranslateY = progress * 10;
            text.style.transform = `translate3d(0, ${textTranslateY.toFixed(1)}px, 0)`;
          }

          const svgAccent = card.querySelector(".pillar-svg-accent");
          if (svgAccent) {
            const svgRotate = progress * 10;
            svgAccent.style.transform = `rotate(${svgRotate.toFixed(1)}deg) scale(1.06)`;
          }
        }
      });

      // 2. Dynamic Lottie speed boost on active scroll (authentic playful Duolingo responsiveness)
      if (Math.abs(scrollDelta) > 5) {
        const boostSpeed = Math.min(1 + Math.abs(scrollDelta) * 0.02, 1.4);
        if (window.__duoLottieInstances) {
          window.__duoLottieInstances.forEach(function (inst) {
            if (inst && typeof inst.setSpeed === "function") {
              inst.setSpeed(boostSpeed);
            }
          });
        }
      } else {
        if (window.__duoLottieInstances) {
          window.__duoLottieInstances.forEach(function (inst) {
            if (inst && typeof inst.setSpeed === "function") {
              inst.setSpeed(1.0);
            }
          });
        }
      }

      lastScrollY = currentScrollY;
      ticking = false;
    }

    window.addEventListener("scroll", function () {
      if (!ticking) {
        window.requestAnimationFrame(onScrollTick);
        ticking = true;
      }
    }, { passive: true });

    // Initial tick
    window.requestAnimationFrame(onScrollTick);
  }

  // Initialize scroll dynamics and Lottie animations when DOM is ready
  function initAllShowcaseAnimations() {
    try {
      initScrollDynamicsController();
    } catch (e) {
      console.error("Scroll dynamics error:", e);
    }
    try {
      initDuoShowcaseLottie();
    } catch (e) {
      console.error("Lottie init error:", e);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAllShowcaseAnimations);
  } else {
    initAllShowcaseAnimations();
  }
})();


