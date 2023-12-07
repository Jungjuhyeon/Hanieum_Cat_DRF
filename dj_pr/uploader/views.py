from multiprocessing import AuthenticationError
import random
import time
from PIL import Image
import torchvision.transforms as transforms

import uuid
import jwt
import requests
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import render
from rest_framework import  status, parsers
from rest_framework.views import APIView
import torch
from uploader.utils import make_signature
from .models import Auth, Diagnosis, Upload, Pet, User
from .serializers import DiagnosisSerializer, PetSerializer, UploadSerializer, UserSerializer
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobClient
from datetime import datetime
from rest_framework.generics import get_object_or_404
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from django.views import View
from django.http import HttpResponse, JsonResponse
import json
from django.http import Http404
import os, json
from rest_framework.parsers import JSONParser

# swagger 
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi 
from .serializers import *
##  ImageField Swagger에 표시
from rest_framework.decorators import parser_classes


# blob connection string 
from azure.storage.blob import BlobServiceClient , ContainerClient
connectionString_blob = "DefaultEndpointsProtocol=https;AccountName=azurefunctionsstorages;AccountKey=엑세스 키"
blob_client = BlobServiceClient.from_connection_string(conn_str=connectionString_blob)

#회원가입 api
class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    
    def post(self, request):
        user = request.data
       
        
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    
        return Response(serializer.data,status=status.HTTP_200_OK)

#로그인 api

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    
    def post(self, request):
        
        user= request.data
        
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception= True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
          
#sms 보내기 api
             
class SmsSendView(APIView):
    def send_sms(self, phone, auth):
        
        timestamp = str(int(time.time() * 1000))  
        
        headers = {
            'Content-Type': "application/json; charset=utf-8", # 네이버 참고서 차용
            'x-ncp-apigw-timestamp': timestamp, # 네이버 API 서버와 5분이상 시간차이 발생시 오류
            'x-ncp-iam-access-key': 'Naver_인증키',
            'x-ncp-apigw-signature-v2': make_signature(timestamp) # utils.py 이용
        }
        
        body= {
            "type": "SMS", 
            "contentType": "COMM",
            "from": "인증번호 보내는 번호", # 사전에 등록해놓은 발신용 번호 입력, 타 번호 입력시 오류
            "content":f"[인증번호:{auth}]", # 메세지를 이쁘게 꾸며보자
            "messages": [{"to": f"{phone}"}] # 네이버 양식에 따른 messages.to 입력
        }
        body = json.dumps(body)

        requests.post('https://sens.apigw.ntruss.com/sms/v2/services/ncp:sms:kr:313328416753:han_cat_sms/messages', headers=headers, data=body)
    
    def post(self, request):
        data = request.data
        try:
            input_mobile_num = data["phone"]
            auth_num = random.randint(1000, 10000) # 랜덤숫자 생성, 4자리로 계획하였다.
            auth_mobile = Auth.objects.get(phone=input_mobile_num)
            auth_mobile.auth= auth_num
            

            auth_mobile.save()
            self.send_sms(phone=input_mobile_num, auth=auth_num)
            response_data = {'message' : '인증번호를 보냈습니다.'}

        except Auth.DoesNotExist:
            Auth.objects.create(
                phone=input_mobile_num,
                username=data["name"],
                auth=auth_num,
            ).save()
            self.send_sms(phone=input_mobile_num, auth=auth_num)
            response_data = {'message' : '인증번호를 보냈습니다.'}
    
        return Response(response_data, status=status.HTTP_200_OK)

# 네이버 SMS 인증번호 검증
class SMSVerificationView(APIView):
    def post(self, request):
        data = json.loads(request.body)

        try:
            verification = Auth.objects.get(phone=data['phone'])

            if verification.auth == data['auth']:
                response_data = {'message': "인증이 완료되었습니다."}
                return Response(response_data, status=status.HTTP_200_OK)


            else:
                response_data = {'auth':["인증번호가 일치하지 않습니다."]}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Auth.DoesNotExist:
                response_data = {'auth':["해당 번호에 대한 정보가 없습니다."]}
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
        
