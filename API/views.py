from datetime import datetime
from API.models import MyUser
from API.serializers import MyUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.views import APIView

# Create your views here.

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
        data=UserCreate.is_valid_data(request.data.dict())
        if data is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_list = list(MyUser.objects.all())
        for _ in user_list:
            if _.get_username() == data['username']:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        user = MyUser(username=data['username'],first_name=data['first_name'],last_name=data['last_name'],email=data['username'])
        user.set_password(data['password'])
        user.save()
        serializer = MyUserSerializer(user)
        data={
            'id':serializer.data['id'],
            'username': serializer.data['email'],
            'first_name': serializer.data['first_name'],
            'last_name': serializer.data['last_name'],
            'account_created': serializer.data['account_created'],
            'account_updated': serializer.data['account_updated'],
            }
        return Response(data, status=status.HTTP_201_CREATED)
class UserDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
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
        user=request.user
        serializer = MyUserSerializer(user)
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
        user = request.user
        data=UserDetail.is_valid_data(request.data.dict())
        if data is not None:
            user.set_password(data['password'])
            user.first_name=data['first_name']
            user.last_name=data['last_name']
            user.account_updated=datetime.now()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
