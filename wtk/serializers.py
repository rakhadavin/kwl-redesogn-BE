
from rest_framework import serializers

from course.models import Topic
from wtk.models import Prereading, WtkPollQuestion, WantToKnow, WtkChoices, WtkReflection

wtk_choices = (("checkbox", "Checkbox"), ("reflection", "Reflection"))

class WtkSerializer(serializers.ModelSerializer):
    class Meta:
        model = WantToKnow
        fields = ['id', 'topic', 'type']
class AddPollingQuestionSerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=wtk_choices, required=True, write_only=True)
    score = serializers.IntegerField(required=True)
    options = serializers.ListField(
    child=serializers.CharField(max_length=255, required=True),
    required=False,
    write_only=True
    )

    topic_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = WtkPollQuestion
        fields = ['id','score','question','wtk','options', 'type', 'topic_id']

    def create(self, validated_data):

        wtk, created = WantToKnow.objects.get_or_create(topic_id=validated_data['topic_id'], type=validated_data['type'])
        if not created:
            raise serializers.ValidationError("Want to know already exists")    
        
        poll_questions = WtkPollQuestion.objects.create(question=validated_data['question'], score=validated_data['score'], wtk=wtk)
        for i in range(len(validated_data['options'])):
            if validated_data['options'][i]:
                choice = WtkChoices.objects.create(option_answer=validated_data['options'][i])
                poll_questions.choices.add(choice)

        return poll_questions
    
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


class WtkPollingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkPollQuestion
        fields = ['score', 'question', 'wtk', 'id']


class WtkPollingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkChoices
        fields = ['option_answer', 'id']

class AddWtkEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=wtk_choices, required=True, write_only=True)
    score = serializers.IntegerField(required=True)
    topic_id = serializers.IntegerField(required=True, write_only=True)

    def create(self, validated_data):
        topic = Topic.objects.get(pk=validated_data['topic_id'])
        know, created = WantToKnow.objects.get_or_create(topic=topic)
        know_essay = WtkReflection.objects.create(know_id=know, question=validated_data['question'], score=validated_data['score'])
        
        return know_essay
    
class WtkReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkReflection
        fields = ('id', 'question', 'score', 'know' )

class EditWtkEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=False)
    score = serializers.IntegerField(required=False)
    topic_id = serializers.IntegerField(required=True, write_only=True)
    id = serializers.IntegerField(required=True, write_only=True)

    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        instance.save()
        return instance
    
class AddPrereadingSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Prereading
        fields = ('id', 'prereading', 'wtk', 'file')

class EditPrereadingSerializer(serializers.Serializer):
    prereading = serializers.CharField(max_length=255, required=False)
    file = serializers.FileField(max_length=None, use_url=True, required=False)
    id = serializers.IntegerField(required=True, write_only=True)

    def update(self, instance, validated_data):
        if 'prereading' in validated_data:
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

