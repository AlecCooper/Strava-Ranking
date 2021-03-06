# Generated by Django 3.1.2 on 2020-11-11 21:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'permissions': [('member', 'Is a member of the ranking')],
            },
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('segment_id', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=50)),
                ('distance', models.FloatField(null=True)),
                ('formated_distance', models.CharField(max_length=50, null=True)),
                ('ranking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ranking_app.ranking')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Performance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.FloatField(null=True)),
                ('formated_time', models.CharField(max_length=50, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('ranking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ranking_app.ranking')),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ranking_app.segment')),
            ],
        ),
    ]
