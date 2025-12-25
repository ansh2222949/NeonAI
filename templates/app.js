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
      : []
  );

  const pressed = toggle.matches("[aria-pressed=true]");

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

window.addEventListener("load", () => {
  const bgMode = localStorage.getItem("bgMode");
  if (bgMode === "custom") {
    const bgUrl = "/static/wallpapers/current_bg.jpg?v=" + new Date().getTime();
    document.documentElement.style.setProperty("--bg-image", `url('${bgUrl}')`);
  }
  const savedTheme = localStorage.getItem("userTheme");
  if (savedTheme) {
    handleThemeChange(savedTheme, true);
    document.getElementById("themeSelect").value = savedTheme;
  }
  const name = localStorage.getItem("userName");
  if (name) {
    document.getElementById("userName").value = name;
    document.getElementById("welcomeName").innerText = name;
  }
  const email = localStorage.getItem("userEmail");
  if (email) document.getElementById("userEmail").value = email;
  const savedPic = localStorage.getItem("userProfilePic");
  if (savedPic) document.getElementById("displayProfilePic").src = savedPic;

  handleModeChange(true);
  if (document.getElementById("modeSelect").value === "movie")
    loadTrendingMovies();
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
      document.getElementById("displayProfilePic").src = imgData;
      localStorage.setItem("userProfilePic", imgData);
      document.querySelectorAll(".chat-user-pic").forEach((img) => {
        img.src = imgData;
      });
    };
    reader.readAsDataURL(fileInput.files[0]);
  }
}
function saveProfile() {
  const name = document.getElementById("userName").value || "User";
  localStorage.setItem("userName", name);
  localStorage.setItem("userEmail", document.getElementById("userEmail").value);
  document.getElementById("welcomeName").innerText = name;
  document
    .querySelectorAll(".user-name-label")
    .forEach((tag) => (tag.innerText = name));
}
function setThinkingState(isThinking) {
  const logo = document.getElementById("neon-logo");
  const text = document.getElementById("neon-name");
  if (isThinking) {
    logo.classList.add("spin");
    text.classList.add("text-thinking-multi");
  } else {
    logo.classList.remove("spin");
    text.classList.remove("text-thinking-multi");
    text.style.color = "var(--primary-glow)";
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
      `url(${e.target.result})`
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
      document.getElementById("bgNameDisplay").innerText = "Saved";
      addMsg("Wallpaper Secured.", "assistant");
    }
  } catch (e) {
    setThinkingState(false);
  }
}

function handleModeChange(isInit = false) {
  const select = document.getElementById("modeSelect");
  const modeValue = select.value;
  const modeText = select.options[select.selectedIndex].text;
  document.getElementById("neon-name").innerText = modeText;
  document.getElementById("examUpload").style.display =
    modeValue === "exam" ? "block" : "none";
  const carousel = document.getElementById("movie-carousel");

  stopAutoScroll();
  if (modeValue === "movie") {
    carousel.style.display = "block";
    loadTrendingMovies();
  } else {
    carousel.style.display = "none";
  }

  if (!isInit) {
    document.getElementById("chat-container").innerHTML = "";
    addMsg(`System switched to ${modeText}.`, "assistant");
  }
}

function startAutoScroll() {
  const wrapper = document.querySelector(".cards-wrapper");
  if (!wrapper) return;
  stopAutoScroll();

  autoScrollInterval = setInterval(() => {
    wrapper.scrollLeft += AUTO_SCROLL_SPEED;
    if (wrapper.scrollLeft + wrapper.clientWidth >= wrapper.scrollWidth - 5) {
      wrapper.scrollLeft = 0;
    }
  }, 16);
}

function stopAutoScroll() {
  if (autoScrollInterval) {
    clearInterval(autoScrollInterval);
    autoScrollInterval = null;
  }
}

