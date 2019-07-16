from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser



# Create your models here.
class User(AbstractUser,BaseModel):
	class Meta:
		db_table ='df_user'
		verbose_name = '用户'
		verbose_name_plural = verbose_name

class Address(BaseModel):
	user = models.ForeignKey('User')
	receiver = models.CharField(max_length=20)
	addr = models.CharField(max_length=240)
	zip_code = models.CharField(max_length=20)
	phone = models.CharField(max_length=20)
	is_default = models.BooleanField(default=False)

	class Meta:
		db_table = 'df_addr'
		verbose_name = '地址'
		verbose_name_plural = verbose_name