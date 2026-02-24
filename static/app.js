const toggle = document.querySelector(".liquid-toggle");
const config = {
  complete: 100,
  active: false,
  deviation: 2,
  alpha: 16,
  bounce: true,
  hue: 200,
  delta: true,
  bubble: true,
  mapped: false,
};

gsap.set(toggle, { "--complete": config.complete });
toggle.setAttribute("aria-pressed", "true");

const updateFilters = () => {
  gsap.set("#goo feGaussianBlur", { attr: { stdDeviation: config.deviation } });
  gsap.set("#goo feColorMatrix", {
    attr: { values: `1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 ${config.alpha} -10` },
  });
  toggle.style.setProperty("--complete", config.complete);
  toggle.style.setProperty("--hue", config.hue);
};

const switchThemeMode = (isDark) => {
  if (isDark) {
    document.body.classList.remove("light-mode");
  } else {
    document.body.classList.add("light-mode");
  }
};

const toggleState = async () => {
  toggle.dataset.pressed = true;
  if (config.bubble) toggle.dataset.active = true;

  await Promise.allSettled(
    !config.bounce
      ? toggle.getAnimations({ subtree: true }).map((a) => a.finished)
      : [],
  );

  const pressed = toggle.getAttribute("aria-pressed") === "true";

  gsap
    .timeline({
      onComplete: () => {
        gsap.delayedCall(0.05, () => {
          toggle.dataset.active = false;
          toggle.dataset.pressed = false;
          const newState = !toggle.matches("[aria-pressed=true]");
          toggle.setAttribute("aria-pressed", newState);
          switchThemeMode(newState);
        });
      },
    })
    .to(toggle, {
      "--complete": pressed ? 0 : 100,
      duration: 0.12,
      delay: config.bounce && config.bubble ? 0.18 : 0,
    });
};

toggle.addEventListener("click", toggleState);
updateFilters();

const proxy = document.createElement("div");
Draggable.create(proxy, {
  trigger: toggle,
  type: "x",
  onDragStart: function () {
    this.startX = this.x;
    toggle.dataset.active = true;
  },
  onDrag: function () {
    const pressed = toggle.matches("[aria-pressed=true]");
    let dragPercent = ((this.x - this.startX) / 60) * 100;
    let complete = pressed ? 100 + dragPercent : dragPercent;
    complete = Math.max(0, Math.min(100, complete));
    config.complete = complete;
    updateFilters();
  },
  onDragEnd: function () {
    toggle.dataset.active = false;
    const finalState = config.complete > 50;
    gsap.to(toggle, {
      "--complete": finalState ? 100 : 0,
      duration: 0.2,
      onComplete: () => {
        toggle.setAttribute("aria-pressed", finalState);
        switchThemeMode(finalState);
      },
    });
  },
});

function getUserAvatar() {
  return (
    localStorage.getItem("userProfilePic") ||
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
  );
}

const allThemes = [
  "theme-emerald",
  "theme-cyber",
  "theme-blue",
  "theme-purple",
  "theme-gold",
  "theme-red",
  "theme-lime",
  "theme-ice",
  "theme-obsidian",
  "theme-rgb",
];
let currentMovies = [];
let autoScrollInterval = null;
let autoScrollBound = false;
const AUTO_SCROLL_SPEED = 0.5;

// ✅ 3D ICON EFFECT — Applied to any .ai-n-logo element
function apply3DIconEffect(logoEl) {
  if (!logoEl || logoEl.dataset.tilt3d) return;
  logoEl.dataset.tilt3d = "true";

  logoEl.style.transition = "transform 0.1s ease, box-shadow 0.1s ease";
  logoEl.style.cursor = "default";
  logoEl.style.display = "inline-flex";
  logoEl.style.alignItems = "center";
  logoEl.style.justifyContent = "center";

  logoEl.addEventListener("mousemove", (e) => {
    const rect = logoEl.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) / (rect.width / 2);
    const dy = (e.clientY - cy) / (rect.height / 2);

    const rotX = -dy * 25;
    const rotY = dx * 25;
    const glow = `${dx * 4}px ${dy * 4}px 18px rgba(0,255,255,0.55)`;

    logoEl.style.transform = `perspective(300px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale(1.18)`;
    logoEl.style.boxShadow = glow;
    logoEl.style.textShadow = `${dx * 3}px ${dy * 3}px 10px rgba(0,255,255,0.8)`;
  });

  logoEl.addEventListener("mouseleave", () => {
    logoEl.style.transform = "perspective(300px) rotateX(0deg) rotateY(0deg) scale(1)";
    logoEl.style.boxShadow = "";
    logoEl.style.textShadow = "";
  });
}

