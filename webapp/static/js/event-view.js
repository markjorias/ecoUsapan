document.addEventListener('DOMContentLoaded', function() {
    const participateBtn = document.getElementById('participate-btn');
    const modal = document.getElementById('participation-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const submitBtn = document.getElementById('submit-participation-btn');
    const formContainer = document.getElementById('participation-form');
    const confirmationMessage = document.getElementById('confirmation-message');
    const closeConfirmationBtn = document.getElementById('close-confirmation-btn');

    // Open Modal
    participateBtn.addEventListener('click', function() {
        modal.classList.add('active');
        // Reset state
        formContainer.style.display = 'flex';
        confirmationMessage.style.display = 'none';
    });

    // Close Modal
    closeModalBtn.addEventListener('click', function() {
        modal.classList.remove('active');
    });

    // Submit Form
    submitBtn.addEventListener('click', function() {
        const eventId = window.location.pathname.split('/').pop(); // Grabs ID from URL
        
        const formData = {
            full_name: document.querySelector('input[placeholder="Your Name"]').value,
            address: document.querySelector('input[placeholder="Your Address"]').value,
            contact: document.querySelector('input[placeholder="09XX XXX XXXX"]').value,
            email: document.querySelector('input[placeholder="email@example.com"]').value,
            purpose: document.querySelector('textarea[placeholder="Why do you want to join?"]').value
        };

        fetch(`/participate/${eventId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error); // Simple validation alert
            } else {
                // Success: Switch to the confirmation message
                formContainer.style.display = 'none';
                confirmationMessage.style.display = 'flex';
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Close Confirmation
    closeConfirmationBtn.addEventListener('click', function() {
        modal.classList.remove('active');
    });

    // Close on click outside (optional)
    // modal.addEventListener('click', function(e) {
    //     if (e.target === modal) {
    //         modal.classList.remove('active');
    //     }
    // });
});
