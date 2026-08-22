document.documentElement.classList.add("has-js");

const picker = document.querySelector("[data-practice-picker]");

if (picker) {
  const choices = [...picker.querySelectorAll("[data-practice-choice]")];
  const title = document.querySelector("[data-practice-title]");
  const copy = document.querySelector("[data-practice-copy]");
  const link = document.querySelector("[data-practice-link]");

  const activate = (choice) => {
    choices.forEach((item) => item.setAttribute("aria-pressed", String(item === choice)));
    if (title) title.textContent = choice.dataset.title || "";
    if (copy) copy.textContent = choice.dataset.copy || "";
    if (link) link.href = choice.dataset.href || "/practice/";
  };

  choices.forEach((choice) => choice.addEventListener("click", () => activate(choice)));
}
