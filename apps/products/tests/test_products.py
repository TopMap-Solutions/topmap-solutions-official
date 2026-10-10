from django.test import TestCase

from apps.products.models import Product, ProductGuide


class ProductPublishingTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Parcel Buddy",
            slug="parcel-buddy",
            product_code="parcel-buddy",
            summary="A parcel workflow plugin.",
            is_published=True,
        )

    def test_catalog_only_shows_published_products(self):
        Product.objects.create(
            name="Private product",
            slug="private",
            product_code="private",
            summary="Draft",
            is_published=False,
        )
        response = self.client.get("/products/")
        self.assertContains(response, "Parcel Buddy")
        self.assertNotContains(response, "Private product")
        self.assertContains(response, "GIS Products, Training &amp; Manuals")

    def test_product_has_manual_training_and_video_guides(self):
        for order, kind in enumerate(ProductGuide.Kind.values):
            ProductGuide.objects.create(
                product=self.product,
                title=f"{kind} guide",
                slug=f"guide-{order}",
                kind=kind,
                summary="Learn the workflow.",
                is_published=True,
                display_order=order,
            )
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, "Training and guides")
        self.assertContains(response, "Manual")
        self.assertContains(response, "Training")
        self.assertContains(response, "Video guide")

    def test_draft_product_and_guide_are_not_public(self):
        draft_product = Product.objects.create(
            name="Draft", slug="draft", product_code="draft", summary="Draft"
        )
        draft_guide = ProductGuide.objects.create(
            product=self.product, title="Hidden", slug="hidden"
        )
        self.assertEqual(
            self.client.get(draft_product.get_absolute_url()).status_code, 404
        )
        self.assertEqual(
            self.client.get(draft_guide.get_absolute_url()).status_code, 404
        )

    def test_guide_uses_editorial_seo_and_navigation(self):
        first = ProductGuide.objects.create(
            product=self.product,
            title="Install",
            slug="install",
            is_published=True,
            seo_title="Install Parcel Buddy",
            search_description="Installation instructions.",
        )
        second = ProductGuide.objects.create(
            product=self.product,
            title="Activate",
            slug="activate",
            is_published=True,
            display_order=1,
        )
        response = self.client.get(first.get_absolute_url())
        self.assertContains(response, "Install Parcel Buddy | TopMap Solutions")
        self.assertContains(response, "Installation instructions.")
        self.assertContains(response, second.get_absolute_url())
