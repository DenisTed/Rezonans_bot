document.addEventListener("DOMContentLoaded", () => {
  const transition = document.getElementById("pageTransition");
  const duration = 900;

  initDropdowns();
  handlePageEnterAnimation(transition, duration);
  handlePageLeaveAnimation(transition, duration);
  updateAuthUI();
});

function initDropdowns() {
  const dropdowns = document.querySelectorAll(".dropdown");
  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector(".dropdown-toggle");
    if (!toggle) return;

    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.contains("open");
      closeAllDropdowns();
      if (!isOpen) dropdown.classList.add("open");
    });
  });

  document.addEventListener("click", closeAllDropdowns);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAllDropdowns();
  });
}

function closeAllDropdowns() {
  document.querySelectorAll(".dropdown").forEach(d => d.classList.remove("open"));
}

function handlePageEnterAnimation(transition, duration) {
  if (!transition) return;
  setTimeout(() => {
    transition.classList.remove("is-entering");
    transition.style.opacity = "0";
    transition.style.visibility = "hidden";
  }, duration);
}

function handlePageLeaveAnimation(transition, duration) {
  document.querySelectorAll(".js-page-link").forEach(link => {
    link.addEventListener("click", (e) => {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || href === "") return;

      e.preventDefault();
      transition.style.visibility = "visible";
      transition.style.opacity = "1";
      transition.classList.add("is-leaving");

      setTimeout(() => window.location.href = href, duration - 60);
    });
  });
}

function updateAuthUI() {
  const isLoggedIn = localStorage.getItem('isLoggedIn');
  const userName = localStorage.getItem('userName');
  const authBtn = document.getElementById('authButton');

  if (isLoggedIn === 'true' && userName && authBtn) {
    authBtn.href = 'profile.html';
    authBtn.classList.add('user-account-btn');
    authBtn.innerHTML = `
      <span style="margin-right: 8px;">👤</span>
      <span>${userName.toUpperCase()}</span>
    `;
  }
}

// Функції для сторінки бронювання (залишаються доступними)
window.generateHall = generateHall;
window.startPurchase = startPurchase;

function generateHall() { /* твоя логіка залу 13×23 */ }
function selectSeat(el) { /* твоя логіка */ }
function startPurchase(name) { /* оновлена з перевіркою авторизації */ }