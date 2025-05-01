document.addEventListener('DOMContentLoaded', function() {
    // API endpoint (change this to match your deployment)
    const API_BASE_URL = '/api';
    
    // Form elements
    const uploadForm = document.getElementById('uploadForm');
    const apolloForm = document.getElementById('apolloForm');
    const fileUpload = document.getElementById('fileUpload');
    const outputFormat = document.getElementById('outputFormat');
    const apolloCallId = document.getElementById('apolloCallId');
    const apolloOutputFormat = document.getElementById('apolloOutputFormat');
    
    // Status elements
    const jobStatus = document.getElementById('jobStatus');
    const statusText = document.getElementById('statusText');
    const progressBar = document.getElementById('progressBar');
    const resultDownload = document.getElementById('resultDownload');
    const downloadLink = document.getElementById('downloadLink');
    const errorMessage = document.getElementById('errorMessage');
    
    // Result elements
    const resultCard = document.getElementById('resultCard');
    const companyInfo = document.getElementById('companyInfo');
    const situationInfo = document.getElementById('situationInfo');
    const needsInfo = document.getElementById('needsInfo');
    const processInfo = document.getElementById('processInfo');
    const nextInfo = document.getElementById('nextInfo');
    const notesInfo = document.getElementById('notesInfo');
    const transcriptInfo = document.querySelector('#transcriptInfo pre');
    
    // Current job status tracking
    let currentJobId = null;
    let statusCheckInterval = null;
    
    // Upload form submission
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Validate file input
        if (!fileUpload.files || fileUpload.files.length === 0) {
            alert('Please select a file to upload');
            return;
        }
        
        // Show status card
        showStatusCard();
        
        // Create form data
        const formData = new FormData();
        formData.append('file', fileUpload.files[0]);
        formData.append('output_format', outputFormat.value);
        
        // Submit to API
        fetch(`${API_BASE_URL}/analyze/upload`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Start tracking job status
            currentJobId = data.job_id;
            updateStatus(data);
            startStatusChecking();
        })
        .catch(error => {
            showError('Error starting analysis: ' + error.message);
        });
    });
    
    // Apollo form submission
    apolloForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Validate input
        if (!apolloCallId.value) {
            alert('Please enter an Apollo.io Call ID');
            return;
        }
        
        // Show status card
        showStatusCard();
        
        // Submit to API
        fetch(`${API_BASE_URL}/analyze/apollo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                apollo_call_id: apolloCallId.value,
                output_format: apolloOutputFormat.value
            })
        })
        .then(response => response.json())
        .then(data => {
            // Start tracking job status
            currentJobId = data.job_id;
            updateStatus(data);
            startStatusChecking();
        })
        .catch(error => {
            showError('Error starting analysis: ' + error.message);
        });
    });
    
    // Start periodic status checking
    function startStatusChecking() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
        }
        
        statusCheckInterval = setInterval(() => {
            if (!currentJobId) {
                clearInterval(statusCheckInterval);
                return;
            }
            
            checkJobStatus(currentJobId);
        }, 2000);
    }
    
    // Check job status
    function checkJobStatus(jobId) {
        fetch(`${API_BASE_URL}/status/${jobId}`)
            .then(response => response.json())
            .then(data => {
                updateStatus(data);
                
                // If job is completed or failed, stop checking
                if (data.status === 'completed' || data.status === 'failed') {
                    clearInterval(statusCheckInterval);
                    
                    if (data.status === 'completed' && data.result) {
                        showResult(data.result);
                    }
                }
            })
            .catch(error => {
                showError('Error checking status: ' + error.message);
                clearInterval(statusCheckInterval);
            });
    }
    
    // Update status display
    function updateStatus(data) {
        // Update status text
        let statusDisplay = 'Unknown';
        
        switch (data.status) {
            case 'queued':
                statusDisplay = 'Queued for processing...';
                break;
            case 'fetching_recording':
                statusDisplay = 'Fetching recording from Apollo.io...';
                break;
            case 'transcribing':
                statusDisplay = 'Transcribing audio...';
                break;
            case 'analyzing':
                statusDisplay = 'Analyzing conversation...';
                break;
            case 'generating_report':
                statusDisplay = 'Generating discovery sheet...';
                break;
            case 'completed':
                statusDisplay = 'Analysis completed!';
                break;
            case 'failed':
                statusDisplay = 'Analysis failed';
                break;
            default:
                statusDisplay = `Status: ${data.status}`;
        }
        
        statusText.textContent = statusDisplay;
        
        // Update progress bar
        const progressPercent = Math.round(data.progress * 100);
        progressBar.style.width = `${progressPercent}%`;
        progressBar.textContent = `${progressPercent}%`;
        progressBar.setAttribute('aria-valuenow', progressPercent);
        
        // Show error if failed
        if (data.status === 'failed' && data.error) {
            showError(data.error);
        }
        
        // Show download button if completed
        if (data.status === 'completed' && data.result && data.result.output_url) {
            resultDownload.classList.remove('d-none');
            downloadLink.href = data.result.output_url;
        }
    }
    
    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
    }
    
    // Show status card
    function showStatusCard() {
        // Reset status elements
        statusText.textContent = 'Initializing...';
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        resultDownload.classList.add('d-none');
        errorMessage.classList.add('d-none');
        errorMessage.textContent = '';
        
        // Show status card
        jobStatus.classList.remove('d-none');
        resultCard.classList.add('d-none');
    }
    
    // Show result preview
    function showResult(result) {
        // Get discovery sheet data
        const discoverySheet = result.discovery_sheet;
        if (!discoverySheet || !discoverySheet.content) {
            return;
        }
        
        // Populate company info
        const companyData = discoverySheet.content['Company Information'] || {};
        companyInfo.innerHTML = formatSection(companyData);
        
        // Populate current situation
        const situationData = discoverySheet.content['Current Situation'] || {};
        situationInfo.innerHTML = formatSection(situationData);
        
        // Populate needs and requirements
        const needsData = discoverySheet.content['Needs and Requirements'] || {};
        needsInfo.innerHTML = formatSection(needsData);
        
        // Populate buying process
        const processData = discoverySheet.content['Buying Process'] || {};
        processInfo.innerHTML = formatSection(processData);
        
        // Populate next steps
        const nextData = discoverySheet.content['Next Steps'] || {};
        nextInfo.innerHTML = formatSection(nextData);
        
        // Populate notes
        const notesData = discoverySheet.content['Notes'] || {};
        notesInfo.innerHTML = formatSection(notesData);
        
        // Populate transcript
        if (discoverySheet.transcript) {
            transcriptInfo.textContent = discoverySheet.transcript;
        } else {
            transcriptInfo.textContent = 'Transcript not available';
        }
        
        // Show result card
        resultCard.classList.remove('d-none');
    }
    
    // Format section data as HTML
    function formatSection(sectionData) {
        let html = '';
        
        for (const [key, value] of Object.entries(sectionData)) {
            if (value) {
                // Format field name for display (convert snake_case to Title Case)
                const displayName = key.split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                
                html += `<div class="mb-3">
                    <h5>${displayName}</h5>
                    <p>${value}</p>
                </div>`;
            }
        }
        
        return html || '<p>No data available</p>';
    }
});