// Apply 3D to static logo in header/navbar if present
function applyGlobal3DLogo() {
  document.querySelectorAll(".ai-n-logo").forEach(apply3DIconEffect);
}

window.addEventListener("load", () => {
  const bgMode = localStorage.getItem("bgMode");
  if (bgMode === "custom") {
    const bgUrl = "/static/wallpapers/current_bg.jpg?v=" + new Date().getTime();
    document.documentElement.style.setProperty("--bg-image", `url('${bgUrl}')`);
  }
  const savedTheme = localStorage.getItem("userTheme");
  if (savedTheme) {
    handleThemeChange(savedTheme, true);
    const themeSelect = document.getElementById("themeSelect");
    if (themeSelect) themeSelect.value = savedTheme;
  }
  const name = localStorage.getItem("userName");
  if (name) {
    const userNameField = document.getElementById("userName");
    const welcomeName = document.getElementById("welcomeName");
    if (userNameField) userNameField.value = name;
    if (welcomeName) welcomeName.innerText = name;
  }
  const email = localStorage.getItem("userEmail");
  const userEmailField = document.getElementById("userEmail");
  if (email && userEmailField) userEmailField.value = email;

  const savedPic = localStorage.getItem("userProfilePic");
  const displayPic = document.getElementById("displayProfilePic");
  if (savedPic && displayPic) displayPic.src = savedPic;

  handleModeChange(true);
  const modeSelect = document.getElementById("modeSelect");
  if (modeSelect && modeSelect.value === "movie") loadTrendingMovies();

  const neonLogo = document.getElementById("neon-logo");
  if (neonLogo) {
    neonLogo.style.flexShrink = "0";
    neonLogo.style.objectFit = "contain";
    neonLogo.style.aspectRatio = "1/1";
  }

  const inputField = document.getElementById("userInput");
  if (inputField) {
    const btn =
      inputField.nextElementSibling ||
      inputField.parentElement.querySelector("button");
    if (btn) {
      const icon = btn.querySelector("svg") || btn.querySelector("i") || btn;
      if (icon) icon.classList.add("send-icon-anim");
      btn.classList.add("send-btn-hover-effect");
    }
  }

  // Apply 3D to any existing logos on load
  applyGlobal3DLogo();

  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const targets = document.querySelectorAll(
    "h1, h2, .chat-name-tag, .card-text",
  );

  targets.forEach((element) => {
    element.addEventListener("mouseover", (event) => {
      const el = event.currentTarget;

      const hasChildElements = Array.from(el.childNodes).some(
        (n) => n.nodeType === Node.ELEMENT_NODE,
      );
      if (hasChildElements) return;

      const originalText = el.innerText;
      if (!originalText.trim()) return;

      if (el.dataset.interval) {
        clearInterval(Number(el.dataset.interval));
        delete el.dataset.interval;
      }

      let iteration = 0;
      const interval = setInterval(() => {
        el.innerText = originalText
          .split("")
          .map((letter, index) => {
            if (index < Math.floor(iteration)) return originalText[index];
            if (letter === " " || letter === "\n") return letter;
            return letters[Math.floor(Math.random() * 26)];
          })
          .join("");

        if (iteration >= originalText.length) {
          clearInterval(Number(el.dataset.interval));
          delete el.dataset.interval;
          el.innerText = originalText;
        }

        iteration += 1 / 3;
      }, 30);

      el.dataset.interval = String(interval);
    });
  });
});

function toggleDrawer() {
  const drawer = document.getElementById("drawer");
  const overlay = document.getElementById("drawer-overlay");
  const isOpen = drawer.classList.toggle("open");
  overlay.classList.toggle("active");
  document.body.style.overflow = isOpen ? "hidden" : "";
}

function handleThemeChange(theme, skipSave = false) {
  document.body.classList.remove(...allThemes);
  document.body.classList.add(theme);
  if (!skipSave) localStorage.setItem("userTheme", theme);
}

