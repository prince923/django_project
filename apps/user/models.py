from django.db import models
from django.contrib.auth.models import AbstractUser , UserManager  as _UserManager


# Create your models here.
class UserManager(_UserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username=username, email=email, password=password, **extra_fields)

    def create_superuser(self, username, password,email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class UserModel(AbstractUser):
    """
    help_text :   帮助文本信息,  用于admin站点
    verbose_name :  api 接口文档会用到
    error_message :   错误信息
    """
    mobile = models.CharField(max_length=11,unique=True,help_text="手机号",verbose_name='手机号',error_messages={
        'unique':'此手机号已经被注册'
    })
    email_active = models.BooleanField(default=False,help_text="邮箱验证状态",verbose_name="邮箱验证状态")

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    REQUIRED_FIELDS = ['mobile']   # 创建super_user 的时候需要输入mobile字段,需要在列表中新加字段
    objects = UserManager()


