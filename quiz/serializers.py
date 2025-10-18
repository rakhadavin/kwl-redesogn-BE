from rest_framework import serializers
from .models import Quiz, Question, Choice, GuestQuizAttempt


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'score', 'choices', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuizListSerializer(serializers.ModelSerializer):
    """
    Serializer untuk list quiz (tanpa questions detail)
    """
    questions_count = serializers.SerializerMethodField()
    lecturer_team = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'visibility', 'lecturer_team',
            'quiz_pin', 'is_started', 'is_lobby', 'if_finished', 
            'questions_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'quiz_pin', 'created_at', 'updated_at']
    
    def get_questions_count(self, obj):
        return obj.questions.count()
    
class QuizCreateSerializer(serializers.ModelSerializer):
    """
    Serializer untuk create quiz
    """
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'visibility']
    
    def create(self, validated_data):
        validated_data['is_started'] = False
        validated_data['if_finished'] = False
        return super().create(validated_data)
    
class QuizDetailSerializer(serializers.ModelSerializer):
    """
    Serializer untuk detail quiz (dengan questions)
    """
    questions = QuestionSerializer(many=True, read_only=True)
    lecturer_team = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'visibility', 'lecturer_team',
            'quiz_pin', 'is_started', 'is_lobby', 'if_finished', 
            'questions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'quiz_pin', 'created_at', 'updated_at']

class ChoiceWriteSerializer(serializers.Serializer):
    choice_text = serializers.CharField(max_length=500)
    is_correct = serializers.BooleanField()

class QuestionWriteSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    score = serializers.IntegerField()
    choices = ChoiceWriteSerializer(many=True)

class QuizUpdateSerializer(serializers.Serializer):
    questions = QuestionWriteSerializer(many=True)

    def update(self, instance, validated_data):
        questions_data = validated_data.get('questions', [])
        instance.questions.all().delete()
        
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            
            question = Question.objects.create(
                quiz=instance,
                question_text=question_data['question_text'],
                score=question_data['score']
            )
            
            for choice_data in choices_data:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_data['choice_text'],
                    is_correct=choice_data['is_correct']
                )
        return instance

class GuestQuizAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer untuk Guest Quiz Attempt
    """
    class Meta:
        model = GuestQuizAttempt
        fields = ['id', 'guest_name', 'quiz', 'score', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'score', 'completed_at', 'created_at', 'updated_at']

class GuestJoinQuizSerializer(serializers.Serializer):
    """
    Serializer untuk join quiz dengan nama langsung
    """
    guest_name = serializers.CharField(max_length=255, required=True)

class UpdateGuestNameSerializer(serializers.Serializer):
    """
    Serializer untuk update nama guest
    """
    guest_name = serializers.CharField(max_length=255)
