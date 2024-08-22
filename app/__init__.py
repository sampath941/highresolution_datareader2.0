from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'alliswell'

    # Register the main blueprint
    from .main.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register the simulation blueprint
    from .main.simulation import simulation as simulation_blueprint
    app.register_blueprint(simulation_blueprint, url_prefix='/simulation')

    return app

