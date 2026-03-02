from django.db import migrations

def add_standard_categories(apps, schema_editor):
    Category = apps.get_model('finance', 'Category')
    
    standard_categories = [
        # Income
        {'name': 'Salary', 'type': 'INCOME', 'is_essential': True},
        {'name': 'Business', 'type': 'INCOME', 'is_essential': False},
        {'name': 'Gifts', 'type': 'INCOME', 'is_essential': False},
        
        # Expense
        {'name': 'Food', 'type': 'EXPENSE', 'is_essential': True},
        {'name': 'Restaurants', 'type': 'EXPENSE', 'is_essential': False},
        {'name': 'Clothes', 'type': 'EXPENSE', 'is_essential': True},
        {'name': 'Transport', 'type': 'EXPENSE', 'is_essential': True},
        {'name': 'Housing', 'type': 'EXPENSE', 'is_essential': True},
        {'name': 'Entertainment', 'type': 'EXPENSE', 'is_essential': False},
        {'name': 'Health', 'type': 'EXPENSE', 'is_essential': True},
        {'name': 'Education', 'type': 'EXPENSE', 'is_essential': False},
        {'name': 'Other', 'type': 'EXPENSE', 'is_essential': False},
    ]

    for cat_data in standard_categories:
        Category.objects.get_or_create(
            user=None,  # Standard categories have no user
            name=cat_data['name'],
            type=cat_data['type'],
            defaults={'is_essential': cat_data['is_essential']}
        )

def remove_standard_categories(apps, schema_editor):
    Category = apps.get_model('finance', 'Category')
    Category.objects.filter(user__isnull=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_standard_categories, remove_standard_categories),
    ]
