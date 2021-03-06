import logging

from api.authentication import models, serializers
from api.utils.views import (CustomAuthentication, get_user_id_from_token,
                             response)
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views, viewsets

logger = logging.getLogger(__name__)


# Create your views here.
class RegisterApiView(views.APIView):
    """Save new users"""
    serializer_class = serializers.UserSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response(data=serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(e)
            return response(message=e.__str__(), status=status.HTTP_400_BAD_REQUEST)


class UserVerify(views.APIView):
    @swagger_auto_schema(request_body=serializers.UserVerificationSerializer)
    def post(self, request, **kwargs):
        try:
            pk = get_user_id_from_token(kwargs.get('token'))
            user = get_object_or_404(models.User, pk=pk)
            # serializer = serializers.UserVerificationSerializer(user, data={"is_verified": True})
            serializer = serializers.UserVerificationSerializer(user)
            serializer.is_valid(raise_exception=True)
            # serializer.save()
            return response(data=serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.exception(e)
            return response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ViewSet):
    """User View class"""

    serializer = serializers.UserSerializer
    model = models.User
    authentication_classes = (CustomAuthentication, )

    def list(self, request):
        """List all users"""
        user = self.model.objects.filter(id=request.user.id)
        serializer = self.serializer(user, many=True)
        return response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Return a user with matching pk value"""
        try:
            serializer = self.serializer(request.user)
            return response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            return response(message=e.__str__(), status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializer)
    def update(self, request, pk=None):
        """Update the user's details with matching pk value"""
        try:
            if pk == request.user.id:
                serializer = self.serializer(request.user, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return response(data=serializer.data, status=status.HTTP_202_ACCEPTED)
            return response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.exception(e)
            return response(message=e.__str__(), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """Remove the user's details with matching pk value"""
        try:
            if pk == request.user.id:
                user = self.model.objects.get(pk=request.user.id)
                user.delete()
                return response(status=status.HTTP_204_NO_CONTENT)
            return response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.exception(e)
            return response(message=e.__str__(), status=status.HTTP_400_BAD_REQUEST)