function changeProfilePic() {
  const fileInput = document.getElementById("profileUpload");
  if (fileInput.files && fileInput.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const imgData = e.target.result;
      const displayPic = document.getElementById("displayProfilePic");
      if (displayPic) displayPic.src = imgData;
      localStorage.setItem("userProfilePic", imgData);
      document.querySelectorAll(".chat-user-pic").forEach((img) => {
        img.src = imgData;
      });
    };
    reader.readAsDataURL(fileInput.files[0]);
  }
}

function saveProfile() {
  const userNameField = document.getElementById("userName");
  const name = userNameField ? userNameField.value || "User" : "User";
  localStorage.setItem("userName", name);

  const userEmailField = document.getElementById("userEmail");
  if (userEmailField) {
    localStorage.setItem("userEmail", userEmailField.value);
  }

  const welcomeName = document.getElementById("welcomeName");
  if (welcomeName) welcomeName.innerText = name;

  document
    .querySelectorAll(".user-name-label")
    .forEach((tag) => (tag.innerText = name));
}

function setThinkingState(isThinking) {
  const logo = document.getElementById("neon-logo");
  const text = document.getElementById("neon-name");
  const chatContainer = document.getElementById("chat-container");
  const bubbleId = "thinking-bubble-loader";

  if (logo && text) {
    if (isThinking) {
      logo.classList.add("spin");
      text.classList.add("text-thinking-multi");

      if (chatContainer && !document.getElementById(bubbleId)) {
        const bubbleRow = document.createElement("div");
        bubbleRow.id = bubbleId;
        bubbleRow.className = "chat-row assistant";
        bubbleRow.innerHTML = `
          <div class="chat-avatar-container">
             <div class="ai-avatar-multiglow"></div><div class="ai-n-logo">N</div>
          </div>
          <div class="msg-column">
             <div class="chat-name-tag">Neon AI</div>
             <div class="msg" style="padding: 15px 20px;">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
             </div>
          </div>`;
        chatContainer.appendChild(bubbleRow);
        // ✅ Apply 3D to newly created logo
        apply3DIconEffect(bubbleRow.querySelector(".ai-n-logo"));
        chatContainer.scrollTo({
          top: chatContainer.scrollHeight,
          behavior: "smooth",
        });
      }
    } else {
      logo.classList.remove("spin");
      text.classList.remove("text-thinking-multi");
      text.style.color = "var(--primary-glow)";

      const bubble = document.getElementById(bubbleId);
      if (bubble) bubble.remove();
    }
  }
}

async function changeWallpaper() {
  const fileInput = document.getElementById("bgUpload");
  if (!fileInput.files[0]) return;
  const file = fileInput.files[0];
  const reader = new FileReader();
  reader.onload = function (e) {
    document.documentElement.style.setProperty(
      "--bg-image",
      `url(${e.target.result})`,
    );
  };
  reader.readAsDataURL(file);
  setThinkingState(true);
  const formData = new FormData();
  formData.append("file", file);
  try {
    const res = await fetch("/upload-bg", { method: "POST", body: formData });
    const data = await res.json();
    setThinkingState(false);
    if (data.status === "success") {
      localStorage.setItem("bgMode", "custom");
      const bgDisplay = document.getElementById("bgNameDisplay");
      if (bgDisplay) bgDisplay.innerText = "Saved";
      addMsg("Wallpaper Secured.", "assistant");
    }
  } catch (e) {
    setThinkingState(false);
  }
}

function handleModeChange(isInit = false) {
  const select = document.getElementById("modeSelect");
  if (!select) return;

  const modeValue = select.value;
  const modeText = select.options[select.selectedIndex].text;

  const modeHints = {
    casual: "General assistant",
    movie: "Movies & shows",
    exam: "Exam & syllabus",
  };
  const modeHint = document.getElementById("mode-hint");
  if (modeHint) modeHint.innerText = modeHints[modeValue] || "";

  const neonName = document.getElementById("neon-name");
  if (neonName) neonName.innerText = modeText;

  const examUpload = document.getElementById("examUpload");
  if (examUpload) {
    examUpload.style.display = modeValue === "exam" ? "block" : "none";
  }

  const carousel = document.getElementById("movie-carousel");

  stopAutoScroll();
  autoScrollBound = false;

  if (carousel) {
    if (modeValue === "movie") {
      carousel.style.display = "block";
      loadTrendingMovies();
    } else {
      carousel.style.display = "none";
    }
  }

  if (!isInit) {
    const chatContainer = document.getElementById("chat-container");
    if (chatContainer) chatContainer.innerHTML = "";
    addMsg(`System switched to ${modeText}.`, "assistant");
  }
}

