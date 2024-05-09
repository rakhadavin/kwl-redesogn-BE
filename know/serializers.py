from rest_framework import serializers

from authentication.api_exceptions import StudentNotFoundException
from authentication.models import Student
from course.models import Topic, RewardStudentPoint
from .models import Know, KnowQuizQuestion, KnowQuizOption, KnowReflection, KnowReflectionStudentAnswer
from .api_exceptions import ExistingKnowException
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
        fields = ('id', 'question', 'score', 'image', 'know', 'options' )

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
    topic = serializers.IntegerField(write_only=True)
    type = serializers.ChoiceField(choices=know_choices, required=True, write_only=True)

    class Meta:
        model = KnowQuizQuestion
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'question', 'type', 'image', 'correct_option', 'score', 'topic', 'know']
    
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
            know, created = Know.objects.get_or_create(topic=topic)

            if not created and know.type != validated_data['type']:
                raise ExistingKnowException("Know already exists")
            
            validated_data['know'] = know
            know.type = validated_data.pop('type')
            know.save()
            
            know_quiz = KnowQuizQuestion.objects.create(**validated_data)
            options = [KnowQuizOption(know_quiz=know_quiz, **option_data) for option_data in options_data]
            KnowQuizOption.objects.bulk_create(options)

        return know_quiz
    

class EditKnowQuizQuestionSerializer(serializers.Serializer):
    option_a = serializers.CharField(max_length=255, write_only=True)
    option_b = serializers.CharField(max_length=255, write_only=True)
    option_c = serializers.CharField(max_length=255, write_only=True)
    option_d = serializers.CharField(max_length=255, write_only=True)
    question = serializers.CharField(max_length=255)
    image = serializers.ImageField(required=False)
    correct_option = serializers.ChoiceField(choices=option_choices, write_only=True)
    score = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        
        instance.question = validated_data['question']
        instance.score = validated_data['score']

        if 'image' in validated_data:
            instance.image.delete(save=False)
            instance.image = validated_data['image']

        instance.save()
        options = instance.get_answers()
  
        options_tuple = [('option_a', 'Opsi A'), ('option_b', 'Opsi B'), ('option_c', 'Opsi C'), ('option_d', 'Opsi D')]

        for option in options_tuple:
            if option[0] in validated_data:
                answer = options.get(alias=option[0])
                answer.option_answer = validated_data[option[0]]
                answer.isCorrect = validated_data['correct_option'] == option[1]
                answer.save()

        return instance
    
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