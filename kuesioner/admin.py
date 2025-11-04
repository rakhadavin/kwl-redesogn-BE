from django.contrib import admin
from .models import (
	Kuesioner,
	Question,
	Choice,
	GuestQuizAttempt,
	GuestQuizAnswer,
	KuesionerSession,
)


class ChoiceInline(admin.TabularInline):
	model = Choice
	extra = 0
	fields = ("choice_text", "is_correct")


class QuestionInline(admin.TabularInline):
	model = Question
	extra = 0
	fields = ("number", "question_text", "time_limit", "score")


@admin.register(Kuesioner)
class KuesionerAdmin(admin.ModelAdmin):
	list_display = (
		"title",
		"question_type",
		"visibility",
		"pin",
		"is_lobby",
		"is_started",
		"if_finished",
		"created_at",
	)
	search_fields = ("title", "description", "pin")
	list_filter = ("question_type", "visibility", "is_lobby", "is_started", "if_finished")
	readonly_fields = ("created_at", "updated_at")
	inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ("short_text", "kuesioner", "number", "time_limit", "score")
	search_fields = ("question_text",)
	list_filter = ("kuesioner",)
	inlines = [ChoiceInline]

	def short_text(self, obj):
		return (obj.question_text[:75] + "...") if len(obj.question_text) > 75 else obj.question_text
	short_text.short_description = "Question"


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
	list_display = ("choice_text", "question", "is_correct")
	search_fields = ("choice_text",)
	list_filter = ("is_correct", "question")


@admin.register(GuestQuizAttempt)
class GuestQuizAttemptAdmin(admin.ModelAdmin):
	list_display = ("guest_name", "kuesioner", "session", "score", "created_at", "completed_at")
	search_fields = ("guest_name",)
	list_filter = ("kuesioner", "session")
	readonly_fields = ("created_at", "updated_at")


@admin.register(GuestQuizAnswer)
class GuestQuizAnswerAdmin(admin.ModelAdmin):
	list_display = ("guest", "question", "text_answer", "selected_choices_list")
	search_fields = ("guest__guest_name", "question__question_text")
	list_filter = ("question",)

	def selected_choices_list(self, obj):
		return ", ".join([c.choice_text for c in obj.selected_choices.all()])
	selected_choices_list.short_description = "Selected Choices"


@admin.register(KuesionerSession)
class KuesionerSessionAdmin(admin.ModelAdmin):
	list_display = (
		"kuesioner",
		"session_number",
		"started_by",
		"started_at",
		"finished_at",
		"total_participants",
		"is_active",
	)
	search_fields = ("kuesioner__title",)
	list_filter = ("is_active",)
	readonly_fields = ("started_at",)

