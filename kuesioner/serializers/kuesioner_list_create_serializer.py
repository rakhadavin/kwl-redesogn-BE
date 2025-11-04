from rest_framework import serializers
from ..models import Kuesioner, Question, Choice, GuestQuizAttempt

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['title', 'description', 'visibility']
    
    def create(self, validated_data):
        validated_data['is_started'] = False
        validated_data['if_finished'] = False
        return super().create(validated_data)

class KuesionerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer untuk create kuesioner
    """
    question = QuestionSerializer(many=True, read_only=True)
    lecturer_team = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Kuesioner
        fields = [
            'id', 'title', 'description', 'question_type', 'visibility', 'lecturer_team',
            'pin', 'is_started', 'is_lobby', 'if_finished', 
            'questions_count', 'created_at', 'updated_at'
        ]