document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadContainer = document.getElementById('upload-container');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const textPrompt = document.getElementById('text-prompt');
    const processBtn = document.getElementById('process-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressStatus = document.getElementById('progress-status');
    const resultContainer = document.getElementById('result-container');
    const resultVideo = document.getElementById('result-video');
    const downloadBtn = document.getElementById('download-btn');
    
    let uploadedFile = null;
    let jobId = null;
    
    // Event Listeners
    browseBtn.addEventListener('click', () => fileInput.click());
    
    // Drag and drop functionality
    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadContainer.classList.add('drag-over');
    });
    
    uploadContainer.addEventListener('dragleave', () => {
        uploadContainer.classList.remove('drag-over');
    });
    
    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadContainer.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFileUpload(fileInput.files[0]);
        }
    });
    
    textPrompt.addEventListener('input', validateForm);
    
    processBtn.addEventListener('click', processVideo);
    
    downloadBtn.addEventListener('click', downloadVideo);
    
    // Functions
    function handleFileUpload(file) {
        if (!file.type.startsWith('video/')) {
            alert('Please upload a valid video file');
            return;
        }
        
        uploadedFile = file;
        
        // Update UI to show uploaded file
        const fileName = file.name;
        uploadContainer.innerHTML = `
            <div class="upload-icon">
                <i class="fas fa-check-circle" style="color: #4CAF50;"></i>
            </div>
            <h2>Video Uploaded</h2>
            <p>${fileName}</p>
            <button class="browse-btn" id="change-file-btn">Change File</button>
        `;
        
        document.getElementById('change-file-btn').addEventListener('click', () => {
            fileInput.click();
        });
        
        validateForm();
    }
    
    function validateForm() {
        if (uploadedFile && textPrompt.value.trim() !== '') {
            processBtn.disabled = false;
        } else {
            processBtn.disabled = true;
        }
    }
    
    function processVideo() {
        // Hide upload section and show progress
        document.querySelector('.upload-section').style.display = 'none';
        progressContainer.style.display = 'block';
        
        // Create FormData and append file and prompt
        const formData = new FormData();
        formData.append('video', uploadedFile);
        formData.append('prompt', textPrompt.value.trim());
        
        // Start progress animation
        startProgressAnimation();
        
        // Send the request to the backend
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                jobId = data.job_id;
                checkProcessingStatus();
            } else {
                alert('Error: ' + data.error);
                resetUI();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during processing. Please try again.');
            resetUI();
        });
    }
    
    function startProgressAnimation() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 2;
            if (progress >= 95) {
                clearInterval(interval);
            }
            
            progressBar.style.width = `${progress}%`;
            
            // Update status message based on progress
            if (progress < 30) {
                progressStatus.textContent = 'Extracting frames...';
            } else if (progress < 60) {
                progressStatus.textContent = 'Applying segmentation masks...';
            } else if (progress < 90) {
                progressStatus.textContent = 'Generating segmented video...';
            } else {
                progressStatus.textContent = 'Finalizing...';
            }
        }, 500);
        
        // Store the interval ID so we can clear it later
        window.progressInterval = interval;
    }
    
    function checkProcessingStatus() {
        fetch(`/api/status/${jobId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    // Clear the progress animation
                    if (window.progressInterval) {
                        clearInterval(window.progressInterval);
                    }
                    
                    // Set progress to 100%
                    progressBar.style.width = '100%';
                    progressStatus.textContent = 'Complete!';
                    
                    // Show the result after a short delay
                    setTimeout(() => {
                        progressContainer.style.display = 'none';
                        showResults(data.video_url);
                    }, 500);
                } else if (data.status === 'failed') {
                    alert('Processing failed: ' + data.error);
                    resetUI();
                } else {
                    // Still processing, check again after a delay
                    setTimeout(checkProcessingStatus, 2000);
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
                alert('Error checking processing status');
                resetUI();
            });
    }
    
    function showResults(videoUrl) {
        resultContainer.style.display = 'block';
        
        // Set the video source to the processed video
        // Use the direct video URL from the results folder
        resultVideo.src = videoUrl || `/video/${jobId}.mp4`;
        resultVideo.load();
    }
    
    function downloadVideo() {
        // Create a link to download the processed video
        const a = document.createElement('a');
        a.href = `/api/download/${jobId}`;
        a.download = `segmented_${uploadedFile.name}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
    
    function resetUI() {
        // Reset the UI to the initial state
        document.querySelector('.upload-section').style.display = 'flex';
        progressContainer.style.display = 'none';
        resultContainer.style.display = 'none';
        progressBar.style.width = '0%';
        
        if (window.progressInterval) {
            clearInterval(window.progressInterval);
        }
    }
});
