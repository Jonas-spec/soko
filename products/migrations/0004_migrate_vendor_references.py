from django.db import migrations

def migrate_vendor_references(apps, schema_editor):
    # Get the current state of the models
    Product = apps.get_model('products', 'Product')
    Vendor = apps.get_model('accounts', 'Vendor')
    User = apps.get_model('auth', 'User')
    
    # For each product, find the corresponding vendor
    for product in Product.objects.all():
        try:
            # Get the user that was set as the vendor
            user = User.objects.get(id=product.vendor_id)
            # Find the vendor that corresponds to this user
            vendor = Vendor.objects.get(user=user)
            # Update the product's vendor to point to the Vendor instance
            product.vendor = vendor
            product.save(update_fields=['vendor'])
        except (User.DoesNotExist, Vendor.DoesNotExist):
            # If the user or vendor doesn't exist, we'll skip this product
            # You might want to handle this case differently
            print(f"Warning: Could not find vendor for product {product.id}")
            continue

def reverse_migrate_vendor_references(apps, schema_editor):
    # This is the reverse migration, in case we need to roll back
    Product = apps.get_model('products', 'Product')
    Vendor = apps.get_model('accounts', 'Vendor')
    
    for product in Product.objects.all():
        if hasattr(product.vendor, 'user'):
            product.vendor = product.vendor.user
            product.save(update_fields=['vendor'])

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_vendor'),
        ('accounts', '0003_customer_vendor_delete_user'),  # Make sure this is correct
    ]

    operations = [
        migrations.RunPython(migrate_vendor_references, reverse_migrate_vendor_references),
    ]