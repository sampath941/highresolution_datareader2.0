document.addEventListener('DOMContentLoaded', function () {

    function getCurrentTimeFormatted() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        return `${year}${month}${day}_${hours}${minutes}${seconds}`;
    }

    const filenameInput = document.getElementById('filename');
    if (filenameInput) {
        filenameInput.value = getCurrentTimeFormatted();
    }

    function flashMessage(message, category) {
        const container = document.getElementById('messages-container');
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messageElement.className = category; // Use this class for styling
        container.appendChild(messageElement);
    }

    console.log('DOM fully loaded');

    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');

    // Function to show the progress bar
    function showProgressBar() {
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
    }

    // Function to update the progress bar
    function updateProgressBar(value) {
        progressBar.style.width = `${value}%`;
        progressBar.textContent = `${value}%`;
    }

    // Function to hide the progress bar
    function hideProgressBar() {
        progressContainer.style.display = 'none';
    }

    // For the save form
    const saveForm = document.getElementById('save-form');
    if (saveForm) {
        saveForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent the default form submission

            const filenameInput = document.getElementById('filename');
            if (filenameInput && filenameInput.value.trim() === '') {
                alert('Filename is required.');
                return; // Prevent form submission
            }

            const formData = new FormData(saveForm);

            // Show the progress bar when starting the request
            showProgressBar();

            // Simulate progress updates
            let progress = 0;
            const interval = setInterval(() => {
                if (progress < 95) {
                    progress += 5; // Increment progress by 1%
                    updateProgressBar(progress);
                }
            }, 100); // Update every 500ms

            // Make an AJAX request to the server
            fetch(saveForm.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                clearInterval(interval); // Stop the interval when response is received
                const completeProgress = () => {
                    if (progress < 100) {
                        progress += 2;
                        updateProgressBar(progress);
                        setTimeout(completeProgress, 10);
                    } else {
                        updateProgressBar(100);
                    }
                };
                completeProgress(); // Update to 95% when the server responds

                return response.blob(); // Get the response as a Blob
            })
            .then(blob => {
                const dataFormat = document.querySelector('input[name="data_format"]:checked').value;
                const filename = document.getElementById('filename').value;
                const extension = dataFormat === 'excel' ? 'xlsx' : 'zip'; // Zip for CSV files
                const downloadUrl = URL.createObjectURL(blob);

                // Create a temporary link element and trigger the download
                const downloadLink = document.createElement('a');
                downloadLink.href = downloadUrl;
                downloadLink.download = `${filename}.${extension}`;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(downloadUrl);

                // Update the progress bar to 100% when the download is ready
                updateProgressBar(100);

                // Display a success message and refresh the page after a short delay
                flashMessage('File successfully downloaded', 'success');
                setTimeout(function() {
                    window.location.reload(true);  // Force a hard reload
                }, 7000);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                clearInterval(interval); // Stop the interval on error
                hideProgressBar(); // Hide the progress bar if there's an error
            });
        });
    } else {
        console.log("Failed to find the form element");
    }

    // For the upload form
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (event) {
            const fileInput = document.getElementById('file');
            if (fileInput) {
                if (!fileInput.files.length) {
                    alert('Please select a .db file to upload.');
                    event.preventDefault(); // Prevent form submission
                } else if (!fileInput.files[0].name.endsWith('.db')) {
                    alert('The selected file is not a .db file.');
                    event.preventDefault(); // Prevent form submission
                }
            }
        });
    }
});
