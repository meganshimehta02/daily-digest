
const dateElement = document.getElementById("current-date");

if (dateElement) {
  const today = new Date();

  dateElement.textContent = today.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric"
  });
}
