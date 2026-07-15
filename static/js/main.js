// Shared utilities — loaded on every page via base.html

// Highlight active nav link (handles exact and prefix matches)
(function () {
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    if (href && href !== "/" && path.startsWith(href)) {
      link.classList.add("active");
    }
  });
})();
