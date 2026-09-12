(function () {
  const toggle = document.querySelector("[data-menu-toggle]");
  const mobileNav = document.querySelector("[data-mobile-nav]");
  if (toggle && mobileNav) {
    toggle.addEventListener("click", function () {
      const open = mobileNav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.querySelectorAll(".reveal").forEach(function (el, i) {
    el.style.animationDelay = (i * 60) + "ms";
  });

  const root = document.querySelector("[data-slider]");
  if (!root) return;

  const viewport = root.querySelector(".slider-viewport");
  const track = root.querySelector(".slider-track");
  const cards = Array.from(root.querySelectorAll(".slider-card"));
  const thumbs = Array.from(root.querySelectorAll("[data-thumbs] .thumb"));
  const timerBar = root.querySelector("[data-timer]");
  const currentEl = root.querySelector("[data-current]");
  if (!viewport || !track || !cards.length) return;

  let index = 0;
  let timer;
  let startX = 0;
  let deltaX = 0;
  let dragging = false;
  const INTERVAL = 4800;

  function layout() {
    const card = cards[index];
    const gap = parseFloat(getComputedStyle(track).gap) || 18;
    const viewportBox = viewport.getBoundingClientRect();
    const cardBox = card.getBoundingClientRect();
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
    if (activeThumb && activeThumb.scrollIntoView) {
      activeThumb.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
    void cardBox;
    void viewportBox;
  }

  function restartTimer() {
    if (!timerBar) return;
    timerBar.classList.remove("is-run");
    void timerBar.offsetWidth;
    timerBar.classList.add("is-run");
  }

  function go(next) {
    index = (next + cards.length) % cards.length;
    layout();
    restartTimer();
  }

  function play() {
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

  root.querySelector("[data-prev]")?.addEventListener("click", function () {
    go(index - 1);
    play();
  });
  root.querySelector("[data-next]")?.addEventListener("click", function () {
    go(index + 1);
    play();
  });
  thumbs.forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      go(Number(thumb.getAttribute("data-goto") || 0));
      play();
    });
  });

  viewport.addEventListener("mouseenter", pause);
  viewport.addEventListener("mouseleave", play);

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
    play();
  });

  window.addEventListener("resize", layout);
  window.addEventListener("load", layout);
  layout();
  play();
})();
