document.addEventListener("DOMContentLoaded", () => {
  const transition = document.getElementById("pageTransition");
  const pageLinks = document.querySelectorAll(".js-page-link");
  const transitionDuration = 900;

  initDropdowns();
  handlePageEnterAnimation(transition, transitionDuration);
  handlePageLeaveAnimation(pageLinks, transition, transitionDuration);
});

function initDropdowns() {
  const dropdowns = document.querySelectorAll(".dropdown");

  dropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector(".dropdown-toggle");
    const menu = dropdown.querySelector(".dropdown-menu");

    if (!toggle || !menu) {
      return;
    }

    toggle.addEventListener("click", (event) => {
      event.stopPropagation();

      const isOpen = dropdown.classList.contains("open");

      closeAllDropdowns();

      if (!isOpen) {
        dropdown.classList.add("open");
        toggle.setAttribute("aria-expanded", "true");
      }
    });
  });

  document.addEventListener("click", () => {
    closeAllDropdowns();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeAllDropdowns();
    }
  });
}

function closeAllDropdowns() {
  const dropdowns = document.querySelectorAll(".dropdown");

  dropdowns.forEach((dropdown) => {
    dropdown.classList.remove("open");

    const toggle = dropdown.querySelector(".dropdown-toggle");
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

function handlePageEnterAnimation(transition, transitionDuration) {
  if (!transition || !transition.classList.contains("is-entering")) {
    return;
  }

  document.body.style.overflow = "hidden";

  window.setTimeout(() => {
    transition.classList.remove("is-entering");
    transition.style.opacity = "0";
    transition.style.visibility = "hidden";
    document.body.style.overflow = "";
  }, transitionDuration);
}

function handlePageLeaveAnimation(pageLinks, transition, transitionDuration) {
  if (!pageLinks.length || !transition) {
    return;
  }

  let isNavigating = false;

  pageLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href");

      if (!href || href.startsWith("#") || isNavigating) {
        return;
      }

      event.preventDefault();
      isNavigating = true;

      closeAllDropdowns();
      document.body.style.overflow = "hidden";
      transition.classList.remove("is-entering");
      transition.classList.add("is-leaving");
      transition.style.opacity = "1";
      transition.style.visibility = "visible";

      window.setTimeout(() => {
        window.location.href = href;
      }, transitionDuration - 60);
    });
  });
}
function generateHall() {
    const hall = document.getElementById('cinema-hall');
    if (!hall) return;

    const rows = 13;
    const seatsPerRow = 23; // 13 * 23 = 299 місць

    for (let i = 1; i <= rows; i++) {
        const rowElement = document.createElement('div');
        rowElement.className = 'hall-row';
        
        // Додаємо номер ряду зліва
        const rowNum = document.createElement('span');
        rowNum.className = 'row-number';
        rowNum.innerText = i;
        rowElement.appendChild(rowNum);

        for (let j = 1; j <= seatsPerRow; j++) {
            const seat = document.createElement('div');
            seat.className = 'seat-item';
            seat.dataset.row = i;
            seat.dataset.seat = j;
            seat.dataset.price = i <= 5 ? 500 : 350; // Перші 5 рядів дорожчі

            seat.addEventListener('click', () => selectSeat(seat));
            rowElement.appendChild(seat);
        }
        hall.appendChild(rowElement);
    }
}

function selectSeat(el) {
    document.querySelectorAll('.seat-item.selected').forEach(s => s.classList.remove('selected'));
    el.classList.add('selected');
    
    document.getElementById('res-row').innerText = el.dataset.row;
    document.getElementById('res-seat').innerText = el.dataset.seat;
    document.getElementById('res-price').innerText = el.dataset.price;
    document.getElementById('confirmBooking').disabled = false;
}

document.addEventListener('DOMContentLoaded', generateHall);

