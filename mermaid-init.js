document.addEventListener("DOMContentLoaded", function () {
  mermaid.initialize({
    startOnLoad: false,
    theme: "default",
    securityLevel: "loose",
    flowchart: { useMaxWidth: true },
  });

  // Render all mermaid code blocks
  let id = 0;
  for (const code of document.querySelectorAll("code.language-mermaid")) {
    const pre = code.parentElement;
    const wrapper = document.createElement("div");
    wrapper.className = "mermaid";
    wrapper.textContent = code.textContent;
    pre.parentElement.replaceChild(wrapper, pre);
  }

  mermaid.run();
});
