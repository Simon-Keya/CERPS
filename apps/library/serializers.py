from rest_framework import serializers
from django.utils import timezone
from .models import Book, LibraryMember, BorrowRecord, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BookSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'publisher', 'category', 'year_published', 'copies_total', 'copies_available']

    def validate_copies_available(self, value):
        # The key fix: check if an instance exists before validating against its properties.
        # This prevents the AttributeError during object creation (POST requests).
        if self.instance and value > self.instance.copies_total:
            raise serializers.ValidationError("Copies available cannot be greater than total copies.")
        return value

class LibraryMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.login_id', read_only=True)

    class Meta:
        model = LibraryMember
        fields = ['id', 'user_id', 'joined_date', 'membership_active']

class BorrowRecordSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(queryset=LibraryMember.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    
    member_id = serializers.CharField(source='member.user.login_id', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'member', 'book', 'member_id', 'book_title', 'borrowed_on', 'due_date', 'returned_on', 'is_overdue']

    def validate(self, data):
        if not self.instance:
            book = data['book']
            if book.copies_available < 1:
                raise serializers.ValidationError(f"No copies of '{book.title}' available to borrow.")
        return data

    def create(self, validated_data):
        book = validated_data['book']
        book.copies_available -= 1
        book.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        returned_on = validated_data.get('returned_on', None)
        if returned_on and not instance.returned_on:
            instance.book.copies_available += 1
            instance.book.save()
            instance.returned_on = timezone.now()
            instance.save()
            return instance
        return super().update(instance, validated_data)

class BorrowReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = ['returned_on']
        read_only_fields = ['returned_on']