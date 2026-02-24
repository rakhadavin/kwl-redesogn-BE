import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_consent_kwluser_consent'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserConsent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreed_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when consent was agreed')),
                ('consent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_consents', to='authentication.consent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_consents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'consent')},
            },
        ),
        # Hapus M2M lama (tanpa through)
        migrations.RemoveField(
            model_name='kwluser',
            name='consent',
        ),
        # Tambah M2M baru (dengan through)
        migrations.AddField(
            model_name='kwluser',
            name='consent',
            field=models.ManyToManyField(blank=True, related_name='users', through='authentication.UserConsent', to='authentication.consent'),
        ),
    ]