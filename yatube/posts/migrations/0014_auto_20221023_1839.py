# Generated by Django 2.2.16 on 2022-10-23 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20221023_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='theme',
            field=models.CharField(blank=True, default='', help_text='Тема поста', max_length=50, verbose_name='Тема поста'),
        ),
    ]
