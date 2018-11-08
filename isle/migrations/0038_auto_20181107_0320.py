# Generated by Django 2.0.7 on 2018-11-06 17:20

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('isle', '0037_auto_20181102_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labseventblock',
            name='block_type',
            field=models.CharField(max_length=255, verbose_name='Тип блока'),
        ),
        migrations.AlterField(
            model_name='labseventblock',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='labseventblock',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='isle.Event', verbose_name='Мероприятие'),
        ),
        migrations.AlterField(
            model_name='labseventblock',
            name='order',
            field=models.IntegerField(verbose_name='Порядок отображения в рамках мероприятия'),
        ),
        migrations.AlterField(
            model_name='labseventblock',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='labseventblock',
            name='uuid',
            field=models.CharField(max_length=36, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='isle.LabsEventBlock', verbose_name='Блок мероприятия'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='check',
            field=models.TextField(verbose_name='Способ проверки результата'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='fix',
            field=models.TextField(verbose_name='Способ фиксации результата'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='meta',
            field=jsonfield.fields.JSONField(default=None, null=True, verbose_name='Ячейки, в которые попадает ЦС'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='order',
            field=models.IntegerField(verbose_name='Порядок отображения в рамках блока мероприятия'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='result_format',
            field=models.CharField(max_length=50, verbose_name='Формат работы'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='title',
            field=models.TextField(verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='labseventresult',
            name='uuid',
            field=models.CharField(max_length=36, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterUniqueTogether(
            name='labsuserresult',
            unique_together=set(),
        ),
    ]
