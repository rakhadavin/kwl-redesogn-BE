
from rest_framework import serializers

from course.api_exceptions import TopicNotFoundException
from course.models import Topic
from wtk.api_exceptions import ExistingWtkException, PrereadingAlreadyExistsException, WtkDoesNotExistException
from wtk.models import Prereading, WantToKnow, WtkPollQuestion, WtkChoices, WtkReflection
from django.db import transaction

wtk_choices = (("checkbox", "Checkbox"), ("reflection", "Reflection"))

class WtkSerializer(serializers.ModelSerializer):
    class Meta:
        model = WantToKnow
        fields = ['id', 'topic', 'type','prereading']

class AddPollingQuestionSerializer(serializers.ModelSerializer):
    question = serializers.CharField()
    type = serializers.ChoiceField(choices=wtk_choices,write_only=True)
    score = serializers.IntegerField()
    options = serializers.ListField(

    child=serializers.CharField(max_length=1000, required=True),
    write_only=True
    )

    topic = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = WtkPollQuestion
        fields = ['id','score','question','wtk','options', 'type', 'topic']

    def create(self, validated_data):
        with transaction.atomic():
            wtk, created = WantToKnow.objects.get_or_create(topic_id=validated_data['topic'])
            if not created:
                raise ExistingWtkException("Want to know already exists")
            wtk.type = validated_data['type']
            wtk.save()
            
            poll_question = WtkPollQuestion.objects.create(question=validated_data['question'], score=validated_data['score'], wtk=wtk)
            for i in range(len(validated_data['options'])):
                if validated_data['options'][i]:
                    choice = WtkChoices.objects.create(option_answer=validated_data['options'][i])
                    poll_question.choices.add(choice)

        return poll_question
    
class EditPollingQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, required=False)
    score = serializers.IntegerField(required=False)
    options = serializers.ListField(
    child=serializers.CharField(max_length=1000, required=False),
    required=False,
    write_only=True
    )
    options_ids = serializers.ListField(
    child=serializers.IntegerField(required=False),
    required=False,
    write_only=True
    )
    topic = serializers.IntegerField(required=False, write_only=True)

    def update(self, instance: WtkPollQuestion, validated_data):
        with transaction.atomic():
            if 'question' in validated_data:
                instance.question = validated_data['question']
            if 'score' in validated_data:
                instance.score = validated_data['score']
            if len(validated_data['options']) != len(validated_data['options_ids']):
                raise serializers.ValidationError("Length of options and options ids must be equal")
            
            total_options_before_updated = instance.choices.count()
            total_options_after_updated = len(validated_data['options'])

            if total_options_before_updated > total_options_after_updated:
                # update the existing options
                for i in range(total_options_after_updated):
                    choice = WtkChoices.objects.get(id=validated_data['options_ids'][i])
                    choice.option_answer = validated_data['options'][i]
                    choice.save()
                # remove the rest of the options
                choices = instance.choices.all()
                for i in range(total_options_before_updated - 1, total_options_after_updated - 1, -1):
                    # delete that is not in the validated_data options_ids
                    choice: WtkChoices = choices[i]
                    choice.delete()
                    

            elif total_options_before_updated < total_options_after_updated:
                for i in range(0, total_options_before_updated):
                    choice = WtkChoices.objects.get(id=validated_data['options_ids'][i])
                    choice.option_answer = validated_data['options'][i]
                    choice.save()
                for i in range(total_options_before_updated, total_options_after_updated):
                    choice = WtkChoices.objects.create(option_answer=validated_data['options'][i])
                    instance.choices.add(choice)
            else:
                for i in range(len(validated_data['options'])):
                    if validated_data['options'][i]:
                        choice = WtkChoices.objects.get(id=validated_data['options_ids'][i])
                        choice.option_answer = validated_data['options'][i]
                        choice.save()
            instance.save()
        return instance

class WtkPollingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkChoices
        fields = ['option_answer', 'id']

class WtkMultipleChoiceAnswerSerializer(serializers.Serializer):
    choices = serializers.ListField(
        child=serializers.IntegerField(required=True),
        required=True
    )
    topic = serializers.IntegerField(required=True)

class WtkPollingQuestionSerializer(serializers.ModelSerializer):
    choices = WtkPollingAnswerSerializer(many=True, read_only=True, source='wtkchoices_set')
    wtk = WtkSerializer(read_only=True)
    class Meta:
        model = WtkPollQuestion
        fields = ['score', 'question', 'wtk', 'id', 'choices']

class AddWtkEssaySerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=1000, required=True)
    type = serializers.ChoiceField(choices=wtk_choices, write_only=True)
    score = serializers.IntegerField(required=True)
    topic = serializers.IntegerField(write_only=True)

    class Meta:
        model = WtkReflection
        fields = ['question', 'type', 'score', 'topic', 'id']

    def create(self, validated_data):
        with transaction.atomic():
            topic = get_topic(validated_data['topic'])

            wtk, created = WantToKnow.objects.get_or_create(topic=topic)
            if not created:
                raise ExistingWtkException("Want to know already exists")
            wtk.type = validated_data['type']
            wtk.save()
            
            wtk_essay = WtkReflection.objects.create(wtk=wtk, question=validated_data['question'], score=validated_data['score'])
        
        return wtk_essay
    
class WtkReflectionSerializer(serializers.ModelSerializer):
    wtk = WtkSerializer(read_only=True)
    class Meta:
        model = WtkReflection
        fields = ('id', 'question', 'score', 'wtk' )

class EditWtkEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, required=False)
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
    prereading = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    class Meta:
        model = Prereading
        fields = ('id', 'prereading','file', 'topic')

    def create(self, validated_data):
        with transaction.atomic():
            topic = get_topic(validated_data['topic'])
            

            prereading, created = Prereading.objects.get_or_create(topic=topic)
            if validated_data['prereading']:
                prereading.prereading = validated_data['prereading']
            
            try:
                wtk = WantToKnow.objects.get(topic=topic)
            except WantToKnow.DoesNotExist:
                raise WtkDoesNotExistException()
            wtk.prereading = prereading
            wtk.save()
            if not created:
                raise PrereadingAlreadyExistsException()
            if 'file' in validated_data:
                prereading.file = validated_data['file']
            prereading.save()
        
        return prereading

class EditPrereadingSerializer(serializers.Serializer):
    prereading = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    file = serializers.FileField(max_length=None, use_url=True, required=False)

    def update(self, instance, validated_data):
      
        instance.prereading = validated_data['prereading']
        if 'file' in validated_data:
            instance.file.delete()
            instance.file = validated_data['file']
        instance.save()
        return instance

class PrereadingSerializer(serializers.ModelSerializer): #Create, retrieval, and delete only
    class Meta:
        model = Prereading
        fields = ('id', 'prereading', 'file', 'topic')
    
class WtkReflectionAnswerSerializer(serializers.Serializer):
    reflection = serializers.CharField(max_length=5000)
    topic = serializers.IntegerField(write_only=True)


def get_topic(topic_id):
    try:
        return Topic.objects.get(pk=topic_id)
    except Topic.DoesNotExist:
        raise TopicNotFoundException()