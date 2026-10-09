from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageBlock


class CalloutBlock(blocks.StructBlock):
    style = blocks.ChoiceBlock(
        choices=[("note", "Note"), ("tip", "Tip"), ("warning", "Warning")],
        default="note",
    )
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock(features=["bold", "italic", "link", "ul", "ol"])

    class Meta:
        icon = "warning"
        template = "products/blocks/callout.html"


def editorial_blocks():
    return [
        ("heading", blocks.CharBlock(form_classname="title")),
        (
            "rich_text",
            blocks.RichTextBlock(
                features=[
                    "h2",
                    "h3",
                    "h4",
                    "bold",
                    "italic",
                    "link",
                    "ul",
                    "ol",
                    "blockquote",
                    "hr",
                ]
            ),
        ),
        ("image", ImageBlock()),
        ("video", EmbedBlock(help_text="Paste a YouTube or Vimeo URL.")),
        ("callout", CalloutBlock()),
    ]
