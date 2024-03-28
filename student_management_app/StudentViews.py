from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
import datetime
from .models import CustomUser, Staffs, Students, Courses, Subjects, Attendance, AttendanceReport, LeaveReportStudent, FeedBackStudent, StudentResult

def student_home(request):
	student_obj = Students.objects.get(admin=request.user.id)
	total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
	attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
	attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()
	course_obj = Courses.objects.get(id=student_obj.course_id.id)
	total_subjects = Subjects.objects.filter(course_id=course_obj).count()
	subject_name = []
	present_data = []
	absent_data = []
	subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
	for subject in subject_data:
		attendance = Attendance.objects.filter(subject_id=subject.id)
		attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
		subject_name.append(subject.subject_name)
		present_data.append(attendance_present_count)
		absent_data.append(attendance_absent_count)

		context = {
		"total_attendance": total_attendance,
		"attendance_present": attendance_present,
		"attendance_absent": attendance_absent,
		"total_subjects": total_subjects,
		"subject_name": subject_name,
		"present_data": present_data,
		"absent_data": absent_data
		}

		return render(request, "student_template/student_home_template.html", context)


def student_view_attendance(request):
	#Get the logged in student data
	student = Students.objects,get(admin=request.user.id)

	#Get enrolled course of logged in student
	course = student.course_id

	#Get subjects of the course
	subjects =  Subjects.objects.filter(course_id=course)
	context = {
	"subjects": subjects
	}
	return render(request, "student_template/student_view_attendance.html", context)


def student_view_attendance_post(request):
	if request.method != "POST":
		messages.error(request, "Invalid Method, POST method needed")
		return redirect('student_view_attendance')
	else:
		#Get all the POST data
		subject_id = request.POST.get('subject')
		start_date = request.POST.get('start_date')
		end_date = request.POST.get('end_date')

		#parsing the date data obtained into Python objects
		parsed_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
		parsed_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

		#Subject data for selected student
		subject_obj = Subjects.objects.get(id=subject_id)

		#Logged in userdata
		user_obj = CustomUser.objects.get(id=request.user.id)

		#Logged in Student data 
		stud_obj = Students.objects.get(admin=user_obj)

		#Now accessing the attendance data within the specified date range
		attendance = Attendance.objects.filter(attendance_date__range=(parsed_start_date, parsed_end_date), subject_id=subject_obj)

		attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

		context = {
		"subject_obj": subject_obj,
		"attendance_reports": attendance_reports
		}

		return render(request, "student_template/student_attendance_data.html",context)


def student_apply_leave(request):
	student_obj = Students.objects.filter(admin=request.user.id)
	leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
	context = {
	"leave_data": leave_data
	}

	return render(request, 'student_template/student_apply_leave.html')


def student_apply_leave_save(request):
	if request.method != 'POST':
		messages.error(request, "Invalid Method")
		return redirect('student_apply_leave')
	else:
		leave_date = request.POST.get('leave_date')
		leave_message = request.POST.get('leave_message')

		student_obj = Students.objects.get(admin=request.user.id)
		try:
			leave_report = LeaveReportStudent(student_id=student_obj, leave_date=leave_date, leave_message=leave_message, leave_status=0)
			leave_report.save()
			messages.success(request, "Applied for leave")
			return redirect('student_apply_leave')
		except:
			messages.error(request, "Failed to apply for leave")
			return redirect('student_apply_leave')


def student_feedback(request):
	student_obj = Students.objects.get(admin=request.user.id)
	feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
	context = {
	"feedback_data": feedback_data
	}
	return render(request, "student_template/student_feedback.html")


def student_feedback_save(request):
	if request.method != 'POST':
		messages.error(request, "Invalid Method")
		return redirect('student_feedback')
	else:
		feedback = request.POST.get('feedback_message')
		student_obj = Students.objects.get(admin=request.user.id)
		try:
			add_feedback = FeedBackStudent(student_id=student_obj, feedback=feedback, feedback_reply="")
			add_feedback.save()			
			messages.success(request, "Feedback sent..")
			return redirect('student_feedback')
		except:
			messages.error(request, "Failed to send feedback")
			return redirect('student_feedback')


def student_profile(request):
	user = CustomUser.objects.get(id=request.user.id)
	student = Students.objects.get(admin=user)

	context = {
	"student": student,
	"user": user
	}

	return render(request, 'student_template/student_profile.html')

def student_profile_update(request):
	if request.method != "POST":
		messages.error(request, "Invalid method")
		return redirect('student_profile')
	else:
		first_name = request.POST.get("first_name")
		last_name = request.POST.get("last_name")
		password = request.POST.get("password")
		address = request.POST.get("address")

		try:
			customuser = CustomUser.objects.get(id=request.user.id)
			customuser.first_name = first_name
			customuser.last_name = last_name
			if password != None and password != '':
				customuser.set_password(password)
			customuser.save()

			student = Students.objects.get(admin=customuser.id)
			student.address = address
			student.save()

			messages.success(request, "Profile has been updated successfully")
			return redirect('student_profile')
		except:
			messages.error(request, "Failed to update user profile")
			return redirect('student_profile')


def student_view_result(request):
	student = Students.objects.get(admin=request.user.id)
	student_result = StudentResult.objects.filter(student_id=student)
	context = {
	"student_result": student_result,
	}
	return render(request, "student_template/student_view_result.html")
