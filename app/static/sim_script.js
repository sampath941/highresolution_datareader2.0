document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('add-device-btn').addEventListener('click', function() {
        const deviceContainer = document.getElementById('devices-container');
        const deviceCount = deviceContainer.children.length; // Starts at 0

        const deviceBlock = document.createElement('div');
        deviceBlock.classList.add('device-block');
        deviceBlock.setAttribute('data-device-id', deviceCount); // Set a data attribute for easy reference

        deviceBlock.innerHTML = `
            <h3>Device ${deviceCount + 1}</h3>
            <label for="hostname-${deviceCount}">Hostname:</label>
            <input type="text" name="devices[${deviceCount}][hostname]" id="hostname-${deviceCount}" required>

            <h4>Simulation Configuration</h4>
            <div id="detectors-container-${deviceCount}">
                <!-- Detectors will be added here dynamically -->
            </div>
            <button type="button" onclick="addDetector(${deviceCount})">Add Detector</button>
            <button type="button" onclick="removeDetector(${deviceCount})" class="danger-button">Remove Detector</button>





        `;
        deviceContainer.appendChild(deviceBlock);
    });

    window.addDetector = function(deviceId) {
        const detectorContainer = document.getElementById(`detectors-container-${deviceId}`);
        const detectorCount = detectorContainer.children.length; // Starts at 0

        const detectorBlock = document.createElement('div');
        detectorBlock.innerHTML = `
            <h5>Detector ${detectorCount + 1}</h5>
            <label for="detnumber-${deviceId}-${detectorCount}">Detector Number:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorCount}][detnumber]" id="detnumber-${deviceId}-${detectorCount}" required>
            <label for="volume-${deviceId}-${detectorCount}">Volume:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorCount}][volume]" id="volume-${deviceId}-${detectorCount}" required>
            <label for="occupancy-${deviceId}-${detectorCount}">Occupancy:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorCount}][occupancy]" id="occupancy-${deviceId}-${detectorCount}" required>
            <label for="frequency-${deviceId}-${detectorCount}">Frequency:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorCount}][frequency]" id="frequency-${deviceId}-${detectorCount}" required>
        `;
        detectorContainer.appendChild(detectorBlock);
    };

    window.removeDetector = function(deviceId, detectorId) {
        // Remove the detector block from the DOM
        const detectorBlock = document.querySelector(`#detectors-container-${deviceId} [data-detector-id="${detectorId}"]`);
        if (detectorBlock) {
            detectorBlock.remove();
        }

        // Send a request to the server to remove the detector from the config
        fetch('/simulation/remove-detector', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ deviceId: deviceId, detectorId: detectorId }),
        }).then(response => {
            if (response.ok) {
                alert('Detector removed successfully.');
            } else {
                alert('Failed to remove the detector.');
            }
        });
    };

    window.removeDevice = function(deviceId) {
        // Remove the device block from the DOM
        const deviceBlock = document.querySelector(`[data-device-id="${deviceId}"]`);
        if (deviceBlock) {
            deviceBlock.remove();
        }

        // Send a request to the server to remove the device from the config
        fetch('/simulation/remove-device', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ deviceId: deviceId }),
        }).then(response => {
            if (response.ok) {
                alert('Device removed successfully.');
            } else {
                alert('Failed to remove the device.');
            }
        });
    };

    // Start simulation
    document.getElementById('start-simulation-btn').addEventListener('click', function() {
        fetch('/simulation/start-simulation', { method: 'POST' });
    });

    // Stop simulation
    document.getElementById('stop-simulation-btn').addEventListener('click', function() {
        fetch('/simulation/stop-simulation', { method: 'POST' });
    });
});
