from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="highlight_on_homepage",
            field=models.BooleanField(
                default=False,
                help_text="Show this product in the homepage tools section when published.",
            ),
        ),
    ]
