
import jwt, json, requests, time
from datetime import datetime,timedelta
from django.conf import settings
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# auto_now=True : 수정 일자 = 최종 수정일자, django model이 save 될 때마다 현재날짜로 갱신됨! 
# auto_now_add=True : 생성일자, 갱신이 안됨, django model이 최초 저장 될때만 현재날짜를 저장함.
# Create your models here.
    
class UserManager(BaseUserManager):
    def create_user(self,users_id, password, email, **extra_fields):
        
        if users_id is None:
            raise TypeError('Please enter ID.')

        if email is None:
            raise TypeError('Please enter email.')

        if password is None:
            raise TypeError('Please enter password.')
        
        extra_fields.pop('password_check', None)
        
        user = self.model(
            users_id = users_id,
            email = self.normalize_email(email),
            **extra_fields
        )
        
        # django 에서 제공하는 password 설정 함수
        user.set_password(password)
        user.save()
        
        return user
        
        # admin user
    def create_superuser(self, users_id, password, email,  **extra_fields):
        
        if password is None:
            raise TypeError('Superuser must have a password.')
        
        extra_fields.pop('password_check', None)
        # "create_user"함수를 이용해 우선 사용자를 DB에 저장
        user = self.create_user(users_id, password, email, **extra_fields)
        # 관리자로 지정
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    userIdx = models.AutoField(primary_key=True)
    username = models.TextField(null=False)
    users_id = models.TextField(max_length=30, unique=True, null=False)
    password = models.TextField( null=False)
    email = models.TextField( unique=True,null=False)
    phone = models.TextField( unique=True,null=False)
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now = True, blank=True)
    status = models.TextField(blank=True,max_length=1, default='A')
    
    USERNAME_FIELD = 'users_id'
    
    #superuser만들떄 필요한 필드
    REQUIRED_FIELDS = [
        'username',
        'phone',
        'email'

    ]

    # 헬퍼 클래스 사용
    objects = UserManager()
    
    @property
    def token(self):
        return self._generate_jwt_token( )

    def _generate_jwt_token(self):
        dt = datetime.now( ) + timedelta(days=60)

        token = jwt.encode({
            'userIdx': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')
        
        
        return token
    
class Auth(models.Model):
    phone = models.CharField(max_length=11, primary_key=True)
    username = models.TextField()
    auth = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now = True, blank=True)

    class Meta:
        db_table = 'auth_sms'
    
class Pet(models.Model):
    petIdx= models.AutoField(primary_key=True)
    userIdx = models.ForeignKey("User", to_field="userIdx", on_delete=models.CASCADE, db_column="userIdx")
    petname = models.TextField(null=False)
    petage = models.IntegerField(null=False)
    petgender = models.TextField(null=False)
    petcomment = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now = True, blank=True)
    status = models.TextField(blank=True,max_length=1, default='A')
    
    
class Diagnosis(models.Model):
    diagnosisIdx = models.AutoField(primary_key=True)
    petIdx = models.ForeignKey("Pet", to_field="petIdx",  on_delete=models.CASCADE, blank=True, db_column="petIdx")
    petresult = models.TextField()
    #petresultper = models.TextField(blank=True,null = True)
    diagday = models.DateTimeField(auto_now_add=True,)
    photo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now = True, blank=True)
    status = models.TextField(blank=True,max_length=1, default='A')
    
class Upload(models.Model):
    id = models.AutoField(primary_key=True)
    photo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now = True, blank=True)