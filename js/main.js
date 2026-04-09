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