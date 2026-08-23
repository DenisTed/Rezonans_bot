/* =====================================================================
   ТЕАТР «РЕЗОНАНС» — спільна логіка сайту
   Мобільне меню (бургер) + стрічка вистав (data.json) + форма кастингу.
   ===================================================================== */
(function () {
  "use strict";

  // Куди надсилати заявки з кастингу.
  // Зараз — той самий Google Apps Script, що й бронювання.
  // Щоб заявки зберігалися, у скрипт треба додати обробку action=saveCasting.
  // Можна замінити на будь-який інший ендпоінт (напр. URL Google-форми).
  var CASTING_URL = "https://script.google.com/macros/s/AKfycbyEUuctwPk1oMzByss1Ex-wYJ_ym2PrKwob9fb3wEe7HYJXKKQfakliWawx2CHJHwRc/exec";

  document.addEventListener("DOMContentLoaded", function () {
    wireNav();
    wireCastingForm();

    if (document.getElementById("showsScroll")) {
      fetch("data.json")
        .then(function (r) { return r.json(); })
        .then(function (data) { renderShows(data.performances || []); })
        .catch(function (e) { console.error("Не вдалося завантажити data.json:", e); });
    }
  });

  /* ---------- МОБІЛЬНЕ МЕНЮ (бургер) ---------- */
  function wireNav() {
    var bar = document.querySelector(".topbar");
    var nav = bar && bar.querySelector(".nav");
    if (!bar || !nav) return;

    var burger = document.createElement("button");
    burger.className = "nav-burger";
    burger.type = "button";
    burger.setAttribute("aria-label", "Меню");
    burger.innerHTML = "<span></span><span></span><span></span>";
    bar.insertBefore(burger, nav);

    burger.addEventListener("click", function () {
      nav.classList.toggle("is-open");
      burger.classList.toggle("is-open");
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("is-open");
        burger.classList.remove("is-open");
      });
    });
  }

  /* ---------- СТРІЧКА ВИСТАВ ---------- */
  function renderShows(list) {
    var root = document.getElementById("showsScroll");
    if (!list.length) return;

    root.innerHTML = list.map(function (p) {
      return '<a class="show-card" href="' + esc(p.link || "afisha.html") + '">' +
        '<div class="show-card__poster"' + (p.image ? ' style="background-image:url(\'' + p.image + '\')"' : "") + '></div>' +
        '<div class="show-card__body">' +
          '<span class="show-card__date">' + esc(p.dateLabel || p.date || "") + (p.time ? " · " + esc(p.time) : "") + "</span>" +
          '<h3 class="show-card__title">' + esc(p.title) + "</h3>" +
          '<p class="show-card__genre">' + esc(p.genre || "") + "</p>" +
          '<span class="show-card__btn">Детальніше</span>' +
        "</div></a>";
    }).join("");
  }

  /* ---------- ФОРМА ЗАЯВКИ НА КАСТИНГ ---------- */
  function wireCastingForm() {
    var form = document.getElementById("castingForm");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = document.getElementById("cName").value.trim();
      var phone = document.getElementById("cPhone").value.trim();
      var age = document.getElementById("cAge").value.trim();
      var about = document.getElementById("cAbout").value.trim();
      var btn = document.getElementById("cSubmit");
      var msg = document.getElementById("castingMsg");

      if (!name || !phone) return;
      btn.disabled = true;
      btn.textContent = "Надсилання...";

      var body = new URLSearchParams();
      body.append("action", "saveCasting");
      body.append("id", Date.now());
      body.append("name", name);
      body.append("phone", phone);
      body.append("age", age);
      body.append("about", about);

      fetch(CASTING_URL, { method: "POST", mode: "no-cors", body: body })
        .catch(function () {})
        .finally(function () {
          msg.style.display = "block";
          msg.textContent = "Дякуємо! Заявку прийнято — ми зв'яжемося з тобою найближчим часом.";
          form.reset();
          btn.disabled = false;
          btn.textContent = "Надіслати заявку";
        });
    });
  }

  /* ---------- утиліта ---------- */
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
})();