// ✅ FIX 1: Auto Scroll — smooth sub-pixel scrolling with rAF
function startAutoScroll() {
  const wrapper = document.querySelector(".cards-wrapper");
  if (!wrapper) return;
  stopAutoScroll();

  let exactScrollLeft = wrapper.scrollLeft;

  function smoothScroll() {
    if (!wrapper) return;

    // Sync if user manually scrolled
    if (Math.abs(exactScrollLeft - wrapper.scrollLeft) > 2) {
      exactScrollLeft = wrapper.scrollLeft;
    }

    exactScrollLeft += AUTO_SCROLL_SPEED;
    wrapper.scrollLeft = exactScrollLeft;

    if (wrapper.scrollLeft + wrapper.clientWidth >= wrapper.scrollWidth - 2) {
      wrapper.scrollLeft = 0;
      exactScrollLeft = 0;
    }

    autoScrollInterval = requestAnimationFrame(smoothScroll);
  }

  autoScrollInterval = requestAnimationFrame(smoothScroll);
}

function stopAutoScroll() {
  if (autoScrollInterval) {
    cancelAnimationFrame(autoScrollInterval);
    autoScrollInterval = null;
  }
}

function addTiltEffect() {
  const isMobile = window.innerWidth <= 768;
  if (isMobile) return;

  const cards = document.querySelectorAll(".movie-card-placeholder");
  cards.forEach((card) => {
    if (!card.querySelector(".card-shine")) {
      const shine = document.createElement("div");
      shine.className = "card-shine";
      card.appendChild(shine);
    }

    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -12;
      const rotateY = ((x - centerX) / centerX) * 12;

      card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;

      const shine = card.querySelector(".card-shine");
      if (shine) {
        shine.style.opacity = "1";
        shine.style.background = `linear-gradient(${135 + rotateY * 2}deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 60%)`;
      }
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = `perspective(800px) rotateX(0) rotateY(0) scale(1)`;
      const shine = card.querySelector(".card-shine");
      if (shine) shine.style.opacity = "0";
    });
  });
}

async function loadTrendingMovies() {
  const container = document.getElementById("cards-container");
  const wrapper = document.querySelector(".cards-wrapper");
  const carousel = document.getElementById("movie-carousel");

  if (!container) return;

  stopAutoScroll();

  const tmdbKey = localStorage.getItem("tmdbKey");

  if (!tmdbKey) {
    container.innerHTML = `<div class="card-text" style="padding: 20px;">Please set TMDB API Key in settings.</div>`;
    return;
  }
  container.innerHTML =
    '<div class="card-text" style="padding: 20px;">Loading trending...</div>';

  try {
    const res = await fetch(
      `https://api.themoviedb.org/3/trending/movie/week?api_key=${tmdbKey}`,
    );
    const data = await res.json();
    if (data.results && data.results.length > 0) {
      currentMovies = data.results;

      const cardsHTML = data.results
        .map((m, index) => {
          const posterUrl = m.poster_path
            ? `https://image.tmdb.org/t/p/w500${m.poster_path}`
            : "https://via.placeholder.com/500x750?text=No+Poster";
          return `<div class="movie-card-placeholder" onclick="openMovieDetails(${index}, event)"><img src="${posterUrl}" alt="${m.title}" onerror="this.src='https://via.placeholder.com/500x750?text=Error'"><div class="card-overlay"><span class="card-text">${m.title}</span></div></div>`;
        })
        .join("");

      container.innerHTML = cardsHTML;

      const cards = container.querySelectorAll(".movie-card-placeholder");
      gsap.fromTo(
        cards,
        { opacity: 0, y: 30, scale: 0.92 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.45,
          ease: "power3.out",
          stagger: 0.055,
          clearProps: "transform",
        },
      );

      setTimeout(() => addTiltEffect(), 100);

      setTimeout(() => {
        startAutoScroll();
        if (!autoScrollBound && wrapper) {
          wrapper.addEventListener("mouseenter", stopAutoScroll);
          wrapper.addEventListener("mouseleave", startAutoScroll);
          wrapper.addEventListener("touchstart", stopAutoScroll, {
            passive: true,
          });
          wrapper.addEventListener(
            "touchend",
            () => setTimeout(startAutoScroll, 2000),
            { passive: true },
          );
          autoScrollBound = true;
        }
      }, 500);
    } else {
      container.innerHTML =
        '<div class="card-text">No trending info available.</div>';
    }
  } catch (e) {
    container.innerHTML =
      '<div class="card-text" style="color:red;">Error fetching TMDB. Check connection/key.</div>';
  }
}

