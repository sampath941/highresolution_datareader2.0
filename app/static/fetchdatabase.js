document.getElementById('fetch-db-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    const hostname = document.getElementById('hostname').value;
    if (!hostname) {
        alert("Please enter the device hostname.");
        return;
    }

    fetch('/simulation/fetch-database', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ hostname: hostname }),
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Failed to fetch database from controller.');
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        const filename = `${Date.now()}.bin`;
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
