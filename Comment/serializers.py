from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from Comment.models import Comment
from AuthUser.models import User

class CommentSerializer(ModelSerializer):
	username = serializers.CharField(source='commenter.username')
	class Meta:
		model = Comment
		fields = [
			'id',
			'comment_text',
			'username',
			'created_at'
			]
		read_only_fields = ['id', 'created_at']