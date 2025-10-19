from django.contrib import admin
from .models import Quiz, Question, Choice, GuestQuizAttempt, StudentQuizAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4  # Jumlah form kosong yang ditampilkan
    fields = ('choice_text', 'is_correct')

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('question_text', 'score')
    show_change_link = True  # Menampilkan link untuk edit detail

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz_pin', 'is_started', 'is_lobby', 'if_finished', 'visibility', 'created_at')
    list_filter = ('is_started', 'is_lobby', 'if_finished', 'visibility', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'quiz_pin')
    filter_horizontal = ('lecturer_team',)  # Widget untuk ManyToMany field
    
    fieldsets = (
        ('Quiz Information', {
            'fields': ('title', 'description', 'lecturer_team')
        }),
        ('Settings', {
            'fields': ('visibility',)
        }),
        ('Status', {
            'fields': ('quiz_pin', 'is_started', 'is_lobby', 'if_finished'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('lecturer_team', 'questions')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'quiz', 'score', 'choice_count', 'created_at')
    list_filter = ('quiz', 'score', 'created_at')
    search_fields = ('question_text', 'quiz__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Question Information', {
            'fields': ('quiz', 'question_text', 'score')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ChoiceInline]
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = "Question"
    
    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = "Choices"

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text_short', 'question_short', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'question__quiz', 'created_at')
    search_fields = ('choice_text', 'question__question_text', 'question__quiz__title')
    readonly_fields = ('created_at', 'updated_at')
    
    def choice_text_short(self, obj):
        return obj.choice_text[:30] + "..." if len(obj.choice_text) > 30 else obj.choice_text
    choice_text_short.short_description = "Choice"
    
    def question_short(self, obj):
        return obj.question.question_text[:30] + "..." if len(obj.question.question_text) > 30 else obj.question.question_text
    question_short.short_description = "Question"

@admin.register(GuestQuizAttempt)
class GuestQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'quiz', 'score', 'completed_at', 'created_at')
    list_filter = ('quiz', 'completed_at', 'created_at')
    search_fields = ('guest_name', 'quiz__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Guest Information', {
            'fields': ('guest_name', 'quiz')
        }),
        ('Results', {
            'fields': ('score', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')

@admin.register(StudentQuizAnswer)
class StudentQuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'question_short', 'quiz_title', 'selected_choices_count', 'created_at')
    list_filter = ('question__quiz', 'student', 'created_at')
    search_fields = ('student__user__username', 'question__question_text', 'question__quiz__title')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('selected_choices',)
    
    fieldsets = (
        ('Answer Information', {
            'fields': ('student', 'question', 'selected_choices')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def student_name(self, obj):
        return obj.student.user.username if obj.student else "Guest"
    student_name.short_description = "Student"
    
    def question_short(self, obj):
        if obj.question:
            return obj.question.question_text[:30] + "..." if len(obj.question.question_text) > 30 else obj.question.question_text
        return "No Question"
    question_short.short_description = "Question"
    
    def quiz_title(self, obj):
        return obj.question.quiz.title if obj.question and obj.question.quiz else "No Quiz"
    quiz_title.short_description = "Quiz"
    
    def selected_choices_count(self, obj):
        return obj.selected_choices.count()
    selected_choices_count.short_description = "Choices Selected"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'question__quiz').prefetch_related('selected_choices')
