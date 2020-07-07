# Generated by Django 3.0.6 on 2020-05-06 13:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('nhsorganisations', '0012_auto_20190916_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganisationType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='e.g. "Arms Length Bodies"', max_length=100, verbose_name='name (plural)')),
                ('name_singular', models.CharField(help_text='e.g. "Arms Length Body"', max_length=100, verbose_name='name (singular)')),
                ('mnemonic', models.SlugField(help_text='e.g. "alb"', unique=True, verbose_name='mnemonic name (singular)')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'organisation type',
                'verbose_name_plural': 'organisation types',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='organisation',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nhsorganisations.OrganisationType', verbose_name='type'),
        ),
    ]
