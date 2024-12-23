


//  var socket1 = io.connect('https://' + document.domain + ':' + location.port);
//   socket1.on('usercon',function(data){ 
//     obj = document.getElementById('users')
//     let li = document.createElement('p')
//     li.textContent += 'User:'+data['username']
//     obj.appendChild(li)
//     console.log("user : "+data['username'])
//   })

  // const source = new EventSource('/stream');
  // source.addEventListener('new_user', (event) => {
  //     const message = JSON.parse(event.data).message;
  //     const waitingRoom = document.getElementById('users');
  //     const listItem = document.createElement('li');
  //     listItem.textContent = message;
  //     waitingRoom.appendChild(listItem);
  // });