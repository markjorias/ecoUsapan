from flask import Flask, send_from_directory, url_for
app = Flask(__name__)

@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return "CUSTOM: " + filename

with app.test_client() as client:
    with app.app_context():
        resp = client.get('/static/uploads/test.png')
        print("Response:", resp.data.decode())
        print("URL FOR:", url_for('static', filename='uploads/test.png'))
