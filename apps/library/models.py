from django.db import models
from django.utils import timezone
from django.conf import settings


class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    year_published = models.PositiveIntegerField(null=True, blank=True)
    copies_total = models.PositiveIntegerField(default=1)
    copies_available = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class LibraryMember(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_date = models.DateField(default=timezone.now)
    membership_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Library Member"
        verbose_name_plural = "Library Members"

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
     ordering = ['-borrowed_on']
     verbose_name = "Borrow Record"
     verbose_name_plural = "Borrow Records"

    @property
    def is_overdue(self):
        return self.returned_on is None and timezone.now() > self.due_date

    def __str__(self):
        return f"{self.member.user.login_id} borrowed {self.book.title}"
