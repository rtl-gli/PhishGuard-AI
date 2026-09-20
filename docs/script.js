const helpButton = document.getElementById("helpButton");
const helpPanel = document.getElementById("helpPanel");
const closeHelp = document.getElementById("closeHelp");
const helpAnswer = document.getElementById("helpAnswer");

function setHelp(open) {
    helpPanel.hidden = !open;
    helpButton.setAttribute("aria-expanded", String(open));
}

helpButton.addEventListener("click", () => setHelp(helpPanel.hidden));
closeHelp.addEventListener("click", () => setHelp(false));
document.querySelectorAll("[data-answer]").forEach((button) => {
    button.addEventListener("click", () => {
        helpAnswer.textContent = button.dataset.answer;
    });
});
