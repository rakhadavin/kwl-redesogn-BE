from rest_framework import serializers

from course.models import Topic
from .models import Know, KnowQuizQuestion, KnowQuizOption, KnowReflection

option_choices = (("Opsi A", "Opsi A"), ("Opsi B", "Opsi B"), ("Opsi C", "Opsi C"), ("Opsi D", "Opsi D"))
know_choices = (("reflection", "Reflection"), ("quiz", "Quiz"))

class KnowQuizOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowQuizOption
        fields = ('id', 'option_answer', 'isCorrect' ) 
        
class KnowQuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowQuizQuestion
        fields = ('id', 'question', 'score', 'image', 'know' )

class AddKnowQuizQuestionSerializer(serializers.Serializer):
    option_a = serializers.CharField(max_length=255, required=True, write_only=True)
    option_b = serializers.CharField(max_length=255, required=True, write_only=True)
    option_c = serializers.CharField(max_length=255, required=False, write_only=True)
    option_d = serializers.CharField(max_length=255, required=False, write_only=True)
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=know_choices, required=True, write_only=True)
    image_url = serializers.ImageField(required=False)
    correct_option = serializers.ChoiceField(choices=option_choices, required=True, write_only=True)
    score = serializers.IntegerField(required=True)
    topic_id = serializers.IntegerField(required=True, write_only=True)
    options = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):

        topic = Topic.objects.get(pk=validated_data['topic_id'])
        know, created = Know.objects.get_or_create(topic=topic)
        know_quiz = KnowQuizQuestion.objects.create(know=know, question=validated_data['question'], score=validated_data['score'], image=validated_data['image_url'])
        know_quiz_opt_a = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_a'], isCorrect=validated_data['correct_option'] == 'Opsi A')
        know_quiz_opt_b = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_b'], isCorrect=validated_data['correct_option'] == 'Opsi B')
        if validated_data['option_c']:
            know_quiz_opt_c = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_c'], isCorrect=validated_data['correct_option'] == 'Opsi C')
        if validated_data['option_d']:
            know_quiz_opt_d = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_d'], isCorrect=validated_data['correct_option'] == 'Opsi D')
        return know_quiz
    
    def get_options(self, obj):
        options = KnowQuizOption.objects.filter(know_quiz_id=obj.id)
        return KnowQuizOptionsSerializer(options, many=True).data
  
class AddKnowEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=know_choices, required=True, write_only=True)
    score = serializers.IntegerField(required=True)
    topic_id = serializers.IntegerField(required=True, write_only=True)

    def create(self, validated_data):
        topic = Topic.objects.get(pk=validated_data['topic_id'])
        know, created = Know.objects.get_or_create(topic=topic)
        know_essay = KnowReflection.objects.create(know_id=know, question=validated_data['question'], score=validated_data['score'])
        
        return know_essay