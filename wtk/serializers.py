
from rest_framework import serializers

from course.models import Topic
from wtk.models import Prereading, WtkPollQuestion, WantToKnow, WtkChoices, WtkReflection

wtk_choices = (("checkbox", "Checkbox"), ("reflection", "Reflection"))
class AddPollingQuestionSerializer(serializers.ModelSerializer):
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=wtk_choices, required=True, write_only=True)
    score = serializers.IntegerField(required=True)
    option_1 = serializers.CharField(max_length=255, required=True, write_only=True)
    option_2 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_3 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_4 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_5 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_6 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_7 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_8 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_9 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_10 = serializers.CharField(max_length=255, required=False, write_only=True)
    topic_id = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = WtkPollQuestion
        fields = ['score','question','want_to_know', 'option_1', 'option_2', 'option_3', 'option_4', 'option_5', 'option_6', 'option_7', 'option_8', 'option_9', 'option_10', 'type', 'topic_id']

    def create(self, validated_data):
        options_array = ['option_1', 'option_2', 'option_3', 'option_4', 'option_5', 'option_6', 'option_7', 'option_8', 'option_9', 'option_10']
        wtk = WantToKnow.objects.create(type=validated_data['type'], topic_id=validated_data['topic_id'])
        poll_questions = WtkPollQuestion.objects.create(question=validated_data['question'], score=validated_data['score'], want_to_know=wtk)

        for i in options_array:
            if i in validated_data and validated_data[i]:
                WtkChoices.objects.create(wtk_poll_question_id=poll_questions, option_answer=validated_data[i], alias=i)

        return poll_questions
    
class EditPollingQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=False)
    score = serializers.IntegerField(required=False)
    option_1 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_2 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_3 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_4 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_5 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_6 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_7 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_8 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_9 = serializers.CharField(max_length=255, required=False, write_only=True)
    option_10 = serializers.CharField(max_length=255, required=False, write_only=True)
    topic_id = serializers.IntegerField(required=True, write_only=True)
    id = serializers.IntegerField(required=True, write_only=True)

    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        existed_choices = WtkChoices.objects.filter(wtk_poll_question_id=instance)
        options_array = ['option_1', 'option_2', 'option_3', 'option_4', 'option_5', 'option_6', 'option_7', 'option_8', 'option_9', 'option_10']
        for i in options_array:
            if i in validated_data and validated_data[i]:
                if existed_choices.exists() and i == existed_choices[i].alias:
                    existed_choices[i].option_answer = validated_data[i]
                    existed_choices[i].save()
                else:
                    WtkChoices.objects.create(wtk_poll_question_id=instance, option_answer=validated_data[i])
        instance.save()
        return instance


class WtkPollingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkPollQuestion
        fields = ['score', 'question', 'want_to_know']


class WtkPollingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WtkChoices
        fields = ['option_answer', 'wtk_poll_question_id']

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
        fields = ('id', 'prereading', 'wtk_id', 'file')

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
        fields = ('id', 'prereading', 'file', 'wtk_id')

