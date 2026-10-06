export function initTestimonialsCarousel(carousel) {
    const track = carousel?.querySelector(".testimonials-scroll");
    const slides = [...(track?.querySelectorAll(".testimonial-card") ?? [])];
    const controls = carousel?.querySelector(".testimonials-controls");
    const previous = carousel?.querySelector(".testimonial-previous");
    const next = carousel?.querySelector(".testimonial-next");
    const dots = [...(carousel?.querySelectorAll(".testimonial-dot") ?? [])];
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
        updateControls(wrappedIndex);
    };
    const updateControls = (index = currentIndex()) => {
        const firstVisible = Math.max(0, Math.min(index - 2, dots.length - 5));
        dots.forEach((dot, dotIndex) => {
            dot.hidden = dots.length > 5 && (dotIndex < firstVisible || dotIndex >= firstVisible + 5);
            dot.setAttribute("aria-current", String(dotIndex === index));
        });
    };

    controls.hidden = false;
    previous.addEventListener("click", () => showSlide(currentIndex() - 1));
    next.addEventListener("click", () => showSlide(currentIndex() + 1));
    dots.forEach((dot, index) => dot.addEventListener("click", () => showSlide(index)));
    track.addEventListener("scroll", () => updateControls(), { passive: true });
    window.addEventListener("resize", () => updateControls());
    updateControls();

    if (carousel.dataset.autoplay !== "true") return;
    window.setInterval(() => {
        if (
            reducedMotion.matches ||
            document.hidden ||
            carousel.matches(":focus-within") ||
            !track.clientWidth
        ) return;
        showSlide(currentIndex() + 1);
    }, 5000);
}
