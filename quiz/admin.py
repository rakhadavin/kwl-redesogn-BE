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

class StudentQuizAnswerInline(admin.TabularInline):
    model = StudentQuizAnswer
    extra = 0
    fields = ('question', 'selected_choices_display', 'is_correct_display')
    readonly_fields = ('question', 'selected_choices_display', 'is_correct_display')
    
    def selected_choices_display(self, obj):
        choices = obj.selected_choices.all()
        return ", ".join([choice.choice_text[:20] for choice in choices]) if choices else "No answer"
    selected_choices_display.short_description = "Selected Choices"
    
    def is_correct_display(self, obj):
        selected_choices = obj.selected_choices.all()
        if not selected_choices:
            return "❌ No Answer"
        
        correct_choices = obj.question.choices.filter(is_correct=True)
        selected_correct = selected_choices.filter(is_correct=True)
        
        if selected_correct.count() == correct_choices.count() and selected_choices.count() == correct_choices.count():
            return "✅ Correct"
        else:
            return "❌ Incorrect"
    is_correct_display.short_description = "Result"

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz_pin', 'participants_count', 'questions_count', 'is_started', 'is_lobby', 'if_finished', 'visibility', 'created_at')
    list_filter = ('is_started', 'is_lobby', 'if_finished', 'visibility', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'quiz_pin')
    filter_horizontal = ('lecturer_team',)  # Widget untuk ManyToMany field
    actions = ['open_lobby', 'start_quiz', 'finish_quiz', 'reset_quiz']
    
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
    
    def participants_count(self, obj):
        return obj.guest_attempts.count()
    participants_count.short_description = "Participants"
    
    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = "Questions"
    
    def open_lobby(self, request, queryset):
        updated = queryset.update(is_lobby=True, is_started=False, if_finished=False)
        self.message_user(request, f'{updated} quiz(es) lobby opened.')
    open_lobby.short_description = "Open lobby for selected quizzes"
    
    def start_quiz(self, request, queryset):
        updated = queryset.update(is_started=True, is_lobby=False)
        self.message_user(request, f'{updated} quiz(es) started.')
    start_quiz.short_description = "Start selected quizzes"
    
    def finish_quiz(self, request, queryset):
        updated = queryset.update(if_finished=True, is_started=False, is_lobby=False)
        self.message_user(request, f'{updated} quiz(es) finished.')
    finish_quiz.short_description = "Finish selected quizzes"
    
    def reset_quiz(self, request, queryset):
        updated = queryset.update(is_started=False, is_lobby=False, if_finished=False)
        self.message_user(request, f'{updated} quiz(es) reset.')
    reset_quiz.short_description = "Reset selected quizzes"
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('lecturer_team', 'questions', 'guest_attempts')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'quiz', 'score', 'choice_count', 'correct_choice_count', 'answer_count', 'created_at')
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
    choice_count.short_description = "Total Choices"
    
    def correct_choice_count(self, obj):
        return obj.choices.filter(is_correct=True).count()
    correct_choice_count.short_description = "Correct Choices"
    
    def answer_count(self, obj):
        return StudentQuizAnswer.objects.filter(question=obj).count()
    answer_count.short_description = "Answers Given"

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
    list_display = ('guest_name_display', 'quiz', 'score', 'answers_count', 'completed_at', 'created_at')
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
    
    inlines = [StudentQuizAnswerInline]
    
    def guest_name_display(self, obj):
        return obj.guest_name or "Anonymous Guest"
    guest_name_display.short_description = "Guest Name"
    
    def answers_count(self, obj):
        return obj.answers.count()
    answers_count.short_description = "Answers"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz').prefetch_related('answers')

@admin.register(StudentQuizAnswer)
class StudentQuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'question_short', 'quiz_title', 'selected_choices_count', 'created_at')
    list_filter = ('question__quiz', 'student', 'created_at')
    search_fields = ('student__guest_name', 'question__question_text', 'question__quiz__title')
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
        return obj.student.guest_name if obj.student and obj.student.guest_name else "Anonymous Guest"
    student_name.short_description = "Student/Guest"
    
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
        return super().get_queryset(request).select_related('student', 'question__quiz').prefetch_related('selected_choices')
