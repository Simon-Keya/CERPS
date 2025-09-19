from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Book, LibraryMember, BorrowRecord
from .serializers import BookSerializer, LibraryMemberSerializer, BorrowRecordSerializer
from .permissions import IsLibraryStaffOrReadOnly, IsLibraryStaff

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibraryStaffOrReadOnly]

class LibraryMemberViewSet(viewsets.ModelViewSet):
    queryset = LibraryMember.objects.all()
    serializer_class = LibraryMemberSerializer
    permission_classes = [IsLibraryStaff]

class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsLibraryStaff]

    def perform_create(self, serializer):
        serializer.save(borrowed_on=timezone.now(), due_date=timezone.now() + timezone.timedelta(days=14))

    @action(detail=True, methods=['post'], url_path='return-book')
    def return_book(self, request, pk=None):
        borrow_record = self.get_object()
        if borrow_record.returned_on:
            return Response({"detail": "Book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)
        
        borrow_record.returned_on = timezone.now()
        borrow_record.book.copies_available += 1
        borrow_record.book.save()
        borrow_record.save()
        
        serializer = self.get_serializer(borrow_record)
        return Response(serializer.data)