from rest_framework import serializers

from authentication.models import Student
from course.api_exceptions import TopicNotFoundException
from course.models import Topic
from .models import Learned, LearnedReflection, LearnedQuizOption, LearnedQuizQuestion, LearnedReflectionStudentAnswer
from django.db import transaction
from .api_exceptions import ExistingLearnedException, LearnedQuizNotFoundException, LearnedReflectionNotFoundException
option_choices = (("Opsi A", "Opsi A"), ("Opsi B", "Opsi B"), ("Opsi C", "Opsi C"), ("Opsi D", "Opsi D"))
learned_choices = (("reflection", "Reflection"), ("quiz", "Quiz"))


class LearnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Learned
        fields = ('id', 'topic', 'type' )
        
class LearnedQuizOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnedQuizOption
        fields = ('id', 'option_answer', 'isCorrect' )

class LearnedQuizQuestionSerializer(serializers.ModelSerializer):
    options = LearnedQuizOptionsSerializer(source='get_answers', many=True, read_only=True)
    class Meta:
        model = LearnedQuizQuestion
        fields = ('id', 'question', 'score', 'learned', 'options' )

class LearnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Learned
        fields = ('id', 'topic', 'type' )


class AddLearnedQuizQuestionSerializer(serializers.ModelSerializer):
    option_a = serializers.CharField(max_length=255, write_only=True)
    option_b = serializers.CharField(max_length=255, write_only=True)
    option_c = serializers.CharField(max_length=255, write_only=True)
    option_d = serializers.CharField(max_length=255, write_only=True)
    correct_option = serializers.ChoiceField(choices=option_choices, required=True, write_only=True)

    class Meta:
        model = LearnedQuizQuestion
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'question', 'correct_option', 'score', 'learned']


class BulkAddLearnedQuizSerializer(serializers.Serializer):
    topic = serializers.IntegerField(write_only=True)
    type = serializers.ChoiceField(choices=learned_choices, required=True, write_only=True)
    questions = AddLearnedQuizQuestionSerializer(many=True, write_only=True)

    def create(self, validated_data):
        topic = get_topic(validated_data['topic'])
        with transaction.atomic():
            learned, created = Learned.objects.get_or_create(topic=topic)
            if not created:
                raise ExistingLearnedException("Learned already exists")
            learned.type = validated_data['type']
            learned.save()
            questions = validated_data.pop('questions')
            for question in questions:
                question['learned'] = learned
                options_data = [
                {'option_answer': question.pop('option_a'), 'isCorrect': question['correct_option'] == 'Opsi A', 'alias': 'option_a'},
                {'option_answer': question.pop('option_b'), 'isCorrect': question['correct_option'] == 'Opsi B', 'alias': 'option_b'},
                {'option_answer': question.pop('option_c'), 'isCorrect': question['correct_option'] == 'Opsi C', 'alias': 'option_c'},
                {'option_answer': question.pop('option_d'), 'isCorrect': question['correct_option'] == 'Opsi D', 'alias': 'option_d'}
                ]
                question.pop('correct_option')      
                learned_quiz = LearnedQuizQuestion.objects.create(**question)
                options = [LearnedQuizOption(learned_quiz=learned_quiz, **option_data) for option_data in options_data]
                LearnedQuizOption.objects.bulk_create(options)

        return learned

class EditLearnedQuizQuestionSerializer(serializers.Serializer):
    option_a = serializers.CharField(max_length=255, write_only=True)
    option_b = serializers.CharField(max_length=255, write_only=True)
    option_c = serializers.CharField(max_length=255, write_only=True)
    option_d = serializers.CharField(max_length=255, write_only=True)
    question = serializers.CharField(max_length=255)
    correct_option = serializers.ChoiceField(choices=option_choices, required=False, write_only=True)
    score = serializers.IntegerField(required=False)
    id =  serializers.IntegerField(required=True, write_only=True)

class BulkEditQuizSerializer(serializers.Serializer):
    questions = EditLearnedQuizQuestionSerializer(many=True, write_only=True)


class AddLearnedEssaySerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=learned_choices, write_only=True)
    score = serializers.IntegerField()
    topic = serializers.IntegerField(write_only=True)

    class Meta:
        model = LearnedReflection
        fields = ['question', 'type', 'score', 'topic', 'id']
    
    def create(self, validated_data):
        with transaction.atomic():
            topic = get_topic(validated_data['topic'])

            learned, created = Learned.objects.get_or_create(topic=topic)
            if not created:
                raise ExistingLearnedException("Learned already exists")
            learned.type = validated_data['type']
            learned.save()
            
            learned_essay = LearnedReflection.objects.create(learned=learned, question=validated_data['question'], score=validated_data['score'])
            
        return learned_essay
    
class EditLearnedEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255)
    score = serializers.IntegerField()
    
    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        instance.save()
        return instance
    
class LearnedReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnedReflection
        fields = ('id', 'question', 'score', 'learned' )

class LearnedReflectionAnswerSerializer(serializers.Serializer):
    reflection = serializers.CharField(max_length=255)
    topic = serializers.IntegerField(write_only=True)

class LearnedQuizAnswerSerializer(serializers.Serializer):
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