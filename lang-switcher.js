// Language switcher for the trilingual mdBook site (zh at /, en at /en/, ja at /ja/).
// Relies on mdBook's global `path_to_root` to locate the current book root, so it
// works on GitHub Pages and `mdbook serve` alike. Same page path exists in every
// language tree (untranslated chapters are stubs), so we can deep-link.
(function () {
  function init() {
    var buttons = document.querySelector(".menu-bar .right-buttons");
    if (!buttons || typeof path_to_root === "undefined") return;

    var root = new URL(path_to_root || "./", window.location.href).pathname;
    var current = "zh";
    var site = root;
    if (root.slice(-3) === "en/") { current = "en"; site = root.slice(0, -3); }
    else if (root.slice(-3) === "ja/") { current = "ja"; site = root.slice(0, -3); }

    var page = window.location.pathname.slice(root.length);
    var langs = [
      ["zh", "中文", site + page],
      ["en", "EN", site + "en/" + page],
      ["ja", "日本語", site + "ja/" + page],
    ];

    var box = document.createElement("span");
    box.style.cssText = "margin-right:12px;font-size:0.85em;white-space:nowrap";
    langs.forEach(function (l, i) {
      if (i > 0) box.appendChild(document.createTextNode(" · "));
      if (l[0] === current) {
        var b = document.createElement("strong");
        b.textContent = l[1];
        box.appendChild(b);
      } else {
        var a = document.createElement("a");
        a.href = l[2];
        a.textContent = l[1];
        a.title = l[1];
        box.appendChild(a);
      }
    });
    buttons.insertBefore(box, buttons.firstChild);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
