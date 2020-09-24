Production = False

from bin import app

if Production:
    app.app.run_server(debug=False, threaded=True)
else:
    PORT = 8050
    ADDRESS = '0.0.0.0'
    app.app.run_server(port=PORT, host=ADDRESS, debug=True)
