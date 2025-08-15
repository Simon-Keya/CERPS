from django.contrib import admin
from .models import Book, LibraryMember, BorrowRecord

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'author', 'copies_total', 'copies_available')
    search_fields = ('title', 'author', 'isbn')

@admin.register(LibraryMember)
class LibraryMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'joined_date', 'membership_active')
    search_fields = ('user__login_id', 'user__first_name', 'user__last_name')

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'borrowed_on', 'due_date', 'returned_on', 'is_overdue')
    search_fields = ('member__user__login_id', 'book__title')
    readonly_fields = ('is_overdue',)
