import re
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Auth, Diagnosis, Pet, User

class RegistrationSerializer(serializers.ModelSerializer):
    
    userIdx = serializers.IntegerField(read_only=True)
    password = serializers.CharField(max_length = 128,min_length = 8,write_only = True
    )
    password_check = serializers.CharField(max_length = 128,min_length = 8,write_only = True
    )
    
    class Meta:
        model = User
        fields = [
            'userIdx',
            'users_id', 
            'username',
            'phone',
            'email',
            'password',
            'password_check',
            ]
        
    def validate(self,data):
        if data['password'] != data['password_check']:
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지않습니다."})
        if not data['phone'].isdigit():  # 숫자가 아닌 값이라면
            raise serializers.ValidationError({'phone':'번호를 확인해주세요.'})
        if len(data['phone']) !=11:
            raise serializers.ValidationError({'phone':'번호를 확인해주세요.'})
        email_regex = r'^\S+@\S+\.\S+$'
        if not re.match(email_regex, data['email']):
            raise serializers.ValidationError({'email': '올바른 이메일 형식이 아닙니다.'})
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    userIdx = serializers.IntegerField( read_only=True)
    username = serializers.CharField(max_length= 30, read_only=True)
    users_id = serializers.CharField(max_length = 30)
    email = serializers.EmailField(max_length= 30, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    last_login = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    
    def validate(self,data):
        users_id = data.get('users_id', None)
        password = data.get('password', None)
        
        # db와 매칭시킨다. 없을경우 None 반환시킴
        user = authenticate(users_id=users_id, password=password)
        
        #일치하는 user가 없을때
        if user is None:
            raise serializers.ValidationError(
                '아이디와 비밀번호를 확인하세요.'
            )
        #해당 유저가 비활성화일때
        if not user.is_active:
            raise serializers.ValidationError(
                '해당 유저가 비활성화입니다.'
            )
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        
        return{
            'userIdx' : user.userIdx,
            'users_id' : user.users_id,
            'username': user.username,
            'email': user.email,
            'last_login': user.last_login,
            'access_token': access_token,
            'refresh_token': refresh_token
        }

class PasswordRestoreSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    password_check = serializers.CharField(max_length=128, min_length=8, write_only=True)

    def validate(self, data):
        userIdx = self.context.get('userIdx') 
        user =User.objects.get(userIdx = userIdx)
        
        if user.check_password(data['password']):  #암호화된 비밀번호
            raise serializers.ValidationError({"password": "이전 비밀번호와 같습니다."})
        
        if data['password'] != data['password_check']: #비밀번호 확인
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return data  


class DiagnosisSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()

    class Meta:
        model = Diagnosis
        fields = ['diagnosisIdx','petIdx','petresult','diagday','photo']
        
class DiagnosisSearchSerializer(serializers.ModelSerializer):
    petname = serializers.CharField(source='petIdx.petname')
    petage = serializers.CharField(source='petIdx.petage')
    petgender = serializers.CharField(source='petIdx.petgender')
    diagday = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Diagnosis
        fields = ['petname', 'petage', 'petgender', 'diagday', 'petresult', 'photo']

class UserSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()

    class Meta:
        model = User
        fields = '__all__'
        
class PetSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()

    class Meta:
        model = Pet
        fields = ['petIdx','userIdx','petname','petage','petgender','petcomment']
        
class AuthSerializer(serializers.ModelSerializer):
    message = serializers.CharField()
    # id = serializers.IntegerField()

    class Meta:
        model = Auth
        fields = '__all__'
        
