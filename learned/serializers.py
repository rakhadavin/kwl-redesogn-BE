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
    topic = serializers.IntegerField(write_only=True)
    type = serializers.ChoiceField(choices=learned_choices, required=True, write_only=True)

    class Meta:
        model = LearnedQuizQuestion
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'question', 'type', 'correct_option', 'score', 'topic', 'learned']
    
    def create(self, validated_data):
        topic_id = validated_data.pop('topic', None)

        topic = get_topic(topic_id)

        options_data = [
        {'option_answer': validated_data.pop('option_a'), 'isCorrect': validated_data['correct_option'] == 'Opsi A', 'alias': 'option_a'},
        {'option_answer': validated_data.pop('option_b'), 'isCorrect': validated_data['correct_option'] == 'Opsi B', 'alias': 'option_b'},
        {'option_answer': validated_data.pop('option_c'), 'isCorrect': validated_data['correct_option'] == 'Opsi C', 'alias': 'option_c'},
        {'option_answer': validated_data.pop('option_d'), 'isCorrect': validated_data['correct_option'] == 'Opsi D', 'alias': 'option_d'}
        ]

        validated_data.pop('correct_option')   

        with transaction.atomic():
            learned, created = Learned.objects.get_or_create(topic=topic)

            if not created and learned.type != validated_data['type']:
                raise ExistingLearnedException("Learned already exists")
            
            validated_data['learned'] = learned 
            learned.type = validated_data.pop('type')
            learned.save()
            
            learned_quiz = LearnedQuizQuestion.objects.create(**validated_data)
            options = [LearnedQuizOption(learned_quiz=learned_quiz, **option_data) for option_data in options_data]
            LearnedQuizOption.objects.bulk_create(options)
        return learned_quiz


class EditLearnedQuizQuestionSerializer(serializers.Serializer):
    option_a = serializers.CharField(max_length=255, write_only=True)
    option_b = serializers.CharField(max_length=255, write_only=True)
    option_c = serializers.CharField(max_length=255, write_only=True)
    option_d = serializers.CharField(max_length=255, write_only=True)
    question = serializers.CharField(max_length=255)
    correct_option = serializers.ChoiceField(choices=option_choices, required=False, write_only=True)
    score = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        instance.question = validated_data['question']
        instance.score = validated_data['score']
        instance.save()
   
        options = instance.get_answers()
        options_tuple = [('option_a', 'Opsi A'), ('option_b', 'Opsi B'), ('option_c', 'Opsi C'), ('option_d', 'Opsi D')]
        for option in options_tuple:
            if option[0] in validated_data:
                answer = options.get(alias=option[0])
                answer.option_answer = validated_data[option[0]]
                if 'correct_option' in validated_data:
                    answer.isCorrect = validated_data['correct_option'] == option[1]
                answer.save()

        return instance

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