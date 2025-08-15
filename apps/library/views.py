from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Book, LibraryMember, BorrowRecord
from .serializers import BookSerializer, LibraryMemberSerializer, BorrowRecordSerializer
from .permissions import IsLibraryStaffOrReadOnly
from rest_framework.permissions import IsAuthenticated

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibraryStaffOrReadOnly]

class LibraryMemberViewSet(viewsets.ModelViewSet):
    queryset = LibraryMember.objects.all()
    serializer_class = LibraryMemberSerializer
    permission_classes = [IsAuthenticated]

class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsLibraryStaffOrReadOnly]

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        borrow_record = self.get_object()
        if borrow_record.returned_on:
            return Response({"detail": "Book already returned."}, status=status.HTTP_400_BAD_REQUEST)
        borrow_record.returned_on = timezone.now()
        borrow_record.save()
        return Response(BorrowRecordSerializer(borrow_record).data)
