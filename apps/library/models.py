from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    year_published = models.PositiveIntegerField(null=True, blank=True)
    copies_total = models.PositiveIntegerField(default=1)
    copies_available = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} ({self.isbn})"

class LibraryMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_date = models.DateField(default=timezone.now)
    membership_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.login_id} - Library Member"

class BorrowRecord(models.Model):
    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrowed_on = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    returned_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('member', 'book', 'borrowed_on')

    @property
    def is_overdue(self):
        return self.returned_on is None and timezone.now() > self.due_date

    def __str__(self):
        return f"{self.member.user.login_id} borrowed {self.book.title}"
