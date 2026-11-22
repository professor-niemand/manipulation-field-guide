/* Small enhancements. The site works without this script. No tracking, no network calls. */
(function () {
  var root = document.documentElement;
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  // Theme toggle: follows the system setting until the visitor picks one.
  var tbtn = document.getElementById("theme-toggle"), tlabel = document.getElementById("theme-label");
  function isDark() {
    var t = root.getAttribute("data-theme");
    if (t) return t === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function paintTheme() { if (tlabel) tlabel.textContent = isDark() ? "Light mode" : "Dark mode"; }
  if (tbtn) {
    tbtn.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next); store("theme", next); paintTheme();
    });
    paintTheme();
  }

  // Mobile menu.
  var mbtn = document.getElementById("menu-toggle"), nav = document.getElementById("site-nav");
  if (mbtn && nav) {
    mbtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open"); mbtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Quick exit: button or Esc pressed twice. Replaces this page in the tab history.
  var qe = document.getElementById("quick-exit");
  function leave() { var u = (qe && qe.getAttribute("data-exit")) || "https://www.bbc.co.uk/weather"; window.location.replace(u); }
  if (qe) qe.addEventListener("click", function (e) { e.preventDefault(); leave(); });
  var lastEsc = 0;
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { var n = Date.now(); if (n - lastEsc < 900) { leave(); } lastEsc = n; }
  });

  // Back to top.
  var top = document.getElementById("to-top");
  if (top) top.addEventListener("click", function (e) { e.preventDefault(); window.scrollTo(0, 0); });

  // Techniques: search, expand/collapse, open the entry named in the address.
  var tools = document.getElementById("tech-tools");
  var entries = Array.prototype.slice.call(document.querySelectorAll("details.tech"));
  function openFromHash() {
    var id = decodeURIComponent((location.hash || "").slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (el && el.tagName === "DETAILS") { el.hidden = false; el.open = true; el.scrollIntoView(); }
  }
  if (tools && entries.length) {
    tools.hidden = false;
    var input = document.getElementById("tech-search"), count = document.getElementById("tech-count");
    function filter() {
      var q = input.value.trim().toLowerCase(), shown = 0;
      entries.forEach(function (d) {
        var ok = !q || d.getAttribute("data-search").indexOf(q) !== -1;
        d.hidden = !ok; if (ok) shown++;
        if (q && ok) d.open = true;
      });
      Array.prototype.forEach.call(document.querySelectorAll(".group"), function (g) {
        g.hidden = !g.querySelector("details.tech:not([hidden])");
      });
      Array.prototype.forEach.call(document.querySelectorAll(".category"), function (c) {
        c.hidden = !c.querySelector("details.tech:not([hidden])");
      });
      count.textContent = q ? (shown + " of " + entries.length + " techniques match") : "";
    }
    input.addEventListener("input", filter);
    document.getElementById("expand-all").addEventListener("click", function () { entries.forEach(function (d) { if (!d.hidden) d.open = true; }); });
    document.getElementById("collapse-all").addEventListener("click", function () { entries.forEach(function (d) { d.open = false; }); });
    window.addEventListener("hashchange", openFromHash);
    window.addEventListener("beforeprint", function () { entries.forEach(function (d) { d.open = true; }); });
    openFromHash();
  }

  // Help page: filter UK / anywhere else.
  var hp = document.getElementById("help-filter");
  if (hp) {
    hp.hidden = false;
    var btns = hp.querySelectorAll("button");
    Array.prototype.forEach.call(btns, function (b) {
      b.addEventListener("click", function () {
        var mode = b.getAttribute("data-mode");
        Array.prototype.forEach.call(btns, function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        Array.prototype.forEach.call(document.querySelectorAll(".h-uk"), function (el) { el.classList.toggle("help-hidden", mode === "any"); });
        Array.prototype.forEach.call(document.querySelectorAll(".h-any"), function (el) { el.classList.toggle("help-hidden", mode === "uk"); });
      });
    });
  }
})();
