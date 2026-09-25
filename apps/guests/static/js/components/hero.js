export function initHeroGallery(gallery) {
    const slides = gallery?.querySelector(".hero-slides");
    const navigation = gallery?.querySelector(".hero-dots");
    if (!slides || !navigation) return;

    const dots = [...navigation.querySelectorAll(".hero-dot")];
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const currentIndex = () => Math.round(slides.scrollLeft / (slides.clientWidth || 1));
    const showSlide = (index) => {
        slides.scrollTo({
            left: index * slides.clientWidth,
            behavior: reducedMotion.matches ? "instant" : "smooth",
        });
    };
    const updateDots = () => {
        const current = currentIndex();
        dots.forEach((dot, index) => {
            dot.setAttribute("aria-current", String(index === current));
        });
    };

    navigation.hidden = false;
    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => showSlide(index));
    });
    slides.addEventListener("scroll", updateDots, { passive: true });
    window.addEventListener("resize", updateDots);
    updateDots();

    window.setInterval(() => {
        if (reducedMotion.matches || document.hidden || gallery.matches(":hover, :focus-within")) return;
        if (!slides.clientWidth) return;
        showSlide((currentIndex() + 1) % dots.length);
    }, 5000);
}
