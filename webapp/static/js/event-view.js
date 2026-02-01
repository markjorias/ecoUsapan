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
        // Validate inputs if needed (skipping for now as per instructions)
        
        // Hide form and show confirmation
        formContainer.style.display = 'none';
        confirmationMessage.style.display = 'flex';
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
