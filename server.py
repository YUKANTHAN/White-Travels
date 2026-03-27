from flask_app import app
from flask_app.controllers import users_controller,bookings_controller,contacts_controller,destinations_controller
from flask_app.utils.monitor import start_sentry_monitor
import os

if __name__ == "__main__":
    # Start the Proactive Sentry Monitor in the background
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        start_sentry_monitor()
        
    app.run(debug=True)
