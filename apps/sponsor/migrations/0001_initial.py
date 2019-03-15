# Generated by Django 2.1.7 on 2019-03-15 19:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='name')),
                ('banner', models.CharField(blank=True, help_text='Use a mirrored image of at least a height of 150px.', max_length=100, verbose_name='Banner url')),
                ('logo', models.CharField(blank=True, help_text='Use a mirrored image of at least a height of 150px.', max_length=100, verbose_name='Logo url')),
                ('website', models.URLField(verbose_name='website')),
            ],
        ),
        migrations.CreateModel(
            name='SponsorRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(help_text='higher priority means closer to the top of the sponsor list.', verbose_name='priority')),
                ('lan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lan.LAN')),
                ('sponsor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sponsor.Sponsor')),
            ],
            options={
                'ordering': ['-priority'],
            },
        ),
    ]
