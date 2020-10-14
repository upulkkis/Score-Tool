Production = False

from bin import app

run=app.app.server

if Production:
    PORT = 8050
    ADDRESS = '0.0.0.0'
    if __name__ == '__main__':
        app.app.run_server(port=PORT, host=ADDRESS, debug=False, threaded=True)
else:
    PORT = 8050
    ADDRESS = '0.0.0.0'
    if __name__ == '__main__':
        app.app.run_server(port=PORT, host=ADDRESS, debug=True)
