from rest_framework import serializers

from authentication.api_exceptions import StudentNotFoundException
from authentication.models import Student
from course.models import Topic, RewardStudentPoint
from .models import Know, KnowQuizQuestion, KnowQuizOption, KnowReflection, KnowReflectionStudentAnswer
from .api_exceptions import ExistingKnowException, KnowQuizQuestionNotFoundException
from course.api_exceptions import TopicNotFoundException
from django.db import transaction

option_choices = (("Opsi A", "Opsi A"), ("Opsi B", "Opsi B"), ("Opsi C", "Opsi C"), ("Opsi D", "Opsi D"))
know_choices = (("reflection", "Reflection"), ("quiz", "Quiz"))

class KnowQuizOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowQuizOption
        fields = ('id', 'option_answer', 'isCorrect') 
        
class KnowQuizQuestionSerializer(serializers.ModelSerializer):
    options = KnowQuizOptionsSerializer(source='get_answers', many=True, read_only=True)
    class Meta:
        model = KnowQuizQuestion
        fields = ('id', 'question', 'score', 'know', 'options' )

class KnowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Know
        fields = ('id', 'topic', 'type' )
    

class AddKnowQuizQuestionSerializer(serializers.ModelSerializer):
    option_a = serializers.CharField(max_length=255, write_only=True)
    option_b = serializers.CharField(max_length=255, write_only=True)
    option_c = serializers.CharField(max_length=255, write_only=True)
    option_d = serializers.CharField(max_length=255, write_only=True)
    correct_option = serializers.ChoiceField(choices=option_choices, required=True, write_only=True)
    
    
    class Meta:
        model = KnowQuizQuestion
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'question', 'correct_option', 'score', 'know']
    
    
class BulkAddQuizSerializer(serializers.Serializer):
    topic = serializers.IntegerField(write_only=True)
    type = serializers.ChoiceField(choices=know_choices, required=True, write_only=True)
    questions = AddKnowQuizQuestionSerializer(many=True, write_only=True)

    def create(self, validated_data):
        topic = get_topic(validated_data['topic'])
        with transaction.atomic():
            know, created = Know.objects.get_or_create(topic=topic)
            if not created:
                raise ExistingKnowException("Know already exists")
            know.type = validated_data['type']
            know.save()
            questions = validated_data.pop('questions')
            for question in questions:
                question['know'] = know
                options_data = [
                {'option_answer': question.pop('option_a'), 'isCorrect': question['correct_option'] == 'Opsi A', 'alias': 'option_a'},
                {'option_answer': question.pop('option_b'), 'isCorrect': question['correct_option'] == 'Opsi B', 'alias': 'option_b'},
                {'option_answer': question.pop('option_c'), 'isCorrect': question['correct_option'] == 'Opsi C', 'alias': 'option_c'},
                {'option_answer': question.pop('option_d'), 'isCorrect': question['correct_option'] == 'Opsi D', 'alias': 'option_d'}
                ]
                question.pop('correct_option')      
                know_quiz = KnowQuizQuestion.objects.create(**question)
                options = [KnowQuizOption(know_quiz=know_quiz, **option_data) for option_data in options_data]
                KnowQuizOption.objects.bulk_create(options)

            return know


class EditKnowQuizQuestionSerializer(serializers.ModelSerializer):
    option_a = serializers.CharField(max_length=255, write_only=True)
    option_b = serializers.CharField(max_length=255, write_only=True)
    option_c = serializers.CharField(max_length=255, write_only=True)
    option_d = serializers.CharField(max_length=255, write_only=True)
    id = serializers.IntegerField(write_only=True)
    correct_option = serializers.ChoiceField(choices=option_choices, write_only=True)
    score = serializers.IntegerField()

    class Meta:
        model = KnowQuizQuestion
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'question', 'correct_option', 'score', 'know','id']
    
    


    
class BulkEditQuizSerializer(serializers.Serializer):
    questions = EditKnowQuizQuestionSerializer(many=True, write_only=True)

    
class AddKnowEssaySerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=know_choices, write_only=True)
    score = serializers.IntegerField()
    topic = serializers.IntegerField(write_only=True)

    class Meta:
        model = KnowReflection
        fields = ('question', 'score', 'type', 'topic','id')

    def create(self, validated_data):
        with transaction.atomic():
            topic = get_topic(validated_data['topic'])

            know, created = Know.objects.get_or_create(topic=topic)
            if not created:
                raise ExistingKnowException("Know already exists")

            know.type = validated_data.pop('type')
            know.save()
            know_essay = KnowReflection.objects.create(know=know, question=validated_data['question'], score=validated_data['score'])
        
        return know_essay
    

class EditKnowEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255)
    score = serializers.IntegerField()

    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        instance.save()
        return instance
    
class KnowReflectionSerializer(serializers.ModelSerializer):
    know = KnowSerializer()
    class Meta:
        model = KnowReflection
        fields = ('id', 'question', 'score', 'know' )


class KnowReflectionAnswerSerializer(serializers.Serializer):
    reflection = serializers.CharField(max_length=255)
    topic = serializers.IntegerField()

class KnowQuizAnswerSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=serializers.IntegerField(required=True),
        required=True
    )
    topic = serializers.IntegerField(required=True)

def get_topic(topic_id):
    try:
        return Topic.objects.get(pk=topic_id)
    except Topic.DoesNotExist:
        raise TopicNotFoundException()