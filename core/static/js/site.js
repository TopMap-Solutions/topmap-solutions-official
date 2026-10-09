const backToTop = document.querySelector("[data-back-to-top]");

if (backToTop) {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updateVisibility = () => {
        backToTop.classList.toggle("is-visible", window.scrollY > 500);
    };

    backToTop.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: reducedMotion.matches ? "instant" : "smooth",
        });
    });
    window.addEventListener("scroll", updateVisibility, { passive: true });
    updateVisibility();
}
