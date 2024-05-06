from rest_framework.permissions import BasePermission

from authentication.models import Lecturer

from authentication.models import Lecturer
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


# class isLecturerInCourse(BasePermission):
#     """
#     Allows access only to authenticated users.
#     """

#     def has_permission(self, request, view):
#         return bool(request.user and request.user.role == "lecturer")
    
#     def has_object_permission(self, request, view, obj):
#         lecturer = Lecturer.objects.get(user_id=request.user.id)
#         if lecturer in obj.lecturer_team.all():
#             return True
#         else:
#             return False
        
# class isLecturerInTopic(BasePermission):
#     """
#     Allows access only to authenticated users.
#     """

#     def has_permission(self, request, view):
#         return bool(request.user and request.user.role == "lecturer")
    
    def has_object_permission(self, request, view, obj):
        lecturer = Lecturer.objects.get(user_id=request.user.id)
        if lecturer in obj.course.lecturer_team.all():
            return True
        else:
            return 
        
