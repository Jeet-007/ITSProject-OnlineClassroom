from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import User

class UserSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'email',
			'mobile_no',
			'password',
			]
		extra_kwargs = {
			'password': {'write_only':True}
		}
		
	def create(self, validated_data):
		username = validated_data.pop('username')
		first_name = validated_data.pop('first_name')
		last_name = validated_data.pop('last_name')
		email = validated_data.pop('email')
		mobile_no = validated_data.pop('mobile_no')

		user = User()
		user.username = username
		user.first_name = first_name
		user.last_name = last_name
		user.email = email
		user.mobile_no = mobile_no
		user.save()

		return(user)