function startPurchase(name) {
  const confirmAction = confirm(`Бажаєте перейти до вибору місць на виставу "${name}"?`);
  if(confirmAction) {
    alert("Модуль вибору місць зараз у розробці. Дякуємо за терпіння!");
  }
}
document.addEventListener("DOMContentLoaded", () => {
  const transition = document.getElementById("pageTransition");
  const pageLinks = document.querySelectorAll(".js-page-link");
  const transitionDuration = 900;

  // 1. Ініціалізація систем
  initDropdowns();
  handlePageEnterAnimation(transition, transitionDuration);
  handlePageLeaveAnimation(pageLinks, transition, transitionDuration);
  
  // 2. Логіка залу (тільки якщо ми на сторінці бронювання)
  if (document.getElementById('cinema-hall')) {
    generateHall();
  }

  // 3. Перевірка авторизації (оновлення кнопок на всіх сторінках)
  updateAuthUI();
});

// --- ЛОГІКА АВТОРИЗАЦІЇ ---
function updateAuthUI() {
  const isLoggedIn = localStorage.getItem('isLoggedIn');
  const userName = localStorage.getItem('userName');
  
  // Шукаємо посилання на вхід (у меню або кнопках)
  const authLinks = document.querySelectorAll('a[href="auth.html"], .hero-btn[href="auth.html"]');
  
  if (isLoggedIn === 'true' && userName) {
    authLinks.forEach(link => {
      link.href = 'profile.html';
      link.innerHTML = `<span>${userName.toUpperCase()}</span>`;
      link.classList.add('logged-in'); // Можна додати стиль золотого кольору в CSS
    });
  }
}

// --- ЛОГІКА DROPDOWNS ---
function initDropdowns() {
  const dropdowns = document.querySelectorAll(".dropdown");
  dropdowns.forEach((dropdown) => {
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
}

function closeAllDropdowns() {
  document.querySelectorAll(".dropdown").forEach(d => d.classList.remove("open"));
}

// --- АНІМАЦІЇ ПЕРЕХОДУ ---
function handlePageEnterAnimation(transition, duration) {
  if (!transition) return;
  document.body.style.overflow = "hidden";
  setTimeout(() => {
    transition.classList.remove("is-entering");
    transition.style.opacity = "0";
    transition.style.visibility = "hidden";
    document.body.style.overflow = "";
  }, duration);
}

function handlePageLeaveAnimation(pageLinks, transition, duration) {
  pageLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || href === "") return;

      event.preventDefault();
      document.body.style.overflow = "hidden";
      transition.style.visibility = "visible";
      transition.style.opacity = "1";
      transition.classList.add("is-leaving");

      setTimeout(() => { window.location.href = href; }, duration - 50);
    });
  });
}

// --- ЛОГІКА ЗАЛУ ---
function generateHall() {
  const hall = document.getElementById('cinema-hall');
  const rows = 13;
  const seatsPerRow = 23;

  for (let i = 1; i <= rows; i++) {
    const rowElement = document.createElement('div');
    rowElement.className = 'hall-row';
    
    const rowNum = document.createElement('span');
    rowNum.className = 'row-number';
    rowNum.innerText = i;
    rowElement.appendChild(rowNum);

    for (let j = 1; j <= seatsPerRow; j++) {
      const seat = document.createElement('div');
      seat.className = 'seat-item';
      seat.dataset.row = i;
      seat.dataset.seat = j;
      seat.dataset.price = i <= 5 ? 500 : 350;
      seat.addEventListener('click', () => selectSeat(seat));
      rowElement.appendChild(seat);
    }
    hall.appendChild(rowElement);
  }
}

function selectSeat(el) {
  document.querySelectorAll('.seat-item.selected').forEach(s => s.classList.remove('selected'));
  el.classList.add('selected');
  
  const resRow = document.getElementById('res-row');
  const resSeat = document.getElementById('res-seat');
  const resPrice = document.getElementById('res-price');
  const confirmBtn = document.getElementById('confirmBooking');

  if (resRow) resRow.innerText = el.dataset.row;
  if (resSeat) resSeat.innerText = el.dataset.seat;
  if (resPrice) resPrice.innerText = el.dataset.price;
  if (confirmBtn) confirmBtn.disabled = false;
}

