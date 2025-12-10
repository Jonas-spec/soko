from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_migrate_vendor_references'),  # The previous migration
        ('accounts', '0004_user_model_restructure'),  # The accounts migration we created
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='accounts.vendor',
                verbose_name='vendor'
            ),
        ),
    ]