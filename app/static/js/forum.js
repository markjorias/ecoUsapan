function toggleThread(btn) {
    const container = btn.nextElementSibling;
    const isHidden = container.style.display === 'none';
    
    container.style.display = isHidden ? 'flex' : 'none';
    
    const textSpan = btn.querySelector('span');
    const icon = btn.querySelector('.collapse-icon');
    
    if (isHidden) {
        textSpan.textContent = 'Hide Replies';
        // You could swap the icon to a minus or chevron here if you have one
    } else {
        textSpan.textContent = 'Show 2 Replies';
    }
}

function showReplyInput(btn) {
    const parent = btn.closest('.comment-card');
    const inputContainer = parent.querySelector('.inline-reply-container');
    
    const isHidden = inputContainer.style.display === 'none';
    inputContainer.style.display = isHidden ? 'flex' : 'none';
    
    if (isHidden) {
        inputContainer.querySelector('input').focus();
    }
}
