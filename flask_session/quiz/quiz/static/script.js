
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

var socket1 = io.connect('https://' + document.domain + ':' + location.port);

socket1.on('connect', function() {
  console.log('Connected to the server.');
});

socket1.on('join_quiz', function(data) {
  // Update the teacher's view with the newly joined student data
  console.log('Student joined: ' + data.username);

  // You can update the HTML content here to display the new student's information
  var studentList = document.getElementById('student-list');
  var listItem = document.createElement('li');
  listItem.appendChild(document.createTextNode(data.username));
  studentList.appendChild(listItem);
});

socket1.on('disconnect', function() {
  console.log('Disconnected from the server.');
});

function joinQuiz() {
  console.log('Imhereee');
  var username = document.getElementById('username').value;
  var quizId = 1; // Replace with the actual quiz ID

  // Emit a 'join_quiz' event to notify the server
  socket1.emit('join_quiz', { username: username, quiz_id: quizId });
}


// Get the elements by their IDs
const createButton = document.getElementById("createButton");
const createBox = document.getElementById("createBox");
const createClassButton = document.getElementById("createClassButton");
const joinClassButton = document.getElementById("joinClassButton");

// Add a click event listener to the create button
createButton.addEventListener("click", function () {
    // Toggle the visibility of the create box
    createBox.classList.toggle("hidden");
});

// Add functionality for the "Create Class" button
createClassButton.addEventListener("click", function () {
    // Add your code to handle class creation here
    alert("Creating a new class!");
});

// Add functionality for the "Join Class" button
joinClassButton.addEventListener("click", function () {
    // Add your code to handle joining a class here
    alert("Joining a class!");
});





    // // Connect to the WebSocket server
    // const socket = io.connect('http://' + document.domain + ':' + location.port + '/quiz');

    // // Listen for the "quiz_started" event
    // socket.on('quiz_started', (data) => {
    //     // Access the quiz_code from the received data
    //     const quizCode = data.quiz_code;

    //     // Redirect to the running_quiz route
    //     window.location.href = '/running_quiz/' + quizCode;
    // });

