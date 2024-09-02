from django.contrib import admin
from learning_platform.models import Course, Material, Test, AnswerOption, StudentAnswer
from .models import User, Subscription, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'city', 'is_active', 'is_staff')
    search_fields = ('email', 'phone')
    list_filter = ('is_active', 'is_staff', 'city', 'groups')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'city', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2'),
        }),
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'material', 'owner')
    search_fields = ('question', 'material', 'owner')
    list_filter = ('question', 'material', 'id', 'owner')


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'answer_text', 'is_correct', 'owner')
    search_fields = ('answer_text', 'is_correct', 'owner')
    list_filter = ('answer_text', 'is_correct', 'owner')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner')
    search_fields = ('is_subscribed', 'title')
    list_filter = ('title', 'id')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_subscribed')
    search_fields = ('user', 'course', 'is_subscribed')
    list_filter = ('user', 'course', 'is_subscribed')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'course')
    search_fields = ('title', 'course')
    list_filter = ('title', 'id')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_session', 'payment_status', 'pay_amount', 'user', 'pay_course')
    search_fields = ('id', 'pay_amount')
    list_filter = ('id', 'pay_amount')


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'test', 'is_correct', 'timestamp')
    search_fields = ('id', 'student', 'is_correct')
    list_filter = ('id', 'student', 'is_correct')