# userId 찾기 인증 api       
class UserIdLostView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self,request):
        data = json.loads(request.body)
        
        try:
            user = User.objects.get(username=data['name'], phone=data['phone'])
            auth_num = random.randint(1000, 10000) 
            
            # 인증번호를 auth_sms 테이블의 해당 번호의 auth 열에 저장
            auth_sms, created = Auth.objects.get_or_create(phone=user.phone)
            auth_sms.auth = auth_num
            auth_sms.save()
            
            sms_sender = SmsSendView()
            sms_sender.send_sms(phone =user.phone, auth = auth_num) #인증번호 전
            response_data = {"message":'인증번호를 전송했습니다.'}
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist: #해당하는 유저가 없다면

            response_data = {'auth': ["이름 혹은 폰번호를 다시 확인해주세요."]}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    
#userId 찾기 인증 후 값반환 api
  
class UserIdRecoveryView(APIView):
    
    def post(self, request):
        data = request.data
        
        try:
            user = User.objects.get(username=data['name'], phone=data['phone'])
            auth = data['auth']
            auth_record = Auth.objects.get(phone=user.phone)
            
            if auth_record.auth == auth:
                response_data = {'message': "인증이 완료되었습니다.","userIdx" : user.userIdx, "users_id": user.users_id}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {'auth':['인증번호가 일치하지 않습니다.']}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            response_data = {'auth':['해당 유저의 정보를 찾을 수 없습니다.']}
            
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Auth.DoesNotExist: #해당 휴대폰 번호에 대한 인증 정보가 없습니다
            response_data = {'auth':['휴대폰 번호를 다시 확인하세요.']}
            
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)            
        
 
#password 찾기인증 api        
        
class UserPasswordLostView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self,request):
        data = json.loads(request.body)
        
        try:
            user = User.objects.get(users_id=data['users_id'], phone=data['phone'])
            auth_num = random.randint(1000, 10000) 
            
            # 인증번호를 auth_sms 테이블의 해당 번호의 auth 열에 저장
            auth_sms, created = Auth.objects.get_or_create(phone=user.phone)
            auth_sms.auth = auth_num
            auth_sms.save()
            
            sms_sender = SmsSendView()
            sms_sender.send_sms(phone =user.phone, auth = auth_num)
            
            response_data = {"message":'인증번호를 전송했습니다.'}
            return Response(response_data, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            response_data = {"auth":['해당 유저의 정보를 찾을 수 없습니다.']}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
#password 찾기 인증확인 api        

class UserPasswordRecoveryView(APIView):
    
    def post(self, request):
        data = request.data
        try:
            user = User.objects.get(users_id=data['users_id'], phone=data['phone'])
            auth = data['auth']
            auth_record = Auth.objects.get(phone=user.phone)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
                
            if auth_record.auth == auth:
                response_data = {'message': "인증이 완료되었습니다.","userIdx": user.userIdx,"access_token": access_token}
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"auth":['인증번호가 일치하지 않습니다.']}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            response_data = {"auth":['해당 유저의 정보를 찾을 수 없습니다.']}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Auth.DoesNotExist: #해당 휴대폰 번호에 대한 인증 정보가 없습니다
            response_data = {"auth":['번호를 다시 확인하세요.']}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)  
        
#password 재설정 api

class UserPasswordRestoreView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        data = request.data
        try:
            userIdx = get_user_idx_from_jwt(request)
            user = User.objects.get(userIdx=userIdx)
        except User.DoesNotExist:
            response_data = {"auth":['해당 유저의 정보를 찾을 수 없습니다.']}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)  

        serializer = PasswordRestoreSerializer(data=data, context={'userIdx': userIdx})
        
        
        
        if serializer.is_valid():
            new_password = serializer.validated_data['password']

            # 비밀번호 업데이트
            user.set_password(new_password)
            user.save()
            
            response_data = {"message":'비밀번호가 변경되었습니다.'}
            return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# jwt토큰에 있는 user_Idx(식별자) 가져오기 함수

def get_user_idx_from_jwt(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthenticationFailed('Invalid token')
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token,'5(!&t(*4iz)c1k(=ygr8ivbpeoe-p7ex7uz@7rvzdg+9u8!5p+', algorithms=['HS256'])
        return payload.get('userIdx')
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
    


#APIView를 상속받음

