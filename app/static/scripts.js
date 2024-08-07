document.addEventListener('DOMContentLoaded', function () {
    function flashMessage(message, category) {
        const container = document.getElementById('messages-container');
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messageElement.className = category; // Use this class for styling
        container.appendChild(messageElement);
    
        // Optionally, remove the message after a few seconds
        setTimeout(() => {
            container.removeChild(messageElement);
        }, 10000); // Removes the message after 10 seconds
    }
    console.log('DOM fully loaded');
    console.log('script-js - 3')
    // For the save form
    const saveForm = document.getElementById('save-form');
    console.log('Save form:', saveForm);
    if (saveForm) {
        console.log('script-js - 7')
        saveForm.addEventListener('submit', function (event) {
            console.log('script-js - 10')
            const filenameInput = document.getElementById('filename');
            console.log('script-js - 12')
            if (filenameInput && filenameInput.value.trim() === '') {
                alert('Filename is required.');
                event.preventDefault();
                console.log('script.js - 16')
                return; // Prevent form submission
            }
    
            const formData = new FormData(saveForm);

            // Make an AJAX request to the server
            fetch(saveForm.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.blob(); // Get the response as a Blob
            })
            .then(blob => {
                console.log('Line 46')
                const dataFormat = document.querySelector('input[name="data_format"]:checked').value;
                const filename = document.getElementById('filename').value;
                const extension = dataFormat === 'xlsx' ? 'xlsx' : 'csv';
                const downloadUrl = URL.createObjectURL(blob);

                // Create a temporary link element and trigger the download
                console.log('Line 53')
                const downloadLink = document.createElement('a');
                downloadLink.href = downloadUrl;
                downloadLink.download = `${filename}.${extension}`;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(downloadUrl);
                console.log('I am in javascript code. Download Triggered, scheduling page reresh..')
                flashMessage('File succesfully downloaded', 'success')
                setTimeout(function() {
                    window.location.reload(true);  // Force a hard reload
                }, 2000);

                // flash('File successfully downloaded', 'success')
                // alert('File successfully downloaded', 'success')
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });

            event.preventDefault(); // Prevent the default form submission
        });
    } else {
        console.log("Failed to find the form element")
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

