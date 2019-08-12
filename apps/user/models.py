from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser



# Create your models here.
class User(AbstractUser,BaseModel):
	class Meta:
		db_table ='df_user'
		verbose_name = '用户'
		verbose_name_plural = verbose_name

class AddressManager(models.Manager):
    '''地址模型管理器类'''
    # 1.改变原有查询的结果集:all()
    # 2.封装方法:用户操作模型类对应的数据表(增删改查)
    def get_default_address(self, user):
        '''获取用户默认收货地址'''
        # self.model:获取self对象所在的模型类
        try:
            address = self.get(user=user, is_default=True)  # models.Manager
        except self.model.DoesNotExist:
            # 不存在默认收货地址
            address = None

        return address

class Address(BaseModel):
	user = models.ForeignKey('User')
	receiver = models.CharField(max_length=20)
	addr = models.CharField(max_length=240)
	zip_code = models.CharField(max_length=20)
	phone = models.CharField(max_length=20)
	is_default = models.BooleanField(default=False)

	objects = AddressManager()

	class Meta:
		db_table = 'df_addr'
		verbose_name = '地址'
		verbose_name_plural = verbose_name

