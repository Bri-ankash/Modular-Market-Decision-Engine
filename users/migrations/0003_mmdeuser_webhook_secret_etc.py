from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_mmdeuser_managers_alter_mmdeuser_google_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mmdeuser',
            name='webhook_secret',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        # migrations.AddField(
        #     model_name='mmdeuser',
        #     name='is_active_subscription',
        #     field=models.BooleanField(default=False),
        # ),
        migrations.AddField(
            model_name='mmdeuser',
            name='allowed_markets',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='mmdeuser',
            name='subscription_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mmdeuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default='2026-05-14 00:00:00'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mmdeuser',
            name='subscription_plan',
            field=models.CharField(choices=[('FREE', 'Free'), ('BASIC', 'Basic $30'), ('PRO', 'Pro $40'), ('ELITE', 'Elite $50')], default='FREE', max_length=20),
        ),
    ]
