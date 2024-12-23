
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
let sidebar = document.querySelector(".sidebar");
let closeBtn = document.querySelector("#btn");

closeBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  menuBtnChange(); //calling the function(optional)
});

// following are the code to change sidebar button(optional)
function menuBtnChange() {
  if (sidebar.classList.contains("open")) {
    closeBtn.classList.replace("bx-menu", "bx-menu-alt-right"); //replacing the iocns class
  } else {
    closeBtn.classList.replace("bx-menu-alt-right", "bx-menu"); //replacing the iocns class
  }
}
   

document.addEventListener('DOMContentLoaded', function () {
  const deleteLinks = document.querySelectorAll('.delete-class');
  deleteLinks.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      const classId = link.getAttribute('data-classid');
      if (confirm('Are you sure you want to delete this class?')) {
        window.location.href = `/delete_class/${classId}`;
      }
    });
  });
});


function openQuizModal() {
const quizModal = document.getElementById('quizModal');
const overlay = document.getElementById('overlay');
quizModal.style.display = 'block';
overlay.style.display = 'block';
}

// Function to close the modal
function closeQuizModal() {
const quizModal = document.getElementById('quizModal');
const overlay = document.getElementById('overlay');
quizModal.style.display = 'none';
overlay.style.display = 'none';
}

// Close the modal if the dimmed background is clicked
window.addEventListener('click', (event) => {
const quizModal = document.getElementById('quizModal');
const overlay = document.getElementById('overlay');
if (event.target === overlay) {
closeQuizModal(); // Call the close function
}
});








