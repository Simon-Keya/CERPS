from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import College, Department
from .serializers import CollegeSerializer, DepartmentSerializer
from .permissions import IsAdminOrReadOnly

class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAdminOrReadOnly]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=['get'])
    def names(self, request):
        """Return list of department names"""
        names = Department.objects.values_list('name', flat=True)
        return Response(names)
