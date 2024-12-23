from quiz import app, socketio
import os

if __name__ == '__main__':
   
   socketio.run(app,allow_unsafe_werkzeug=True)
   port = int(os.environ.get("PORT", 5000))  # Default to 5000 if no port is provided
   app.run(host="0.0.0.0", port=port)