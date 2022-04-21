from datetime import date
import datetime
from API.models import MyUser, UserPicture
from API.serializers import MyUserSerializer, ImageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.views import APIView
import os
import boto3

import secrets

# Create statsD obj for cloudwatch
import statsd

# Create your views here.

class VarifyEmail(APIView):

    def get(self, request, format=None):
        data = request.GET
        user_email = data['email']
        token = data['token']
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        table = dynamodb.Table('EmailValidTable')
        response = table.get_item(
            Key={
                'EmailAddress': user_email,
                'Token': token
            }
        )
        item = response['Item']
        ttl = item['TTL']
        if item == None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if ttl < int(datetime.datetime.now()):
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = MyUser.objects.get(username=user_email)
        user.is_valid = True
        user.save()
        return Response(status=status.HTTP_200_OK)



class UserCreate(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def is_valid_data(data):

        if len(data)!=4:

            return None
        if 'first_name' in data.keys() and 'last_name' in data.keys() and 'username' in data.keys() and 'password' in data.keys():
            return data
        return None
        

    def post(self, request, format=None):
        
        counter = statsd.Counter('APICounter')
        counter.increment('CreateUserCall')
        counter.increment('TotalCall')

        data=UserCreate.is_valid_data(request.data.dict())
        if data is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_list = list(MyUser.objects.all())
        for _ in user_list:
            if _.get_username() == data['username']:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        user = MyUser(username=data['username'],first_name=data['first_name'],last_name=data['last_name'],email=data['username'],is_valid=False)
        user.set_password(data['password'])
        user.save()

        token = secrets.token_urlsafe(20)
        TTL = int((datetime.datetime.now() + datetime.timedelta(minutes=5)).timestamp())

        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        table = dynamodb.Table('EmailValidTable')
        table.put_item(
            Item={
                'EmailAddress': data['username'],
                'TTL': TTL,
                'Token': token,
            }
        )


        sns_client = boto3.client('sns',region_name='us-east-1')
        sns_client.publish(
            TopicArn = os.environ['TOPIC_ARN'],
            Message = 'Email:' + data['username'] + ':Token:' + token,
        )


        # serializer = MyUserSerializer(user)
        # data={
        #     'id':serializer.data['id'],
        #     'username': serializer.data['email'],
        #     'first_name': serializer.data['first_name'],
        #     'last_name': serializer.data['last_name'],
        #     'account_created': serializer.data['account_created'],
        #     'account_updated': serializer.data['account_updated'],
        #     }
        # return Response(data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_201_CREATED)
class UserDetail(APIView):
    """
    Retrieve, update a user data.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def is_valid_data(data):
        if len(data)!=3:
            return None
        if 'first_name' in data.keys() and 'last_name' in data.keys() and 'password' in data.keys():
            return data
        return None

    def get(self, request):
        
        counter = statsd.Counter('APICounter')
        counter.increment('GetUserCall')
        counter.increment('TotalCall')

        user=request.user
        serializer = MyUserSerializer(user)
        
        if not serializer.data['is_valid'] :
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        data={
            'id':serializer.data['id'],
            'username': serializer.data['email'],
            'first_name': serializer.data['first_name'],
            'last_name': serializer.data['last_name'],
            'account_created': serializer.data['account_created'],
            'account_updated': serializer.data['account_updated'],
            }
        return Response(data)

        
    def put(self, request, format=None):
        
        counter = statsd.Counter('APICounter')
        counter.increment('UpdateUserCall')
        counter.increment('TotalCall')
        
        user = request.user
        data=UserDetail.is_valid_data(request.data.dict())
        
        if not MyUserSerializer(user).data['is_valid'] :
            return Response(status=status.HTTP_403_FORBIDDEN)

        if data is not None:
            user.set_password(data['password'])
            user.first_name=data['first_name']
            user.last_name=data['last_name']
            user.account_updated=datetime.datetime.now()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserPic(APIView):
    """
    Retrieve, update a user data.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    #parser_classes = [FileUploadParser,]

    def post(self, request, format=None):
        

        counter = statsd.Counter('APICounter')
        counter.increment('UploadPictureCall')
        counter.increment('TotalCall')

        user = request.user
        serializer = MyUserSerializer(user)
        if not serializer.data['is_valid'] :
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        file_obj = request.FILES['profilePic']
        s3 = boto3.client('s3',region_name='us-east-1')


        bucketname=os.environ['S3_Bucket_Name']
        folder = str(serializer.data['id'])+'/'
        if UserPicture.objects.filter(user_id=serializer.data['id']).count() == 1:
            pic = UserPicture.objects.get(user_id=serializer.data['id'])
            Picserializer = ImageSerializer(pic)
            
            response = s3.delete_object(
                Bucket=bucketname,
                Key=folder+Picserializer.data['file_name']
            )
        
            pic.delete()

        s3.upload_fileobj(file_obj, bucketname, folder+file_obj._name)
        picURL='https://'+bucketname+'.s3.amazonaws.com/'+folder+file_obj._name
        pic = UserPicture(id=serializer.data['id'], file_name=file_obj._name, user_id=serializer.data['id'],url=picURL,upload_date=date.today())
        pic.save()
        Picserializer = ImageSerializer(pic)
        data={
            'id':Picserializer.data['id'],
            'file_name': Picserializer.data['file_name'],
            'url': Picserializer.data['url'],
            'upload_date': Picserializer.data['upload_date'],
            'user_id': Picserializer.data['user_id'],
        }
        return Response(data, status=status.HTTP_201_CREATED)


    def get(self,request,format=None):

        counter = statsd.Counter('APICounter')
        counter.increment('GetPictureCall')
        counter.increment('TotalCall')

        user = request.user
        serializer = MyUserSerializer(user)

        if not serializer.data['is_valid'] :
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        if UserPicture.objects.filter(user_id=serializer.data['id']).count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        pic = UserPicture.objects.get(user_id=serializer.data['id'])
        Picserializer = ImageSerializer(pic)
        data={
            'id':Picserializer.data['id'],
            'file_name': Picserializer.data['file_name'],
            'url': Picserializer.data['url'],
            'upload_date': Picserializer.data['upload_date'],
            'user_id': Picserializer.data['user_id'],
        }
        return Response(data, status=status.HTTP_200_OK)

    def delete(self,request,format=None):

        counter = statsd.Counter('APICounter')
        counter.increment('DeletePictureCall')
        counter.increment('TotalCall')

        user = request.user
        serializer = MyUserSerializer(user)
        
        if not serializer.data['is_valid'] :
            return Response(status=status.HTTP_403_FORBIDDEN)

        if UserPicture.objects.filter(user_id=serializer.data['id']).count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        pic = UserPicture.objects.get(user_id=serializer.data['id'])
        Picserializer = ImageSerializer(pic)
        s3 = boto3.client('s3',region_name='us-east-1')
            # aws_access_key_id='AKIAZAJCF6G3BKJGRSCK',
            # aws_secret_access_key='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'
            # )
        bucketname=os.environ['S3_Bucket_Name']
        #bucketname=usedforcsye6225zhenluodeveloptest'
        folder = str(serializer.data['id'])+'/'
        response = s3.delete_object(
            Bucket=bucketname,
            Key=folder+Picserializer.data['file_name']
        )
        
        pic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

