from flask import Flask, send_file
import io
import cv2
from picamera2 import Picamera2

app = Flask(__name__)
picam2 = Picamera2()  # Initialize the camera only once when the server starts

def initialize_camera():
    """Function to initialize and configure the camera."""
    picam2.start()
    # Additional configuration can be set here if necessary

@app.before_first_request
def startup():
    """Configure camera at startup only once."""
    initialize_camera()

@app.route('/image')
def serve_image_stream():
    try:
        image_array = picam2.capture_array()
        _, buffer = cv2.imencode('.png', image_array)
        image_io = io.BytesIO(buffer)
        image_io.seek(0)
        return send_file(image_io, mimetype='image/png')
    except Exception as e:
        # Log error and potentially reinitialize or restart the camera if needed
        print(f"Error capturing image: {str(e)}")
        return "Error capturing image", 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Route to properly stop the camera and shutdown the server."""
    shutdown_server()
    picam2.stop()  # Properly stop the camera before shutting down
    return 'Server shutting down...'

def shutdown_server():
    """Utility function to stop the Flask server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
