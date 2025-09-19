from django.contrib import admin
from django.utils import timezone
from .models import Book, LibraryMember, BorrowRecord, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'author', 'copies_total', 'copies_available', 'category')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category', 'publisher', 'year_published')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'isbn', 'author', 'publisher', 'category', 'year_published')
        }),
        ('Availability', {
            'fields': ('copies_total', 'copies_available'),
            'description': 'Manage the total and available copies of the book.'
        }),
    )

@admin.register(LibraryMember)
class LibraryMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'joined_date', 'membership_active')
    search_fields = ('user__login_id', 'user__first_name', 'user__last_name')
    list_filter = ('membership_active', 'joined_date')
    actions = ['activate_members', 'deactivate_members']

    @admin.action(description='Mark selected members as active')
    def activate_members(self, request, queryset):
        updated_count = queryset.update(membership_active=True)
        self.message_user(request, f'{updated_count} members were successfully activated.')

    @admin.action(description='Mark selected members as inactive')
    def deactivate_members(self, request, queryset):
        updated_count = queryset.update(membership_active=False)
        self.message_user(request, f'{updated_count} members were successfully deactivated.')

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('member', 'book', 'borrowed_on', 'due_date', 'returned_on', 'is_overdue')
    list_filter = ('returned_on', 'due_date')
    search_fields = ('member__user__login_id', 'book__title', 'book__isbn')
    readonly_fields = ('is_overdue',)
    actions = ['mark_as_returned']
    
    def get_list_filter(self, request):
        # Dynamically add an "Overdue" filter
        return self.list_filter + ('is_overdue',)

    @admin.action(description='Mark selected books as returned')
    def mark_as_returned(self, request, queryset):
        returned_count = 0
        for record in queryset:
            if not record.returned_on:
                record.returned_on = timezone.now()
                record.book.copies_available += 1
                record.book.save()
                record.save()
                returned_count += 1
        self.message_user(request, f'{returned_count} borrow records were successfully marked as returned.')