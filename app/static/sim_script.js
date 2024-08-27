document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('add-device-btn').addEventListener('click', function() {
        const deviceContainer = document.getElementById('devices-container');
        const deviceCount = deviceContainer.children.length;

        const deviceBlock = document.createElement('div');
        deviceBlock.classList.add('device-block');
        deviceBlock.setAttribute('data-device-id', deviceCount);

        deviceBlock.innerHTML = `
            <h3>Device ${deviceCount + 1}</h3>
            <label for="hostname-${deviceCount}">Hostname:</label>
            <input type="text" name="devices[${deviceCount}][hostname]" id="hostname-${deviceCount}" required>

            <h4>Simulation Configuration</h4>
            <div id="detectors-container-${deviceCount}">
                <!-- Detectors will be added here dynamically -->
            </div>
            <div class="detector-actions">
                <button type="button" onclick="addDetector(${deviceCount})" class="btn-primary">Add a New Detector</button>
                <button type="button" onclick="removeLastDetector(${deviceCount})" class="danger-button">Remove Detector</button>
            </div>
            <button type="button" class="danger-button remove-device-btn" onclick="removeDevice(${deviceCount})">Remove Device</button>
        `;
        deviceContainer.appendChild(deviceBlock);
    });

    window.addDetector = function(deviceId) {
        const detectorContainer = document.getElementById(`detectors-container-${deviceId}`);
        const detectorCount = detectorContainer.children.length;

        const detectorBlock = document.createElement('div');
        detectorBlock.classList.add('detector-block');
        detectorBlock.setAttribute('data-detector-id', detectorCount);

        detectorBlock.innerHTML = `
            <h5>Detector ${detectorCount + 1}</h5>
            <label for="detnumber-${deviceId}-${detectorCount}">Detector Number:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorCount}][detnumber]" id="detnumber-${deviceId}-${detectorCount}" required>
            <div id="sequences-container-${deviceId}-${detectorCount}" class="sequences-container">
                <!-- Sequences will be added here dynamically -->
            </div>
            <div class="sequence-actions">
                <button type="button" onclick="addSequence(${deviceId}, ${detectorCount})" class="btn-primary">Add a Sequence</button>
                <button type="button" onclick="removeLastSequence(${deviceId}, ${detectorCount})" class="danger-button">Remove Last Sequence</button>
            </div>
        `;
        detectorContainer.appendChild(detectorBlock);
    };

    window.addSequence = function(deviceId, detectorId) {
        const sequenceContainer = document.getElementById(`sequences-container-${deviceId}-${detectorId}`);
        const sequenceCount = sequenceContainer.children.length;

        const sequenceBlock = document.createElement('div');
        sequenceBlock.classList.add('sequence-block');
        sequenceBlock.setAttribute('data-sequence-id', sequenceCount);

        sequenceBlock.innerHTML = `
            <h6>Sequence ${sequenceCount + 1}</h6>
            <label for="volume-${deviceId}-${detectorId}-${sequenceCount}">Volume:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorId}][sequences][${sequenceCount}][volume]" id="volume-${deviceId}-${detectorId}-${sequenceCount}" required>
            <label for="occupancy-${deviceId}-${detectorId}-${sequenceCount}">Occupancy:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorId}][sequences][${sequenceCount}][occupancy]" id="occupancy-${deviceId}-${detectorId}-${sequenceCount}" required>
            <label for="frequency-${deviceId}-${detectorId}-${sequenceCount}">Frequency:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorId}][sequences][${sequenceCount}][frequency]" id="frequency-${deviceId}-${detectorId}-${sequenceCount}" required>
            <label for="duration-${deviceId}-${detectorId}-${sequenceCount}">Duration (seconds):</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorId}][sequences][${sequenceCount}][duration]" id="duration-${deviceId}-${detectorId}-${sequenceCount}" required>
        `;
        sequenceContainer.appendChild(sequenceBlock);
    };

    window.removeLastSequence = function(deviceId, detectorId) {
        const sequenceContainer = document.getElementById(`sequences-container-${deviceId}-${detectorId}`);
        if (sequenceContainer.children.length > 0) {
            sequenceContainer.removeChild(sequenceContainer.lastElementChild);
        }
    };

    window.removeLastDetector = function(deviceId) {
        const detectorContainer = document.getElementById(`detectors-container-${deviceId}`);
        if (detectorContainer.children.length > 0) {
            detectorContainer.removeChild(detectorContainer.lastElementChild);
        }
    };

    window.removeDevice = function(deviceId) {
        const deviceBlock = document.querySelector(`.device-block[data-device-id="${deviceId}"]`);
        if (deviceBlock) {
            deviceBlock.remove();
        }
    };

    function checkSimulationStatus() {
        console.log("Checking simulation status...");
        fetch('/simulation/simulation-status')
            .then(response => response.json())
            .then(data => {
                const statusIndicator = document.getElementById('status-indicator');
                const startButton = document.getElementById('start-simulation-btn');
                const stopButton = document.getElementById('stop-simulation-btn');
                if (data.status) {
                    statusIndicator.classList.remove('inactive');
                    statusIndicator.classList.add('active');
                    startButton.disabled = true;
                    stopButton.disabled = false;
                } else {
                    statusIndicator.classList.remove('active');
                    statusIndicator.classList.add('inactive');
                    startButton.disabled = false;
                    stopButton.disabled = true;
                }

                document.getElementById('total-requests').textContent = data.Total_Requests;
                document.getElementById('successful-requests').textContent = data.Successful_Requests;
                document.getElementById('failed-requests').textContent = data.Failed_Requests;                
            })
            .catch(error => {
                console.error('Error fetching simulation status:', error);
            });
    };
    
    setInterval(checkSimulationStatus, 3000); 
    checkSimulationStatus();

    document.getElementById('start-simulation-btn').addEventListener('click', function() {
        fetch('/simulation/start-simulation', { method: 'POST' });
    });

    document.getElementById('stop-simulation-btn').addEventListener('click', function() {
        fetch('/simulation/stop-simulation', { method: 'POST' });
    });

    const messagesContainer = document.getElementById('messages-container');
        
    if (messagesContainer) {
        // Set a timeout to remove the messages after 5 seconds (5000 milliseconds)
        setTimeout(function() {
            messagesContainer.style.transition = 'opacity 0.5s ease';
            messagesContainer.style.opacity = '0'; // Fade out
            setTimeout(function() {
                messagesContainer.innerHTML = ''; // Remove the messages from the DOM
            }, 500); // Wait for the fade-out to complete before removing
        }, 5000); // 5-second delay before starting the fade-out
    }
});
