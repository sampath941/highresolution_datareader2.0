from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
import json
import asyncio
from app.services.det_simulator import run_simulation, stop_event
from app.services.simulation_state import set_simulation_status, get_simulation_status

# Create a blueprint for simulation-related routes
simulation = Blueprint('simulation', __name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')

@simulation.route('/config-ui')
def config_ui():
    config = {}
    try:
        # Load the existing configuration
        with open(CONFIG_PATH, 'r') as config_file:
            config = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file does not exist or is invalid, start with an empty config
        config = {'devices': []}
    
    # Pass the configuration to the template
    return render_template('simconfig_ui.html', config=config)


@simulation.route('/save-config', methods=['POST'])
def save_config():
    config_data = request.form.to_dict(flat=False)

    # Load the existing configuration
    try:
        with open(CONFIG_PATH, 'r') as config_file:
            existing_config = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_config = {'devices': []}

    # Clear the devices list to avoid duplicates
    devices = []

    # Extract all device IDs from the submitted form data
    device_ids = sorted(set([key.split('[')[1].split(']')[0] for key in config_data.keys() if key.startswith('devices[')]))

    for device_id in device_ids:
        hostname_key = f'devices[{device_id}][hostname]'
        hostname = config_data.get(hostname_key, [None])[0]

        if hostname:
            detectors = []
            
            # Count how many detectors are there for this device
            detector_count = len([key for key in config_data.keys() if key.startswith(f'devices[{device_id}][detectors]') and key.endswith('[detnumber]')])

            for det_id in range(detector_count):
                detector = {
                    'detnumber': int(config_data.get(f'devices[{device_id}][detectors][{det_id}][detnumber]', [0])[0]),
                    'volume': int(config_data.get(f'devices[{device_id}][detectors][{det_id}][volume]', [0])[0]),
                    'occupancy': int(config_data.get(f'devices[{device_id}][detectors][{det_id}][occupancy]', [0])[0]),
                    'frequency': int(config_data.get(f'devices[{device_id}][detectors][{det_id}][frequency]', [0])[0]),
                }
                detectors.append(detector)

            devices.append({
                'hostname': hostname,
                'detectors': detectors,
            })

    # Save the updated configuration
    updated_config = {'devices': devices}

    try:
        with open(CONFIG_PATH, 'w') as config_file:
            json.dump(updated_config, config_file, indent=4)
        flash('Configuration saved successfully!', 'success')
    except Exception as e:
        print(f"Failed to write to {CONFIG_PATH}: {e}")
        flash('Failed to save configuration!', 'error')

    # Reload the page with the updated configuration
    return redirect(url_for('simulation.config_ui'))


@simulation.route('/start-simulation', methods=['POST'])
def start_simulation():
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    asyncio.run(run_simulation(config))
    return '', 204

@simulation.route('/stop-simulation', methods=['POST'])
def stop_simulation():
    stop_event.set() 
    status, total, succesful, failed = get_simulation_status()
    set_simulation_status(False, total, succesful, failed) # Signal the simulation to stop
    return '', 204

@simulation.route('/clear-config', methods=['POST'])
def clear_config():
    # Clear the configuration by writing an empty devices list
    try:
        with open(CONFIG_PATH, 'w') as config_file:
            json.dump({'devices': []}, config_file, indent=4)
        flash('Configuration cleared successfully!', 'success')
    except Exception as e:
        print(f"Failed to clear configuration: {e}")
        flash('Failed to clear configuration!', 'error')
    
    return redirect(url_for('simulation.config_ui'))
# @simulation.route('/remove-device', methods=['POST'])
# def remove_device():
#     data = request.get_json()
#     device_id = data.get('deviceId')

#     if device_id is None:
#         return jsonify({'error': 'Invalid device ID'}), 400

#     with open(CONFIG_PATH, 'r') as f:
#         config = json.load(f)

#     if device_id < len(config['devices']):
#         del config['devices'][device_id]

#         with open(CONFIG_PATH, 'w') as f:
#             json.dump(config, f, indent=4)

#         return jsonify({'success': True}), 200
#     else:
#         return jsonify({'error': 'Device not found'}), 404
    
# @simulation.route('/remove-detector', methods=['POST'])
# def remove_detector():
#     data = request.get_json()
#     device_id = data.get('deviceId')
#     detector_id = data.get('detectorId')

#     if device_id is None or detector_id is None:
#         return jsonify({'error': 'Invalid device or detector ID'}), 400

#     with open(CONFIG_PATH, 'r') as f:
#         config = json.load(f)

#     if device_id < len(config['devices']) and detector_id < len(config['devices'][device_id]['detectors']):
#         del config['devices'][device_id]['detectors'][detector_id]

#         with open(CONFIG_PATH, 'w') as f:
#             json.dump(config, f, indent=4)

#         return jsonify({'success': True}), 200
#     else:
#         return jsonify({'error': 'Detector not found'}), 404

@simulation.route('/simulation-status', methods=['GET'])
def simulation_status_endpoint():
    status, total, succesful, failed = get_simulation_status()
    if total > 0:
        success_percent = round ((succesful / total) * 100)
    else:
        success_percent = 0  # or you could use None, or some other appropriate value
    print ('Here is the list of results:', status, total, succesful, failed, success_percent)
    return jsonify({'status': status, 'Total_Requests': total, 'Successful_Requests': succesful, 'Failed_Requests': failed, 'success_percent': success_percent})