function openMovieDetails(index, event) {
  if (event) event.stopPropagation();

  const movie = currentMovies[index];
  if (!movie) return;

  document.body.classList.add("movie-chat-active");

  setTimeout(() => {
    const poster = movie.poster_path
      ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
      : null;
    const year = movie.release_date
      ? new Date(movie.release_date).getFullYear()
      : "N/A";
    const msgHtml = `<b>${movie.title}</b> (${year})<br><br><span style="font-size:0.9rem; opacity:0.8;">${movie.overview}</span><br><br>⭐ Rating: ${movie.vote_average}/10`;

    addMsg(msgHtml, "assistant", poster, "0s");
  }, 50);
}

const _carousel = document.getElementById("movie-carousel");
if (_carousel) {
  _carousel.addEventListener("click", () => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) return;

    const input = document.getElementById("userInput");
    if (document.activeElement === input) {
      input.blur();
      return;
    }

    document.body.classList.remove("movie-chat-active");

    _carousel.style.willChange = "transform, opacity";
    gsap.to(_carousel, {
      scale: 1,
      opacity: 1,
      duration: 0.5,
      ease: "back.out(1.4)",
      // ✅ FIX 2: Only clear transform & opacity, not display
      clearProps: "transform,opacity",
      onComplete: () => {
        _carousel.style.willChange = "auto";
      },
    });
  });
}

const userInputField = document.getElementById("userInput");
const movieCarousel = document.getElementById("movie-carousel");

if (userInputField) {
  userInputField.addEventListener("focus", () => {
    const isMobile = window.innerWidth <= 768;
    document.body.classList.add("movie-chat-active");

    gsap.to(userInputField, {
      scale: 1.02,
      boxShadow: "0 0 10px var(--primary-glow, rgba(0, 255, 255, 0.15))",
      borderColor: "var(--primary-glow, #0ff)",
      duration: 0.3,
    });

    if (movieCarousel && !isMobile) {
      movieCarousel.style.willChange = "transform, opacity";
      gsap.to(movieCarousel, {
        scale: 0.92,
        opacity: 0.4,
        duration: 0.5,
        ease: "power2.inOut",
      });
    }
  });

  userInputField.addEventListener("blur", () => {
    const isMobile = window.innerWidth <= 768;

    document.body.classList.remove("movie-chat-active");

    gsap.to(userInputField, {
      scale: 1,
      boxShadow: "inset 0 2px 5px rgba(0,0,0,0.2)",
      borderColor: "rgba(255,255,255,0.15)",
      duration: 0.3,
    });

    if (movieCarousel && !isMobile) {
      gsap.to(movieCarousel, {
        scale: 1,
        opacity: 1,
        duration: 0.5,
        ease: "back.out(1.4)",
        // ✅ FIX 3: Only clear transform & opacity, not all (fixes display:none bug)
        clearProps: "transform,opacity",
        onComplete: () => {
          movieCarousel.style.willChange = "auto";
        },
      });
    }
  });
}

async function typeWriter(element, html) {
  const tempDiv = document.createElement("div");
  tempDiv.innerHTML = html;

  element.innerHTML = "";

  const cursor = document.createElement("span");
  cursor.className = "cursor-blink";
  element.appendChild(cursor);

  async function typeNode(node, target) {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = node.textContent;

      const isCodeBlock =
        target.closest("pre") ||
        target.closest("code") ||
        target.classList.contains("instant-type");

      if (isCodeBlock) {
        target.insertBefore(document.createTextNode(text), cursor);
        const chatContainer = document.getElementById("chat-container");
        if (chatContainer)
          chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: "smooth",
          });
      } else {
        const chatContainer = document.getElementById("chat-container");
        for (let i = 0; i < text.length; i++) {
          target.insertBefore(document.createTextNode(text[i]), cursor);
          if (i % 8 === 0 && chatContainer) {
            chatContainer.scrollTo({
              top: chatContainer.scrollHeight,
              behavior: "smooth",
            });
          }
          await new Promise((r) => setTimeout(r, Math.random() * 5 + 2));
        }
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const newNode = document.createElement(node.tagName);
      Array.from(node.attributes).forEach((attr) => {
        newNode.setAttribute(attr.name, attr.value);
      });
      target.insertBefore(newNode, cursor);

      if (!["BR", "HR", "IMG", "INPUT"].includes(node.tagName)) {
        for (const child of Array.from(node.childNodes)) {
          await typeNode(child, newNode);
        }
      }
    }
  }

  try {
    for (const child of Array.from(tempDiv.childNodes)) {
      await typeNode(child, element);
    }
  } catch (err) {
    console.error("Typewriter error:", err);
    element.innerHTML = html;
  } finally {
    if (cursor && cursor.parentNode) cursor.remove();
  }
}

