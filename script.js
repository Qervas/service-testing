document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const uploadButton = document.getElementById('uploadButton');
    const responseContainer = document.getElementById('response');
    const formData = new FormData();
    const fileInput = document.getElementById('fileInput');

    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);

        // Display loading text
        uploadButton.innerText = 'Uploading...';
        uploadButton.disabled = true;
		const originalFileName = document.getElementById('fileInput').files[0].name.split('.').slice(0, -1).join('.');;
		const timeInterval = document.getElementById('timeInterval').value || '0.5';
		formData.append('time_interval', timeInterval);
        fetch('http://127.0.0.1:5000/upload', { // Replace with your Flask app's URL
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // Reset upload button
            uploadButton.innerText = 'Upload';
            uploadButton.disabled = false;

            // Display success message and download button
            responseContainer.innerHTML = `
                <p>File uploaded successfully!</p>
                <button id="downloadButton">Download JSON</button>
            `;
			filename = document.getElementById('fileInput').files[0].name.split('.')[0];

            // Add click event listener to download button
            document.getElementById('downloadButton').addEventListener('click', function() {
                const jsonStr = JSON.stringify(data, null, 2);
                downloadJSON(jsonStr, originalFileName+'.json')
            });
        })
        .catch(error => {
            console.error('Error:', error);
            responseContainer.innerHTML = `<p>Error during upload: ${error.message}</p>`;
            // Reset upload button
            uploadButton.innerText = 'Upload';
            uploadButton.disabled = false;
        });
    } else {
        alert('Please select a file to upload.');
    }
});

// Function to trigger JSON file download
function downloadJSON(data, filename) {
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}