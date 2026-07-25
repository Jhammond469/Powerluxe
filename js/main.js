// Navbar — transparent on home hero, solid on inner pages and on scroll
const navbar = document.getElementById('navbar');
const isHomePage = document.querySelector('.hero') !== null;

if (!isHomePage) {
    navbar.classList.add('solid');
}

window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 80);
});

// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
});
document.addEventListener('click', (e) => {
    if (!navbar.contains(e.target)) navLinks.classList.remove('open');
});

// Scroll-in animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
            setTimeout(() => entry.target.classList.add('visible'), i * 80);
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.15 });

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

// Portfolio slider
new Swiper('.portfolio-swiper', {
    slidesPerView: 1,
    spaceBetween: 24,
    loop: true,
    navigation: {
        nextEl: '.portfolio-swiper .swiper-button-next',
        prevEl: '.portfolio-swiper .swiper-button-prev',
    },
    pagination: {
        el: '.portfolio-swiper .swiper-pagination',
        clickable: true,
    },
    breakpoints: {
        640:  { slidesPerView: 2 },
        1024: { slidesPerView: 3 },
    },
});

// Testimonials slider — live Google Reviews via n8n, falls back to the reviews already in the HTML
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function initTestimonialsSwiper() {
    new Swiper('.testimonials-swiper', {
        slidesPerView: 1,
        spaceBetween: 32,
        loop: true,
        autoplay: { delay: 5000, disableOnInteraction: false },
        pagination: {
            el: '.testimonials-swiper .swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 },
        },
    });
}

const testimonialsWrapper = document.querySelector('.testimonials-swiper .swiper-wrapper');
if (testimonialsWrapper) {
    const REVIEWS_WEBHOOK_URL = 'https://jhammond.app.n8n.cloud/webhook/powerluxe-reviews';
    fetch(REVIEWS_WEBHOOK_URL)
        .then(res => res.ok ? res.json() : Promise.reject())
        .then(reviews => {
            if (!Array.isArray(reviews) || reviews.length === 0) throw new Error('No reviews');
            testimonialsWrapper.innerHTML = reviews.map(r => `
                <div class="swiper-slide">
                    <div class="testimonial-card">
                        <div class="stars">${'&#9733;'.repeat(r.rating)}</div>
                        <p>"${escapeHtml(r.text)}"</p>
                        <span class="author">— ${escapeHtml(r.author)}, Google Review</span>
                    </div>
                </div>
            `).join('');
        })
        .catch(() => { /* keep the hardcoded reviews already in the HTML */ })
        .finally(initTestimonialsSwiper);
} else {
    initTestimonialsSwiper();
}
