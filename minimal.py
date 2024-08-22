from flask import Flask, Blueprint, render_template

simulation = Blueprint('simulation', __name__)

@simulation.route('/config-ui')
def config_ui():
    return "Simulation Config UI"

app = Flask(__name__)

app.register_blueprint(simulation, url_prefix='/simulation')

if __name__ == '__main__':
    app.run(debug=True)
