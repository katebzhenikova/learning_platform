# Generated by Django 5.1 on 2024-08-28 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_payment_pay_course"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="pay_amount",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="сумма оплаты",
            ),
        ),
    ]
