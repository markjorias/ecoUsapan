document.addEventListener('DOMContentLoaded', () => {
    // 1. Target the content container
    // Priority: .scroll-content -> .app-container
    let target = document.querySelector('.scroll-content');
    if (!target) {
        target = document.querySelector('.app-container');
        if (target) target.classList.add('animate-target'); // Add class so CSS targets it
    }
    
    // Safety check
    if (!target) return;

    // 2. Trigger fade-in (reveal content)
    // Use requestAnimationFrame to ensure the initial state is applied
    requestAnimationFrame(() => {
        target.classList.add('page-loaded');
    });

    // 3. Handle link clicks for fade-out
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        
        // Check if it's a valid link
        if (link && link.href && !link.target && !link.hasAttribute('download')) {
            const destination = new URL(link.href);
            
            // Only transition for internal links and different generic pages
            if (destination.origin === window.location.origin && 
                destination.pathname !== window.location.pathname &&
                !link.getAttribute('href').startsWith('#') &&
                !link.dataset.noTransition) {
                
                e.preventDefault(); // Stop immediate navigation
                
                // Add exiting class to fade out
                target.classList.remove('page-loaded');
                target.classList.add('page-exiting');

                // Wait for animation to finish, then navigate
                setTimeout(() => {
                    window.location.href = link.href;
                }, 200); // 200ms matches CSS exit transition
            }
        }
    });

    // 4. Handle Back/Forward Cache (bfcache)
    window.addEventListener('pageshow', (event) => {
        if (event.persisted) {
            // Force reset to visible state if coming from cache
            target.classList.remove('page-exiting');
            target.classList.add('page-loaded');
        }
    });
});
