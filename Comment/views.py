from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from Comment.models import Comment
from AuthUser.models import User
from Comment.serializers import CommentSerializer
# Create your views here.

class CommentView(APIView):

	def get(self, request, format=None):
		comments = Comment.objects.all()
		serializer = CommentSerializer(comments, many=True)

		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = CommentSerializer(data=request.data)
		if serializer.is_valid():
			user = User.objects.get(username=request.data.get('username'))
			serializer.save(commenter=user)
		return Response(serializer.data)