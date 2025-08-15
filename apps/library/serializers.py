from rest_framework import serializers
from .models import Book, LibraryMember, BorrowRecord

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class LibraryMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.login_id', read_only=True)

    class Meta:
        model = LibraryMember
        fields = ['id', 'user_id', 'joined_date', 'membership_active']

class BorrowRecordSerializer(serializers.ModelSerializer):
    member_id = serializers.CharField(source='member.user.login_id', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'member_id', 'book_title', 'borrowed_on', 'due_date', 'returned_on', 'is_overdue']

    def create(self, validated_data):
        book = validated_data['book']
        if book.copies_available < 1:
            raise serializers.ValidationError(f"No copies of '{book.title}' available to borrow.")
        book.copies_available -= 1
        book.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        returned_on = validated_data.get('returned_on', instance.returned_on)
        if returned_on and instance.returned_on is None:
            instance.book.copies_available += 1
            instance.book.save()
        return super().update(instance, validated_data)
