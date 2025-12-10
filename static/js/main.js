 // Main JavaScript for form handling
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions
    const forms = document.querySelectorAll('form[data-ajax="true"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            
            // Show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = 'Sending...';
            
            // Get form attributes
            const method = form.method.toUpperCase();
            const action = form.action || window.location.href;
            const enctype = form.enctype || 'application/x-www-form-urlencoded';
            
            // Handle file uploads
            const isFileUpload = form.enctype === 'multipart/form-data';
            
            fetch(action, {
                method: method,
                body: isFileUpload ? formData : new URLSearchParams(formData),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    ...(!isFileUpload && { 'Content-Type': enctype })
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Handle success response
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else if (data.message) {
                    showMessage('success', data.message);
                }
                form.reset();
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('error', 'An error occurred. Please try again.');
            })
            .finally(() => {
                // Reset button state
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    });
    
    // Show flash messages
    function showMessage(type, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type}`;
        messageDiv.textContent = message;
        
        const container = document.querySelector('.messages') || document.body;
        container.prepend(messageDiv);
        
        // Auto-remove message after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
    
    // Initialize any tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
