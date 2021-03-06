from rest_framework.views import APIView
from .models import Classroom
from .serializers import ClassroomSerializer
from AuthUser.serializers import UserSerializer
from AuthUser.models import User
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status	

class ClassroomView(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		'''To get Classrooms for students, moderators, faculty.
		return classrooms where the user enrolled as faculty, moderator and student'''

		classroom = Classroom.objects.filter(creator__username=request.user.username)
		classroom_moderator = Classroom.objects.filter(moderators=request.user, is_active=True)
		classroom_student = Classroom.objects.filter(students=request.user, is_active=True)
		serializer = ClassroomSerializer(classroom, many=True)
		serializer_student = ClassroomSerializer(classroom_student, many=True)
		serializer_moderator = ClassroomSerializer(classroom_moderator, many=True)
		return Response({
			"faculty":serializer.data,
			"moderator":serializer_moderator.data,
			"student":serializer_student.data
			})

	def post(self, request, format=None):
		''' To create Classroom.
		Takes classroom_name and discription
		returns the new created classroom'''

		try:
			classroom_name = request.data.get('name')
			if request.user.is_faculty:
				classroom = Classroom()
				classroom.name = classroom_name
				classroom.creator = request.user
				classroom.description = request.data.get('description')
				classroom.save()
				serialized_classroom = ClassroomSerializer(classroom, many=False)
				return Response(serialized_classroom.data)
			else:
				return Response({
					"error": "You aren't authorized to make a classroom."
					}, status=status.HTTP_400_BAD_REQUEST)	
		except Exception as e:
			return Response({
				"error": "Something went wrong."
				}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None):
		'''To edit Classroom Object.
		Takes classroom_id, name and description.
		returns the edited classroom.'''

		classroom_id = request.data.get('id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			classroom_name = request.data.get('name')
			description = request.data.get('description')
			if(classroom.creator.username==request.user.username):
				classroom.name=classroom_name
				classroom.description = description
				classroom.save()
				classroom_serializer=ClassroomSerializer(classroom, many=False).data
				return Response(classroom_serializer)
			return Response({
					"errors": [
						"You can't update this classroom."
					]
				}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, format=None):
		'''To delete Classroom Object.
		Takes classroom_id.
		returns successful message'''

		classroom_id = request.data.get('classroom_id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username:
				if classroom.is_active == True:
					classroom.is_active = False
				else:
					classroom.is_active = True
				classroom.save()
				return Response({
					"success": "Classroom successfully deleted."
					}, status=status.HTTP_200_OK)
			return Response({
				"error": "You are not authorized to delete this classroom."
				}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)


class JoinClassroom(APIView):
	permission_classes = (IsAuthenticated, )

	def post(self, request, format=None):
		'''To join classroom through a unique code.
		Takes the unique code as joinCode
		returns the classroom object'''

		classroom_code = request.data.get('joinCode')
		try:
			classroom = Classroom.objects.get(code=classroom_code)
			classroom.students.add(request.user)
			classroom.save()
			serializer = ClassroomSerializer(classroom, many=False)
			return Response(serializer.data)
		except Exception as e:
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)


class ClassroomStudentView(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		'''To get students in a classroom.
		Takes the classroom_id
		return the list of student objects'''
		classroom_id = request.GET.get('id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username or request.user in classroom.moderators.all() or request.user in classroom.students.all():
				students = classroom.students.all()
				serialized_students = UserSerializer(students, many=True)
				return Response(serialized_students.data)
			else:
				return Response({
					"error": "You are not authorized to access this data."
					}, status=status.HTTP_403_FORBIDDEN)
		except Exception as e:
			return Response({
				"error": "Query does not exists."
				}, status=status.HTTP_403_FORBIDDEN)

	def post(self, request, format=None):
		'''To add students in a classroom by the faculty.
		Takes the classroom_id, students(list)
		return the Classroomobject with list of student objects in that classroom'''
		classroom_id = request.data.get('id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username:
				student_ids = request.data.get('students')
				student_users = [User.objects.get(username=student_id) for student_id in student_ids]
				classroom.students.add(*student_users)
				classroom.save()
				serialized_classroom = ClassroomSerializer(classroom, many=False).data
				serialized_students = UserSerializer(classroom.students.all(), many=True).data
				serialized_classroom['students'] = serialized_students
				return Response(serialized_classroom)
			else:
				return Response({
					"error": "You are not authorized to add students to this classroom."
					}, status=status.HTTP_403_FORBIDDEN)
		except Exception as e:
			return Response({
				"error": "Query does not exists."
				}, status=status.HTTP_403_FORBIDDEN)

	def put(self, request, format=None):
		'''To remove students in a classroom by the faculty.
		Takes the classroom_id, students_to_remove(list)
		return the Classroomobject with list of student objects in that classroom'''
		classroom_id = request.data.get('classroom_id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username:
				student_ids = request.data.get('students_to_remove')
				student_users = [User.objects.get(username=student_id) for student_id in student_ids]
				classroom.students.remove(*student_users)
				classroom.save()
				serialized_classroom = ClassroomSerializer(classroom, many=False).data	
				serialized_students = UserSerializer(classroom.students.all(), many=True).data
				serialized_classroom['students'] = serialized_students
				return Response(serialized_classroom)
			return Response({
					"errors": [
						"You can't remove students"
					]
				}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)


class ClassroomModeratorView(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		'''To get moderators in a classroom.
		Takes the classroom_id
		return the list of moderator objects'''
		classroom_id = request.GET.get('id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username or request.user in classroom.moderators.all() or request.user in classroom.students.all():
				moderators = classroom.moderators.all()
				serialized_moderators = UserSerializer(moderators, many=True)
				return Response(serialized_moderators.data)
			else:
				return Response({
					"error": "You are not authorized to access this data."
					}, status=status.HTTP_403_FORBIDDEN)
		except Exception as e:
			return Response({
				"error": "Classroom query does not exists."
				}, status=status.HTTP_403_FORBIDDEN)

	def post(self, request, format=None):
		'''To add moderators in a classroom by the faculty.
		Takes the classroom_id, moderators(list)
		return the Classroomobject with list of student objects in that classroom'''
		classroom_id = request.data.get('classroom_id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username:
				moderator_ids = request.data.get('moderators')
				moderator_users = [User.objects.get(username=moderator_id) for moderator_id in moderator_ids]
				classroom.moderators.add(*moderator_users)
				classroom.save()
				serialized_classroom = ClassroomSerializer(classroom, many=False).data
				serialized_moderators = UserSerializer(classroom.moderators.all(), many=True).data
				serialized_classroom['moderators'] = serialized_moderators
				return Response(serialized_classroom)
			else:
				return Response({
					"error": "You are not authorized to add moderators to this classroom."
					}, status=status.HTTP_403_FORBIDDEN)
		except Exception as e:
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_403_FORBIDDEN)

	def put(self, request, format=None):
		'''To remove moderators in a classroom by the faculty.
		Takes the classroom_id, moderators(list)
		return the Classroomobject with list of student objects in that classroom'''
		classroom_id = request.data.get('classroom_id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username:
				moderator_ids = request.data.get('moderators_to_remove')
				moderator_users = [User.objects.get(username=moderator_id) for moderator_id in moderator_ids]
				classroom.moderators.remove(*moderator_users)
				classroom.save()
				serialized_classroom = ClassroomSerializer(classroom, many=False).data	
				serialized_students = UserSerializer(classroom.moderators.all(), many=True).data
				serialized_classroom['moderators'] = serialized_students
				return Response(serialized_classroom)
			return Response({
					"error": "You are not authorized to remove moderators."
				}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)







