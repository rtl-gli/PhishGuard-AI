const chatToggle = document.getElementById("chatToggle");
const chatPanel = document.getElementById("chatPanel");
const chatClose = document.getElementById("chatClose");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");

const answers = [
    {
        keywords: ["what is phishing", "phishing"],
        answer: "Phishing is a scam that uses a convincing message or website to trick you into sharing information, sending money, or installing something harmful. Unexpected urgency, unusual sender addresses, and links that do not match the claimed organisation are common warning signs."
    },
    {
        keywords: ["clicked", "click", "opened", "already"],
        answer: "If you clicked a suspicious link, do not enter any information and close the page. If you entered a password, change it from the real website and enable multi-factor authentication. If you entered payment details, contact your bank. Run a security check and report the message too."
    },
    {
        keywords: ["accurate", "accuracy", "score", "result", "risk"],
        answer: "The detector is an educational second opinion based on patterns in a URL. It does not visit the website and cannot guarantee that a link is safe. Treat a medium or high result as a reason to pause, and verify important messages through a trusted channel."
    },
    {
        keywords: ["safe", "legitimate", "real"],
        answer: "A low-risk result is not a guarantee. Check the sender, look for spelling or urgency, and go to the organisation's website by typing its address yourself instead of following a message link."
    },
    {
        keywords: ["password", "account", "login"],
        answer: "Never share a password in this tool or through a link you do not fully trust. To sign in, type the organisation's known website address yourself or use a saved bookmark, then consider turning on multi-factor authentication."
    },
    {
        keywords: ["report", "bank", "money", "payment"],
        answer: "Report suspicious messages using your email or platform's report button. If you shared banking or payment details, contact your bank immediately using the number on your card or an official statement."
    }
];

function getAnswer(question) {
    const normalised = question.toLowerCase();
    const match = answers.find((entry) => entry.keywords.some((keyword) => normalised.includes(keyword)));
    return match ? match.answer : "I can help with phishing basics, suspicious links, scan results, passwords, or what to do after clicking. Try asking: “What should I do if I clicked a suspicious link?”";
}

function addMessage(text, type) {
    const message = document.createElement("div");
    message.className = `chat-message ${type}`;
    message.textContent = text;
    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function askQuestion(question) {
    const trimmed = question.trim();
    if (!trimmed) return;
    addMessage(trimmed, "user");
    window.setTimeout(() => addMessage(getAnswer(trimmed), "assistant"), 260);
}

chatToggle.addEventListener("click", () => {
    const isOpen = !chatPanel.classList.toggle("hidden");
    chatToggle.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) chatInput.focus();
});
chatClose.addEventListener("click", () => {
    chatPanel.classList.add("hidden");
    chatToggle.setAttribute("aria-expanded", "false");
});
chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    askQuestion(chatInput.value);
    chatInput.value = "";
});
document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => askQuestion(button.dataset.question));
});

if (window.location.hash === "#help") {
    chatPanel.classList.remove("hidden");
    chatToggle.setAttribute("aria-expanded", "true");
    chatInput.focus();
}
