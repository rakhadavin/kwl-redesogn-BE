from rest_framework.permissions import BasePermission
from authentication.models import Lecturer, Student

class IsStudent(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "student")
    
class isLecturer(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "lecturer")


class isLecturerInCourse(BasePermission):
    """
    Allows access only to lecturer assigned to the course only.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "lecturer")
    
    def has_object_permission(self, request, view, obj):
        lecturer = Lecturer.objects.get(user_id=request.user.id)
        if lecturer in obj.lecturer_team.all():
            return True
        else:
            return False
        
class isEnrolledInCourse(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.role == "student" or request.user.role == "lecturer"))
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == "lecturer":
            lecturer = Lecturer.objects.get(user_id=request.user.id)
            if lecturer in obj.lecturer_team.all():
                return True
            else:
                return False
        else:
            student = Student.objects.get(user_id=request.user.id)
            if student in obj.students.all():
                return True
            else:
                return False
        
# class isLecturerInKnowCourse(BasePermission):
#     """
#     Allows access only to authenticated users.
#     """
#     def has_object_permission(self, request, view, obj):
#         print("dfd")
#         lecturer = Lecturer.objects.get(user_id=request.user.id)
#         if lecturer in obj.know.topic.course.lecturer_team.all():
#             print("HAH KOK TRUE")
#             return True
#         else:
#             return False
        
# class isLecturerInTopic(BasePermission):
#     """
#     Allows access only to authenticated users.
#     """

#     def has_permission(self, request, view):
#         return bool(request.user and request.user.role == "lecturer")
    
#     def has_object_permission(self, request, view, obj):
#         lecturer = Lecturer.objects.get(user_id=request.user.id)
#         if lecturer in obj.course.lecturer_team.all():
#             return True
#         else:
#             return 
        
