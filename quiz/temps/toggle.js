const modeToggle = document.getElementById("mode-toggle");
const themeStyle = document.getElementById("theme-style");

modeToggle.addEventListener("change", () => {
    if (modeToggle.checked) {
        themeStyle.href = "dark.css"; // Use dark mode stylesheet
    } else {
        themeStyle.href = "light.css"; // Use light mode stylesheet
    }
});