async function sendMessage() {
  const input = document.getElementById("userInput");
  const modeSelect = document.getElementById("modeSelect");
  if (!input || !modeSelect) return;

  const text = input.value.trim();
  const mode = modeSelect.value;

  if (!text) return;

  const sendBtn =
    input.nextElementSibling || input.parentElement.querySelector("button");
  if (sendBtn) {
    const icon =
      sendBtn.querySelector("svg") ||
      sendBtn.querySelector("i") ||
      sendBtn.querySelector(".send-icon-anim");
    if (icon) {
      icon.classList.remove("fly-away");
      void icon.offsetWidth;
      icon.classList.add("fly-away");
    }
  }

  addMsg(text, "user");
  input.value = "";
  setThinkingState(true);

  if (text.toLowerCase() === "show demo poster") {
    setTimeout(() => {
      setThinkingState(false);
      addMsg(
        "Here is a demo poster for testing.",
        "assistant",
        "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
      );
    }, 1500);
    return;
  }

  const startTime = performance.now();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        mode: mode,
      }),
    });

    const data = await res.json();
    setThinkingState(false);

    const endTime = performance.now();
    const latency = ((endTime - startTime) / 1000).toFixed(2) + "s";

    if (data.error) {
      addMsg("Error: " + data.error, "assistant", null, latency);
    } else {
      addMsg(
        data.response || "No response.",
        "assistant",
        data.poster_url,
        latency,
      );
    }
  } catch (e) {
    setThinkingState(false);
    console.error("Chat Error:", e);
    addMsg("Connection failed. Check server.", "assistant");
  }
}

