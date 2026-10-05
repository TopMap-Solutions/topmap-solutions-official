export function initTestimonialsCarousel(carousel) {
    const track = carousel?.querySelector(".testimonials-scroll");
    const slides = [...(track?.querySelectorAll(".testimonial-card") ?? [])];
    const controls = carousel?.querySelector(".testimonials-controls");
    const previous = carousel?.querySelector(".testimonial-previous");
    const next = carousel?.querySelector(".testimonial-next");
    const currentLabel = carousel?.querySelector("[data-testimonial-current]");
    if (!track || slides.length < 2 || !controls || !previous || !next) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const currentIndex = () =>
        Math.max(0, Math.min(slides.length - 1, Math.round(track.scrollLeft / track.clientWidth)));
    const showSlide = (index) => {
        const wrappedIndex = (index + slides.length) % slides.length;
        track.scrollTo({
            left: wrappedIndex * track.clientWidth,
            behavior: reducedMotion.matches ? "instant" : "smooth",
        });
        if (currentLabel) currentLabel.textContent = String(wrappedIndex + 1);
    };
    const updateCurrent = () => {
        if (currentLabel) currentLabel.textContent = String(currentIndex() + 1);
    };

    controls.hidden = false;
    previous.addEventListener("click", () => showSlide(currentIndex() - 1));
    next.addEventListener("click", () => showSlide(currentIndex() + 1));
    track.addEventListener("scroll", updateCurrent, { passive: true });
    window.addEventListener("resize", updateCurrent);
    updateCurrent();

    if (carousel.dataset.autoplay !== "true") return;
    window.setInterval(() => {
        if (
            reducedMotion.matches ||
            document.hidden ||
            carousel.matches(":hover, :focus-within") ||
            !track.clientWidth
        ) return;
        showSlide(currentIndex() + 1);
    }, 5000);
}
