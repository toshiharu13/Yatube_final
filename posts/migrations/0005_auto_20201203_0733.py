# Generated by Django 2.2.6 on 2020-12-03 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20201203_0728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Дайте короткое название группе', max_length=200, verbose_name='группа/сообщество'),
        ),
    ]