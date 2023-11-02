
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
const socket1 = io();
socket1.on('redirect_to_quiz', function (quizUrl) {
    window.location.href = quizUrl;
});

   
const socket = io({autoConnect: false}); 
socket.connect('http://127.0.0.1:5000');  // Use the base URL of your Flask application


socket.on('connect', () => {
    console.log('Connected to the WebSocket server');
});

socket.on('participant_joined', (data) => {
    const head = document.getElementById('head');
    head.textContent +="participants";
    console.log("User: " + data.username + " joined");
    const participantsList = document.getElementById("participants");
    const participantItem = document.createElement("li");
    participantItem.textContent = `User: ${data.username}`;
    participantsList.appendChild(participantItem);
});

socket.on('disconnect', () => {
    console.log('Disconnected from the WebSocket server');
});

socket.on('connect_error', (error) => {
    console.error('WebSocket connection error:', error);
});





