document.addEventListener('DOMContentLoaded', function () {

    // Check if the configuration is empty on page load
    const isConfigEmpty = document.querySelectorAll('.device-block').length === 0;

    const addDeviceBtn = document.getElementById('add-device-btn');
    const saveConfigBtn = document.querySelector('form#config-form button[type="submit"]');

    if (!isConfigEmpty) {
        addDeviceBtn.disabled = true;
        saveConfigBtn.disabled = true;
    }

    // Add Device Button Click Event
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

        // Enable Save Configuration button since we now have at least one device
        saveConfigBtn.disabled = false;
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
                <button type="button" onclick="addSequence(${deviceId}, ${detectorCount})" class="btn-primary">Add a Cycle</button>
                <button type="button" onclick="removeLastSequence(${deviceId}, ${detectorCount})" class="danger-button">Remove Cycle</button>
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
            <label for="cycles-${deviceId}-${detectorId}-${sequenceCount}">No. of Cycles:</label>
            <input type="number" name="devices[${deviceId}][detectors][${detectorId}][sequences][${sequenceCount}][cycles]" id="cycles-${deviceId}-${detectorId}-${sequenceCount}" required>
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

        // Check if there are any devices left after removing one
        const deviceContainer = document.getElementById('devices-container');
        if (deviceContainer.children.length === 0) {
            saveConfigBtn.disabled = true;
        }
    };
    let inTransition = false;
    function checkSimulationStatus() {
        if (inTransition) return; // Skip status check if we are in a transition
        fetch('/simulation/simulation-status')
            .then(response => response.json())
            .then(data => {
                const greenIndicator = document.getElementById('green-indicator');
                const yellowIndicator = document.getElementById('yellow-indicator');
                const redIndicator = document.getElementById('red-indicator');
                const startButton = document.getElementById('start-simulation-btn');
                const stopButton = document.getElementById('stop-simulation-btn');
    
                if (data.status === true) { // Simulation is active (Green)
                    greenIndicator.classList.add('active');
                    yellowIndicator.classList.remove('active');
                    redIndicator.classList.remove('active');
                    startButton.disabled = true;
                    stopButton.disabled = false;
                } else { // Simulation is inactive (Red)
                    greenIndicator.classList.remove('active');
                    yellowIndicator.classList.remove('active');
                    redIndicator.classList.add('active');
                    startButton.disabled = false;
                    stopButton.disabled = true;
                    inTransition = false; // Transition is complete
                }
    
                document.getElementById('total-requests').textContent = data.Total_Requests;
                document.getElementById('successful-requests').textContent = data.Successful_Requests;
                document.getElementById('failed-requests').textContent = data.Failed_Requests;                
            })
            .catch(error => {
                console.error('Error fetching simulation status:', error);
            });
    }
    
    setInterval(checkSimulationStatus, 5000); 
    checkSimulationStatus();


    // document.getElementById('start-simulation-btn').addEventListener('click', function() {
    //     inTransition = false;
    //     fetch('/simulation/start-simulation', { method: 'POST' })
    //         .then(() => {
    //             checkSimulationStatus(); // Check status immediately after starting
    //         });
    // });

    const startSimulationBtn = document.getElementById('start-simulation-btn');
    const countdownContainer = document.getElementById('countdown-container'); // Use the existing countdown container

    startSimulationBtn.addEventListener('click', function() {
        const now = new Date();
        const seconds = now.getSeconds();
        const delay = (58 - seconds) > 0 ? (58 - seconds) : (118 - seconds); // Time in seconds to wait until 00:55
        let countdown = delay;

        // Show the countdown timer
        const countdownInterval = setInterval(() => {
            countdownContainer.textContent = `Trying to start the simulation until it's about to be the next Minute. So waiting for another ${countdown} seconds...`;
            countdown--;

            if (countdown < 0) {
                clearInterval(countdownInterval);
                countdownContainer.textContent = ''; // Clear the countdown timer text
                startSimulation();
            }
        }, 1000); // Update every second
    });

    function startSimulation() {
        inTransition = false;
        fetch('/simulation/start-simulation', { method: 'POST' })
            .then(() => {
                checkSimulationStatus(); // Check status immediately after starting
            })
            .catch(error => {
                console.error('Error starting simulation:', error);
            });
    }
    document.getElementById('stop-simulation-btn').addEventListener('click', function() {
        inTransition = true; // Set the transition flag when stopping
        const greenIndicator = document.getElementById('green-indicator');
        const yellowIndicator = document.getElementById('yellow-indicator');
        const redIndicator = document.getElementById('red-indicator');
    
        // Set the indicators: Yellow active, Green inactive
        greenIndicator.classList.remove('active');
        yellowIndicator.classList.add('active');
        redIndicator.classList.remove('active');
    
        // Send the stop request to the server
        fetch('/simulation/stop-simulation', { method: 'POST' })
            .then(() => {
                // After sending the stop request, check the status after a short delay
                setTimeout(() => {
                    inTransition = false; // End the transition before checking the status
                    checkSimulationStatus(); // Check the status again to transition to red
                }, 7000); // Reduced delay to quickly re-check the status
            });
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
