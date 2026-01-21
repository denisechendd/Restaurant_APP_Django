document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const header = document.querySelector('.header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Mobile nav toggle
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', function() {
            document.body.classList.toggle('mobile-nav-active');
            this.classList.toggle('bi-list');
            this.classList.toggle('bi-x');
        });
    }
});