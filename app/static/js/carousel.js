document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.featured-card');
    const indicators = document.querySelectorAll('.indicator-pill');
    const progressBars = document.querySelectorAll('.indicator-progress');
    
    if (cards.length === 0) return;

    let currentIndex = 0;
    const intervalTime = 5000;
    let startTime = Date.now();
    let animationFrame;

    function updateCarousel() {
        cards.forEach((card, index) => {
            card.classList.toggle('active', index === currentIndex);
        });
        indicators.forEach((pill, index) => {
            pill.classList.toggle('active', index === currentIndex);
        });
        resetBars();
        startTime = Date.now();
    }

    function resetBars() {
        progressBars.forEach((bar, index) => {
            bar.style.width = '0%';
        });
    }

    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min((elapsed / intervalTime) * 100, 100);
        
        if (progressBars[currentIndex]) {
            progressBars[currentIndex].style.width = progress + '%';
        }

        if (elapsed >= intervalTime) {
            currentIndex = (currentIndex + 1) % cards.length;
            updateCarousel();
        }
        
        animationFrame = requestAnimationFrame(animate);
    }

    // Initialize
    updateCarousel();
    animationFrame = requestAnimationFrame(animate);
});
