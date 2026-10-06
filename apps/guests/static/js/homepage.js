import { initHeroGallery } from "./components/hero.js";
import { initTestimonialsCarousel } from "./components/testimonials.js";

document.querySelectorAll(".hero-visual").forEach(initHeroGallery);
document
    .querySelectorAll("[data-testimonials-carousel]")
    .forEach(initTestimonialsCarousel);
