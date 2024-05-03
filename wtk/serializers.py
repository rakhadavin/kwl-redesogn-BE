
from rest_framework import serializers

from course.api_exceptions import TopicNotFoundException
from course.models import Topic
from wtk.api_exceptions import ExistingWtkException
from wtk.models import Prereading, WantToKnow, WtkPollQuestion, WtkChoices, WtkReflection
from django.db import transaction

wtk_choices = (("checkbox", "Checkbox"), ("reflection", "Reflection"))

class WtkSerializer(serializers.ModelSerializer):
    class Meta:
        model = WantToKnow
        fields = ['id', 'topic', 'type']

class AddPollingQuestionSerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=wtk_choices,write_only=True)
    score = serializers.IntegerField()
    options = serializers.ListField(

    child=serializers.CharField(max_length=255, required=True),
    write_only=True
    )

    topic = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = WtkPollQuestion
        fields = ['id','score','question','wtk','options', 'type', 'topic']

    def create(self, validated_data):
        with transaction.atomic():
            wtk, created = WantToKnow.objects.get_or_create(topic_id=validated_data['topic'], type=validated_data['type'])
            if not created:
                raise ExistingWtkException("Want to know already exists")
            
            poll_question = WtkPollQuestion.objects.create(question=validated_data['question'], score=validated_data['score'], wtk=wtk)
            for i in range(len(validated_data['options'])):
                if validated_data['options'][i]:
                    choice = WtkChoices.objects.create(option_answer=validated_data['options'][i])
                    poll_question.choices.add(choice)

        return poll_question
    
class EditPollingQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=False)
    score = serializers.IntegerField(required=False)
    options = serializers.ListField(
    child=serializers.CharField(max_length=255, required=False),
    required=False,
    write_only=True
    )
    options_ids = serializers.ListField(
    child=serializers.IntegerField(required=False),
    required=False,
    write_only=True
    )
    topic_id = serializers.IntegerField(required=False, write_only=True)
    id = serializers.IntegerField(required=True, write_only=True)

    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        if len(validated_data['options']) != len(validated_data['options_ids']):
            raise serializers.ValidationError("Length of options and options ids must be equal")
        for i in range(len(validated_data['options'])):
            if validated_data['options'][i]:
                choice = WtkChoices.objects.get(id=validated_data['options_ids'][i])
                choice.option_answer = validated_data['options'][i]
                choice.save()
        return instance

class WtkPollingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkChoices
        fields = ['option_answer', 'id']

class WtkPollingQuestionSerializer(serializers.ModelSerializer):
    choices = WtkPollingAnswerSerializer(many=True, read_only=True, source='wtkchoices_set')
    class Meta:
        model = WtkPollQuestion
        fields = ['score', 'question', 'wtk', 'id', 'choices']




class AddWtkEssaySerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=wtk_choices, write_only=True)
    score = serializers.IntegerField(required=True)
    topic = serializers.IntegerField(write_only=True)

    class Meta:
        model = WtkReflection
        fields = ['question', 'type', 'score', 'topic', 'id']

    def create(self, validated_data):
        with transaction.atomic():
            topic = get_topic(validated_data['topic'])

            wtk, created = WantToKnow.objects.get_or_create(topic=topic, type=validated_data['type'])
            if not created:
                raise ExistingWtkException("Want to know already exists")
            
            wtk_essay = WtkReflection.objects.create(wtk=wtk, question=validated_data['question'], score=validated_data['score'])
        
        return wtk_essay
    
class WtkReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkReflection
        fields = ('id', 'question', 'score', 'wtk' )

class EditWtkEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=False)
    score = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        instance.save()
        return instance
    
class AddPrereadingSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, use_url=True, required=False)
    topic = serializers.IntegerField(write_only=True)

    class Meta:
        model = Prereading
        fields = ('id', 'prereading', 'wtk', 'file')

    def create(self, validated_data):
        with transaction.atomic():
            topic = get_topic(validated_data['topic'])
            try:
                wtk = WantToKnow.objects.get(topic=topic)
            except WantToKnow.DoesNotExist:
                raise WantToKnow.DoesNotExist("Want to know does not exist")
            prereading = Prereading.objects.create(prereading=validated_data['prereading'], wtk=wtk, file=validated_data['file'])
        
        return prereading

class EditPrereadingSerializer(serializers.Serializer):
    prereading = serializers.CharField(max_length=255)
    file = serializers.FileField(max_length=None, use_url=True, required=False)

    def update(self, instance, validated_data):
      
        instance.prereading = validated_data['prereading']
        if 'file' in validated_data:
            instance.file.delete()
            instance.file = validated_data['file']
        instance.save()
        return instance

class PrereadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prereading
        fields = ('id', 'prereading', 'file', 'wtk')

def get_topic(topic_id):
    try:
        return Topic.objects.get(pk=topic_id)
    except Topic.DoesNotExist:
        raise TopicNotFoundException()