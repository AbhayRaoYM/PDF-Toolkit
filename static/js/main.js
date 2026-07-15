// Shared utilities — loaded on every page via base.html

// Mobile nav hamburger toggle
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("navToggle");
  const mobileNav = document.getElementById("mobileNav");
  if (toggle && mobileNav) {
    toggle.addEventListener("click", () => {
      mobileNav.classList.toggle("open");
    });
  }

  // Re-render lucide icons after any dynamic content changes
  if (window.lucide) lucide.createIcons();
});
