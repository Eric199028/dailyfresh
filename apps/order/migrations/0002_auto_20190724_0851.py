# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordergoods',
            name='update_time',
            field=models.DateTimeField(verbose_name='更新时间', auto_now=True),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='update_time',
            field=models.DateTimeField(verbose_name='更新时间', auto_now=True),
        ),
    ]
