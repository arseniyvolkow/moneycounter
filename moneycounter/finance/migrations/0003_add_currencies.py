from django.db import migrations

def add_currencies(apps, schema_editor):
    Currency = apps.get_model('finance', 'Currency')
    
    currencies = [
        {'code': 'USD', 'name': 'US Dollar'},
        {'code': 'EUR', 'name': 'Euro'},
        {'code': 'KZT', 'name': 'Kazakhstani Tenge'},
        {'code': 'RUB', 'name': 'Russian Ruble'},
        {'code': 'GBP', 'name': 'British Pound'},
        {'code': 'JPY', 'name': 'Japanese Yen'},
        {'code': 'CNY', 'name': 'Chinese Yuan'},
        {'code': 'TRY', 'name': 'Turkish Lira'},
        {'code': 'THB', 'name': 'Thai Baht'},
        {'code': 'AED', 'name': 'United Arab Emirates Dirham'},
    ]

    for curr in currencies:
        Currency.objects.get_or_create(
            code=curr['code'],
            defaults={'name': curr['name']}
        )

def remove_currencies(apps, schema_editor):
    Currency = apps.get_model('finance', 'Currency')
    codes = ['USD', 'EUR', 'KZT', 'RUB', 'GBP', 'JPY', 'CNY', 'TRY', 'THB', 'AED']
    Currency.objects.filter(code__in=codes).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_add_standard_categories'),
    ]

    operations = [
        migrations.RunPython(add_currencies, remove_currencies),
    ]