async function loadTrendingMovies() {
  const container = document.getElementById("cards-container");
  const wrapper = document.querySelector(".cards-wrapper");
  const tmdbKey = localStorage.getItem("tmdbKey");

  if (!tmdbKey) {
    container.innerHTML = `<div class="card-text" style="padding: 20px;"> Please set TMDB API Key in settings.</div>`;
    return;
  }
  container.innerHTML =
    '<div class="card-text" style="padding: 20px;">Loading trending...</div>';

  try {
    const res = await fetch(
      `https://api.themoviedb.org/3/trending/movie/week?api_key=${tmdbKey}`
    );
    const data = await res.json();
    if (data.results && data.results.length > 0) {
      currentMovies = data.results;
      container.innerHTML = "";
      data.results.forEach((m, index) => {
        const posterUrl = m.poster_path
          ? `https://image.tmdb.org/t/p/w500${m.poster_path}`
          : "https://via.placeholder.com/500x750?text=No+Poster";
        container.innerHTML += `<div class="movie-card-placeholder" onclick="openMovieDetails(${index})"><img src="${posterUrl}" alt="${m.title}" onerror="this.src='https://via.placeholder.com/500x750?text=Error'"><div class="card-overlay"><span class="card-text">${m.title}</span></div></div>`;
      });

      setTimeout(() => {
        startAutoScroll();
        if (!autoScrollBound) {
          wrapper.addEventListener("mouseenter", stopAutoScroll);
          wrapper.addEventListener("mouseleave", startAutoScroll);
          wrapper.addEventListener("touchstart", stopAutoScroll);
          wrapper.addEventListener("touchend", () =>
            setTimeout(startAutoScroll, 2000)
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

function openMovieDetails(index) {
  const movie = currentMovies[index];
  if (!movie) return;
  document.body.classList.add("movie-chat-active");
  const poster = movie.poster_path
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : null;
  const msgHtml = `<b>${movie.title}</b> (${new Date(
    movie.release_date
  ).getFullYear()})<br><br><span style="font-size:0.9rem; opacity:0.8;">${
    movie.overview
  }</span><br><br>⭐ Rating: ${movie.vote_average}/10`;
  addMsg(msgHtml, "assistant", poster);
}

let isInputFocused = false;
const userInputField = document.getElementById("userInput");

userInputField.addEventListener("focus", () => {
  isInputFocused = true;
  document.body.classList.add("movie-chat-active");
});

userInputField.addEventListener("blur", () => {
  isInputFocused = false;
  setTimeout(() => {
    if (!isInputFocused) {
      // document.body.classList.remove("movie-chat-active");
    }
  }, 200);
});

async function sendMessage() {
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (!text) return;
  addMsg(text, "user");
  input.value = "";
  setThinkingState(true);
  if (text.toLowerCase() === "show demo poster") {
    setTimeout(() => {
      setThinkingState(false);
      addMsg(
        "Here is a demo poster for testing.",
        "assistant",
        "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
      );
    }, 1500);
    return;
  }
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        mode: document.getElementById("modeSelect").value,
      }),
    });
    const data = await res.json();
    setThinkingState(false);
    addMsg(data.response, "assistant", data.poster_url);
  } catch (e) {
    setThinkingState(false);
    addMsg("Connection failed......", "assistant");
  }
}

function addMsg(text, type, posterUrl = null) {
  const container = document.getElementById("chat-container");
  const rowDiv = document.createElement("div");
  rowDiv.className = `chat-row ${type}`;
  let avatarHTML = "";
  let nameTag = "";
  if (type === "user") {
    const storedPic = getUserAvatar();
    const storedName = document.getElementById("userName").value || "User";
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
  let messageContent = cleanText.replace(/\n/g, "<br>");
  if (posterUrl && posterUrl !== "null" && posterUrl !== "undefined") {
    messageContent += `<img src="${posterUrl}" class="chat-poster" alt="Movie Poster">`;
  }
  rowDiv.innerHTML = `<div class="chat-avatar-container">${avatarHTML}</div><div class="msg-column">${nameTag}<div class="msg">${messageContent}</div></div>`;
  container.appendChild(rowDiv);
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

async function saveAllKeys() {
  const tKey = document.getElementById("apiKeyInput").value.trim();
  const mKey = document.getElementById("tmdbKeyInput").value.trim();
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
  if (document.getElementById("modeSelect").value === "movie")
    loadTrendingMovies();
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
  document.getElementById("apiKeyInput").value = "";
  document.getElementById("tmdbKeyInput").value = "";
  addMsg("Keys Removed. Offline Mode.", "assistant");
  loadTrendingMovies();
}
async function uploadPDF() {
  const fileInput = document.getElementById("pdfFile");
  if (!fileInput.files[0]) return;
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
      "assistant"
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