def upload_to_blob(userIdx, petIdx, photo):
        
    user = User.objects.get(userIdx=userIdx)
    # react에서 form data로 보내주면 아래와 같이 받음
    users_id = user.users_id
        
    container_name =  str(users_id) + "-" + str(petIdx) + "-" + "photos"
    now = datetime.now()

    # 컨테이너 생성 또는 가져오기
    container_client = blob_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()
    
    # 파일 이름에 현재 시간과 무작위 UUID 값을 포함
    file_upload_name = f"{petIdx}-{now.strftime('%Y-%m-%d-%H.%M.%S.%f')}_{str(uuid.uuid4())}.png"
    container_client.upload_blob(name=file_upload_name, data=photo, overwrite=True)

    blob_url = f"https://azurefunctionsstorages.blob.core.windows.net/{container_name}/{file_upload_name}"
    return blob_url


class PredictedImageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        userIdx = get_user_idx_from_jwt(request)
        petIdx = request.POST['petIdx']
        photo = request.FILES.__getitem__('photo')
        
        blob_url = upload_to_blob(userIdx,petIdx,photo)
        class_name = get_prediction(photo)
        
        diag_data= request.data
        diag_data['petresult'] = class_name
        diag_data['photo'] = blob_url
        
        diagnosis_serializer =DiagnosisSerializer(data = diag_data)
        if diagnosis_serializer.is_valid():
            diagnosis_serializer.save()
            return Response(diagnosis_serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(diagnosis_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#ai모델 예측결과 반환 함수
def get_prediction(image_file):
 # AI 모델 로드
    model = torch.load('dj_pr/uploader/model.pth')
    model.eval()
    

    # 이미지 처리 및 예측
    image = Image.open(image_file)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image)
        _, preds = torch.max(outputs, 1)

    # 예측 클래스 가져오기
    class_names = ["abnormal", "normal"]
    class_idx = torch.argmax(outputs)
    class_name = class_names[int(class_idx.item())]  # 클래스 이름으로 변환

    return class_name


#해당 유저의 펫의 진단결과 나타내기
class DiagnosisRetrieveView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user_idx = get_user_idx_from_jwt(request) #유저Idx(식별자)를 가져옴.
        pet_name = request.GET.get('petname',None)
        
        if not pet_name:
            response_data = {"petname": ["petname을 제공해야 합니다."]}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        pet_diagnosis = Diagnosis.objects.filter(petIdx__userIdx=user_idx, petIdx__petname=pet_name).order_by('-diagday')
        
        if not pet_diagnosis.exists():
            response_data = {"petname": [f"{pet_name}에 대한 진단 결과를 찾을 수 없습니다."]}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        diagnosis_serializer = DiagnosisSerializer(pet_diagnosis, many=True)
        return Response(diagnosis_serializer.data, status=status.HTTP_200_OK)
                    
#해당 유저의 과거 진단 내역 가져옴 
class DiagnosisListView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user_idx = get_user_idx_from_jwt(request)

        try:
            pets = Pet.objects.filter(userIdx=user_idx)
            pet_idx_list = [pet.petIdx for pet in pets]
            diagnosis = Diagnosis.objects.filter(petIdx__in=pet_idx_list).order_by('-diagday')
            
            # 진단 데이터가 없을 경우
            if not diagnosis:
                response_data = {"Pet": ['진단한 애완동물이 없습니다.']}
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            diagnosis_serializer = DiagnosisSearchSerializer(diagnosis, many=True)
            return Response(diagnosis_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # 다른 예외 처리를 원할 경우 이곳에 추가할 수 있습니다.
            response_data = {"error": [str(e)]}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# 해당 유저의 펫 조회
class PetListView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            userIdx = get_user_idx_from_jwt(request)
            pet = Pet.objects.filter(userIdx=userIdx)
            
            if pet.exists():
                Pet_Serializer = PetSerializer(pet, many=True)
                return Response(Pet_Serializer.data, status=status.HTTP_200_OK)
            else:
                response_data = {'Pet': ['등록한 애완동물이 없습니다.']}
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            response_data = {'detail': str(e)}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

#펫 추가하기
class PetCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        userIdx = get_user_idx_from_jwt(request)
        pet_data = JSONParser().parse(request)
        pet_data['userIdx'] = userIdx
        
        if Pet.objects.filter(petname=pet_data['petname'], userIdx=userIdx).exists():
            response_data = {"petname":["이미 등록된 애완동물입니다."]}
            return Response(response_data, status=status.HTTP_409_CONFLICT)
            
        pet_serializer = PetSerializer(data=pet_data)
        if pet_serializer.is_valid():
            pet_serializer.save()
            # collection_pet.insert(pet_serializer.data)
            return Response(pet_serializer.data,status=status.HTTP_200_OK)    
        return Response(pet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