// --- ЛОГІКА ПОКУПКИ ---
function startPurchase(name) {
  // Перевірка: чи увійшов користувач перед покупкою?
  if (localStorage.getItem('isLoggedIn') !== 'true') {
    alert("Щоб обрати квитки, будь ласка, увійдіть у свій кабінет.");
    window.location.href = 'auth.html';
    return;
  }
  
  // Якщо залогінений — ведемо на сторінку вибору місць (наприклад, зал у тебе в map.html або окремо)
  window.location.href = 'booking.html?performance=' + encodeURIComponent(name);
}
const grid = document.getElementById('seatsGrid');
const rows = 8;
const cols = 12;
const pricePerSeat = 250;
let selectedSeats = []; // Масив для зберігання обраних місць

// Генерація залу
for (let r = 1; r <= rows; r++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'seat-row';
    
    const label = document.createElement('div');
    label.className = 'row-label';
    label.innerText = `Ряд ${r}`;
    rowDiv.appendChild(label);

    for (let c = 1; c <= cols; c++) {
        const seat = document.createElement('div');
        seat.className = 'seat available';
        
        // Рандомно займаємо місця
        if (Math.random() < 0.1) seat.classList.add('occupied');

        seat.addEventListener('click', () => {
            if (seat.classList.contains('occupied')) return;
            
            const seatId = `Р${r}-М${c}`;
            
            if (seat.classList.contains('selected')) {
                // Видаляємо з вибору
                seat.classList.remove('selected');
                selectedSeats = selectedSeats.filter(item => item.id !== seatId);
            } else {
                // Додаємо до вибору
                seat.classList.add('selected');
                selectedSeats.push({ id: seatId, row: r, seat: c });
            }
            
            updateUI();
        });
        rowDiv.appendChild(seat);
    }
    grid.appendChild(rowDiv);
}

function updateUI() {
    const rowDisplay = document.getElementById('display-row');
    const seatDisplay = document.getElementById('display-seat');
    const priceDisplay = document.getElementById('display-price');
    const btn = document.getElementById('confirmBtn');

    if (selectedSeats.length > 0) {
        // Виводимо всі обрані місця гарними бейджами
        rowDisplay.innerHTML = `<div class="selected-list">${[...new Set(selectedSeats.map(s => s.row))].join(', ')}</div>`;
        seatDisplay.innerHTML = `<div class="selected-list">
            ${selectedSeats.map(s => `<span class="seat-badge">${s.seat}</span>`).join('')}
        </div>`;
        
        priceDisplay.innerText = selectedSeats.length * pricePerSeat;
        btn.classList.add('ready');
        btn.innerText = `ПРОДОВЖИТИ (${selectedSeats.length})`;
    } else {
        rowDisplay.innerText = '-';
        seatDisplay.innerText = '-';
        priceDisplay.innerText = '0';
        btn.classList.remove('ready');
        btn.innerText = 'ПРОДОВЖИТИ';
    }
}
payBtn.addEventListener('click', () => {
    if (selectedSeats.length === 0) return;

    // Отримуємо існуючі замовлення або створюємо порожній масив
    const allOrders = JSON.parse(localStorage.getItem('theatreOrders')) || [];

    const newOrder = {
        id: Date.now(),
        seats: [...selectedSeats],
        totalPrice: selectedSeats.length * price,
        status: 'pending', // Статус: очікує підтвердження адміном
        time: new Date().toLocaleTimeString()
    };

    allOrders.push(newOrder);
    localStorage.setItem('theatreOrders', JSON.stringify(allOrders));

    alert('Замовлення надіслано! Очікуйте підтвердження адміністратором.');
    
    // Очищуємо вибір
    selectedSeats = [];
    document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));
    renderSummary();
});