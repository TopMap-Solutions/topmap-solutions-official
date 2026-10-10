# Products, training, and manuals

Product content is managed in Wagtail at `/cms/` under **Snippets**. Licensing
records are separate and remain in Django admin.

## Publishing a product

1. Open **Products** in Wagtail snippets.
2. Add a name, URL slug, summary, and stable product code.
3. Add body blocks for headings, text, images, embedded video, tips, or warnings.
4. Add SEO title and description.
5. Select **Published** only when the product is ready for the public site.

The product code connects editorial content to licensing conceptually. It should
match the licensed-product code and must not be changed after release. The site
does not automatically create or modify licensing records from Wagtail.

Public product URLs are:

```text
/products/
/products/<product-slug>/
```

Existing `/products/` links remain valid.

## Manuals and training

Open **Product guides** in Wagtail snippets. Each guide belongs to a product and
can be classified as a manual, training article, or video guide. Guides support
the same structured blocks as product pages and have independent SEO fields.

For video, paste a supported YouTube or Vimeo URL into a video block. Prefer an
external streaming provider over uploading large video files to website media.
Only embed videos that TopMap has permission to publish, and verify their privacy
settings before publishing.

Public guide URLs are:

```text
/products/<product-slug>/guides/<guide-slug>/
```

Draft products and guides return 404 and are excluded from the sitemap. A guide
also remains inaccessible when its parent product is not published.

