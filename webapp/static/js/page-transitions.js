/**
 * Page Transitions Controller
 * Handles smooth fade transitions when navigating between pages
 * Only applies to pages with .app-container > .scroll-content structure
 */

(function() {
    'use strict';

    // Configuration
    const FADE_OUT_DURATION = 150; // ms - should match CSS fadeOut duration

    /**
     * Check if the current page should have transitions
     * Admin dashboard uses different layout and is excluded
     */
    function shouldApplyTransitions() {
        const appContainer = document.querySelector('.app-container');
        const scrollContent = document.querySelector('.app-container .scroll-content');
        return appContainer && scrollContent;
    }

    /**
     * Check if a link is an internal navigation link
     */
    function isInternalLink(link) {
        // Skip if no href
        if (!link.href) return false;
        
        // Skip external links
        if (link.hostname !== window.location.hostname) return false;
        
        // Skip hash links on same page
        if (link.hash && link.pathname === window.location.pathname) return false;
        
        // Skip javascript: links
        if (link.href.startsWith('javascript:')) return false;
        
        // Skip links that open in new tab
        if (link.target === '_blank') return false;
        
        // Skip download links
        if (link.hasAttribute('download')) return false;
        
        // Skip form submit buttons styled as links
        if (link.closest('form')) return false;
        
        return true;
    }

    /**
     * Perform fade-out transition and navigate
     */
    function navigateWithTransition(href) {
        const scrollContent = document.querySelector('.app-container .scroll-content');
        
        if (!scrollContent) {
            // Fallback: just navigate
            window.location.href = href;
            return;
        }

        // Add fade-out class
        scrollContent.classList.add('fade-out');

        // Navigate after animation completes
        setTimeout(function() {
            window.location.href = href;
        }, FADE_OUT_DURATION);
    }

    /**
     * Handle link clicks
     */
    function handleLinkClick(event) {
        const link = event.target.closest('a');
        
        if (!link) return;
        if (!isInternalLink(link)) return;
        
        // Prevent default navigation
        event.preventDefault();
        
        // Navigate with transition
        navigateWithTransition(link.href);
    }

    /**
     * Initialize transitions
     */
    function init() {
        // Only apply if page has the right structure
        if (!shouldApplyTransitions()) return;

        // Intercept all link clicks using event delegation
        document.addEventListener('click', handleLinkClick);

        // Handle browser back/forward buttons
        window.addEventListener('pageshow', function(event) {
            // If returning from bfcache, ensure content is visible
            if (event.persisted) {
                const scrollContent = document.querySelector('.app-container .scroll-content');
                if (scrollContent) {
                    scrollContent.classList.remove('fade-out');
                }
            }
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
