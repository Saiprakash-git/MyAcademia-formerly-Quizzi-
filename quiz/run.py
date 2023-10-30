# from quiz import app, socketio



# if __name__ == '__main__':
#    app.run(debug=True)

# socketio.run(app,debug=True)


# from flask import Flask
# from flask_socketio import SocketIO

# if __name__ == '__main__':
#    app.run(debug=True)

# app = Flask(__name__)
# socketio = SocketIO(app, async_mode="eventlet")

# ... rest of your code ...
from quiz import app,socketio



if __name__ == '__main__':
   app.run(debug=True)
if __name__ == '__main__':
    socketio.run(app)
  