function renderMessage(text) {
  if (!text) return "";

  text = text.replace(/\\n/g, "\n");

  const placeholders = [];

  text = text.replace(/```(\w+)?\s*([\s\S]*?)```/g, (_, lang, code) => {
    const safeCode = code
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    const placeholder = `__CODE_BLOCK_${placeholders.length}__`;

    const html = `
      <div class="code-block" style="background:#0b0f14; color:#e6f1ff; padding:12px; border-radius:8px; margin:10px 0; overflow-x:auto; border:1px solid rgba(255,255,255,0.1);">
        <pre class="instant-type" style="margin:0; white-space:pre; font-family:'JetBrains Mono', monospace; font-size:0.85rem;"><code>${safeCode}</code></pre>
      </div>`;
    placeholders.push(html);
    return placeholder;
  });

  text = text.replace(
    /`([^`]+)`/g,
    '<span style="background:rgba(255,255,255,0.1); padding:2px 5px; border-radius:4px; font-family:monospace;">$1</span>',
  );

  text = text.replace(/(?:\r\n|\r|\n)/g, "<br>");

  placeholders.forEach((html, index) => {
    text = text.replace(`__CODE_BLOCK_${index}__`, html);
  });

  return text;
}

function addMsg(text, type, posterUrl = null, latency = null) {
  const container = document.getElementById("chat-container");
  if (!container) return;

  const rowDiv = document.createElement("div");
  rowDiv.className = `chat-row ${type}`;

  let avatarHTML = "";
  let nameTag = "";

  if (type === "user") {
    const storedPic = getUserAvatar();
    const userNameField = document.getElementById("userName");
    const storedName = userNameField ? userNameField.value || "User" : "User";
    nameTag = `<div class="chat-name-tag user-name-label">${storedName}</div>`;
    avatarHTML = `<div class="user-avatar-glow"></div><img src="${storedPic}" class="chat-avatar-img chat-user-pic">`;
  } else {
    nameTag = `<div class="chat-name-tag">Neon AI</div>`;
    avatarHTML = `<div class="ai-avatar-multiglow"></div><div class="ai-n-logo">N</div>`;
  }

  if (!posterUrl) {
    const urlRegex =
      /(https?:\/\/[^\s]+?\.(jpg|jpeg|png|gif|webp)(\?[^\s]+)?)/i;
    const match = text.match(urlRegex);
    if (match) {
      posterUrl = match[0];
      text = text.replace(match[0], "").trim();
    }
  }

  let cleanText = text;
  if (posterUrl && posterUrl !== "null") {
    cleanText = cleanText.replace(posterUrl, "").trim();
  }

  let messageContent = renderMessage(cleanText);
  let extraContent = "";

  if (posterUrl && posterUrl !== "null" && posterUrl !== "undefined") {
    extraContent = `<br><img src="${posterUrl}" class="chat-poster" alt="Movie Poster" loading="lazy">`;
  }

  let metaInfo = "";
  if (latency) {
    metaInfo = `<div style="font-size: 0.7rem; opacity: 0.5; margin-top: 5px; text-align: right;">⚡ ${latency}</div>`;
  }

  rowDiv.innerHTML = `<div class="chat-avatar-container">${avatarHTML}</div><div class="msg-column">${nameTag}<div class="msg"></div>${metaInfo}</div>`;

  container.appendChild(rowDiv);

  // ✅ Apply 3D effect to newly added AI logo in chat
  if (type === "assistant") {
    const newLogo = rowDiv.querySelector(".ai-n-logo");
    if (newLogo) apply3DIconEffect(newLogo);
  }

  const msgDiv = rowDiv.querySelector(".msg");

  if (type === "assistant" && !posterUrl) {
    typeWriter(msgDiv, messageContent + extraContent);
  } else {
    msgDiv.innerHTML = messageContent + extraContent;
  }

  requestAnimationFrame(() => {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  });
}

async function saveAllKeys() {
  const apiKeyInput = document.getElementById("apiKeyInput");
  const tmdbKeyInput = document.getElementById("tmdbKeyInput");

  const tKey = apiKeyInput ? apiKeyInput.value.trim() : "";
  const mKey = tmdbKeyInput ? tmdbKeyInput.value.trim() : "";

  setThinkingState(true);
  if (mKey) localStorage.setItem("tmdbKey", mKey);
  if (tKey)
    await fetch("/set-api-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: tKey }),
    });
  if (mKey)
    await fetch("/set-tmdb-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: mKey }),
    });
  setThinkingState(false);
  addMsg("Keys Updated (Trending Now Active).", "assistant");

  const modeSelect = document.getElementById("modeSelect");
  if (modeSelect && modeSelect.value === "movie") loadTrendingMovies();
}

async function removeAllKeys() {
  if (!confirm("Remove all API keys?")) return;
  localStorage.removeItem("tmdbKey");
  await fetch("/set-api-key", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: "" }),
  });
  await fetch("/set-tmdb-key", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: "" }),
  });
  const apiKeyInput = document.getElementById("apiKeyInput");
  const tmdbKeyInput = document.getElementById("tmdbKeyInput");
  if (apiKeyInput) apiKeyInput.value = "";
  if (tmdbKeyInput) tmdbKeyInput.value = "";
  addMsg("Keys Removed. Offline Mode.", "assistant");
  loadTrendingMovies();
}

async function uploadPDF() {
  const fileInput = document.getElementById("pdfFile");
  if (!fileInput || !fileInput.files[0]) return;

  const fileNameDisplay = document.getElementById("fileNameDisplay");
  if (fileNameDisplay) fileNameDisplay.innerText = fileInput.files[0].name;

  addMsg(`Uploading PDF...`, "assistant");
  setThinkingState(true);
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  try {
    const res = await fetch("/upload-pdf", { method: "POST", body: formData });
    const data = await res.json();
    setThinkingState(false);
    addMsg(
      data.status === "success" ? "PDF Indexed!" : "Error: " + data.message,
      "assistant",
    );
  } catch (e) {
    setThinkingState(false);
  }
}

async function deletePDF() {
  const res = await fetch("/delete-pdf", { method: "POST" });
  const data = await res.json();
  addMsg(data.status === "success" ? "PDF Deleted." : "Error.", "assistant");
}

async function resetExamDB() {
  if (!confirm("Reset Exam Memory?")) return;
  const res = await fetch("/reset-exam-db", { method: "POST" });
  const data = await res.json();
  addMsg(data.status === "success" ? "Database Reset." : "Error.", "assistant");
}

function handleEnter(e) {
  if (e.key === "Enter") {
    e.preventDefault();
    sendMessage();
  }
}