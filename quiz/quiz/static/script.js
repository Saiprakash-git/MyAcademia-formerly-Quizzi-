
document.addEventListener("click", function(event) {
  var dropdown = document.getElementById("myDropdown");
  var button = document.querySelector(".dot-button");
  
  // Check if the click occurred outside the dropdown and the button
  if (!dropdown.contains(event.target) && !button.contains(event.target)) {
      dropdown.style.display = "none";
  }
});

function toggleDropdown() {
  var dropdown = document.getElementById("myDropdown");
  if (dropdown.style.display === "block") {
      dropdown.style.display = "none";
  } else {
      dropdown.style.display = "block";
  }
}

   


