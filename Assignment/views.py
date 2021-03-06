from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from Assignment.models import Assignment, Submission
from Assignment.serializers import AssignmentSerializer, SubmissionSerializer
from Classroom.models import Classroom
from AuthUser.models import User
from Comment.serializers import CommentSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from Notifications.views import Notify, sendMail 
from Notifications.models import Notification
# Create your views here.

class AssignmentView(APIView):
	permission_classes = (IsAuthenticated, )
	
	def get(self, request, format=None):
		'''To get all assignments in a user enrolled classroom 
		Takes classroom_id
		Returns all assignments'''

		classroom_id = request.GET.get('classroom_id')
		try:
			classroom = Classroom.objects.get(id=classroom_id)
			if request.user.username == classroom.creator.username or request.user in classroom.moderators.all() or request.user in classroom.students.all():
				assignments = Assignment.objects.filter(classroom__id=classroom_id)
				serialized_assignments = AssignmentSerializer(assignments, many=True).data	
				return Response(serialized_assignments)
			else:
				return Response({
					"error": "You aren't enrolled in this classroom."
					}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, format=None):
		'''To upload a assignment in a classroom
		Takes Classroom_id, title, attachment, deadline and max_score
		Returns newly created assignment'''

		try:
			classroom = Classroom.objects.get(id=request.data.get('classroom_id'))
			if classroom.creator.username == request.user.username:
				serializer = AssignmentSerializer(data=request.data)
				uploader = request.user
				if serializer.is_valid():
					serializer.save(uploader=uploader, classroom=classroom)
					print(serializer.data)
					students = classroom.students.all()
					msg = "A new assignment is posted in "+ str(classroom.name) +"."
					Notify(sender=request.user, receiver=[student for student in students], type=Notification.AN, text=msg)
					sendMail(recipient=[student.email for student in students],subject="Aphlabet Notification",body= msg )
					return Response(serializer.data)
				else:
					return Response(serializer.errors)
			else:
				return Response({
					"error": "Only classroom owner can upload assignment."
					}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			print(e)
			return Response({
				"error": "Classroom query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)


class SubmissionView(APIView):
	permission_classes = (IsAuthenticated, )
	
	def get(self, request, format=None):
		'''To get all submissions of an assignment or a user uploaded submission
		Takes assignment_id
		Returns all submissions if user is student else returns all submissions of that assignment'''

		assignment_id = request.GET.get('assignment_id')
		try:
			assignment = Assignment.objects.get(id=assignment_id)
			if request.user.username == assignment.classroom.creator.username:
				submissions = Submission.objects.filter(assignment__id=assignment.id).order_by('score')
				serialized_submissions = SubmissionSerializer(submissions, many=True)
				return Response(serialized_submissions.data)
			else:
				submissions = Submission.objects.filter(assignment__id=assignment.id, submitter__username=request.user.username)
				serialized_submissions = SubmissionSerializer(submissions, many=True)
				return Response(serialized_submissions.data)
		except Exception as e:
			return Response({
				"error": "Assignment query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, format=None):
		'''To grade assignment submissions OR to change uploaded submission attachment
		Takes assignment_id, scores(is a list of objects(username and score)) or attachment
		Returns submissions with updated score if user is faculty otherwise returns submission with updated attachment'''

		assignment_id = request.data.get('assignment_id')
		students = request.data.get('scores')
		try:
			assignment = Assignment.objects.get(id=assignment_id)
			if request.user.is_faculty and request.user.username == assignment.uploader.username:
				submissionList = list()
				for student in students:
					submission = Submission.objects.get(submitter__username=student['username'], assignment__id=assignment_id)
					submission.score = int(student['score'])
					submission.save()
					submissionList.append(submission)
				serialized_submissions = SubmissionSerializer(submissionList, many=True)
				return Response(serialized_submissions.data)
			else:
				submission = Submission.objects.get(assignment_id=assignment.id, submitter__username=request.user.username)
				submission.attachment = request.data.get('attachment')
				submission.save()
				serializer = SubmissionSerializer(submission, many=False)
				return Response(serializer.data)
		except Exception as e:
			return Response({
				"error": "Assignment OR Submission query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)


	def post(self, request, format=None):
		'''To upload submission or update uploaded submission
		Takes assignment_id, attachment
		Returns newly uploaded or updated submission'''

		assignment_id = request.data.get('assignment_id')
		try:
			assignment = Assignment.objects.get(id=assignment_id)
			if request.user.username == assignment.classroom.creator.username or request.user in assignment.classroom.moderators.all() or request.user in assignment.classroom.students.all():
				try:
					submission = Submission.objects.get(submitter__username=request.user.username, assignment__id=assignment.id)
					submission.attachment = request.data.get('attachment')
					submission.save()
					serializer = SubmissionSerializer(submission, many=False)
					return Response(serializer.data)
				except:
					serializer = SubmissionSerializer(data=request.data)
					if serializer.is_valid():
						serializer.save(submitter=request.user, assignment=assignment)
						return Response(serializer.data)
					else:
						return Response(serializer.errors)
			else:
				return Response({
					"error": "You aren't enrolled in this classroom."
					}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			print(e)
			return Response({
				"error": "Assignment query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)


class AssignmentCommentView(APIView):
	permission_classes = (IsAuthenticated, )

	def get(self, request, format=None):
		'''To get all comments on an assignment
		Takes assignment_id
		Returns all comments with assignment'''

		assignment_id = request.GET.get('assignment_id')
		try:
			assignment = Assignment.objects.get(id=assignment_id)
			if request.user.username == assignment.classroom.creator.username or request.user in assignment.classroom.moderators.all() or request.user in assignment.classroom.students.all():
				allComments = assignment.comments.all()
				serialized_comments = CommentSerializer(allComments, many=True).data
				serialized_assignment = AssignmentSerializer(assignment, many=False).data
				serialized_assignment['comments'] = serialized_comments
				return Response(serialized_assignment)
			else:
				return Response({
					"error": "You aren't enrolled in this classroom."
					}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({
				"error": "Assignment query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, format=None):
		'''To post a comment on an assignment
		Takes assignment_id, comment_id(if replying a comment), content
		Returns assignment with comments'''
		
		assignment_id = request.data.get('assignment_id')
		try:
			assignment = Assignment.objects.get(id=assignment_id)
			if request.user.username == assignment.classroom.creator.username or request.user in assignment.classroom.moderators.all() or request.user in assignment.classroom.students.all():
				comment = Comment()
				if request.data.get('comment_id'):
					try:
						comment.parent = Comment.objects.get(id=request.data.get('comment_id'))
						comment.commenter = request.user
						comment.comment_text = request.data.get('content')
						comment.save()
					except Exception as e:
						return Response({
							"error": "Comment query doesn't exists."
							}, status=status.HTTP_400_BAD_REQUEST)
				else:
					comment.parent = None
					comment.commenter = request.user
					comment.comment_text = request.data.get('content')
					comment.save()
					assignment.comments.add(comment)
					assignment.save()
				allComments = assignment.comments.all()
				serialized_comments = CommentSerializer(allComments, many=True).data
				serialized_assignment = AssignmentSerializer(assignment, many=False).data
				serialized_assignment['comments'] = serialized_comments
				return Response(serialized_assignment)
			else:
				return Response({
					"error": "You aren't enrolled in this classroom."
					}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({
				"error": "Assignment query doesn't exists."
				}, status=status.HTTP_400_BAD_REQUEST)