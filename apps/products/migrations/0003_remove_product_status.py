from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_product_highlight_on_homepage"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="status",
        ),
    ]
