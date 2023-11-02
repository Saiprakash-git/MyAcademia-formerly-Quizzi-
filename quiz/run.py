from quiz import app, socketio


from flask import Flask, request, session
import uuid

@app.before_request
def add_tab_identifier():
    if 'tab_id' not in session:
        session['tab_id'] = str(uuid.uuid4())

if __name__ == '__main__':

   socketio.run(app,debug=True)

