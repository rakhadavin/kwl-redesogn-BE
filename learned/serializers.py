from rest_framework import serializers

from course.models import Topic
from .models import Learned, LearnedReflection, LearnedQuizOption, LearnedQuizQuestion, LearnedReflectionStudentAnswer
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
    class Meta:
        model = LearnedQuizQuestion
        fields = ('id', 'question', 'score', 'image', 'know' )

class LearnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Learned
        fields = ('id', 'topic', 'type' )


class AddLearnedQuizQuestionSerializer(serializers.ModelSerializer):
    option_a = serializers.CharField(max_length=255, required=True, write_only=True)
    option_b = serializers.CharField(max_length=255, required=True, write_only=True)
    option_c = serializers.CharField(max_length=255, required=False, write_only=True)
    option_d = serializers.CharField(max_length=255, required=False, write_only=True)
    correct_option = serializers.ChoiceField(choices=option_choices, required=True, write_only=True)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), write_only=True)
    type = serializers.ChoiceField(choices=learned_choices, required=True, write_only=True)

    class Meta:
        model = LearnedQuizQuestion
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'question', 'type', 'image', 'correct_option', 'score', 'topic', 'learned']
    
    def create(self, validated_data):
        topic = validated_data.pop('topic', None)

        
        options_data = [
        {'option_answer': validated_data.pop('option_a'), 'isCorrect': validated_data['correct_option'] == 'Opsi A', 'alias': 'option_a'},
        {'option_answer': validated_data.pop('option_b'), 'isCorrect': validated_data['correct_option'] == 'Opsi B', 'alias': 'option_b'},
        ]
        if validated_data['option_c']:
            options_data.append({'option_answer': validated_data.pop('option_c'), 'alias': 'option_c'})
        if validated_data['option_d']:
            options_data.append({'option_answer': validated_data.pop('option_d'),  'alias': 'option_d'})
    
        validated_data.pop('correct_option')   
        
        know, created = Learned.objects.get_or_create(topic=topic, type=validated_data['type'])
        if not created:
            raise serializers.ValidationError("Know already exists")
        validated_data['know'] = know
        validated_data.pop('type')
        
        know_quiz = LearnedQuizQuestion.objects.create(**validated_data)
        options = [LearnedQuizOption(know_quiz_id=know_quiz, **option_data) for option_data in options_data]
        LearnedQuizOption.objects.bulk_create(options)
        return know_quiz


class EditLearnedQuizQuestionSerializer(serializers.Serializer):
    option_a = serializers.CharField(max_length=255, required=False, write_only=True)
    option_b = serializers.CharField(max_length=255, required=False, write_only=True)
    option_c = serializers.CharField(max_length=255, required=False, write_only=True)
    option_d = serializers.CharField(max_length=255, required=False, write_only=True)
    question = serializers.CharField(max_length=255, required=False)

    image = serializers.ImageField(required=False)
    correct_option = serializers.ChoiceField(choices=option_choices, required=False, write_only=True)
    score = serializers.IntegerField(required=False)
    topic_id = serializers.IntegerField(required=True, write_only=True)
    id = serializers.IntegerField(required=True, write_only=True)

    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        if 'image' in validated_data:
            instance.image.delete(save=False)
            instance.image = validated_data['image']
    
        instance.save()
   
        options = instance.get_answers()
        options_tuple = [('option_a', 'Opsi A'), ('option_b', 'Opsi B'), ('option_c', 'Opsi C'), ('option_d', 'Opsi D')]
        for option in options_tuple:
            if option[0] in validated_data:
                answer = options.get(alias=option[1])
                answer.option_answer = validated_data[option[0]]
                if 'correct_option' in validated_data:
                    answer.isCorrect = validated_data['correct_option'] == option[1]
                answer.save()

        return instance

class AddLearnedEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=learned_choices, required=True, write_only=True)
    score = serializers.IntegerField(required=True)
    topic_id = serializers.IntegerField(required=True, write_only=True)

    def create(self, validated_data):
        topic = Topic.objects.get(pk=validated_data['topic_id'])
        know, created = Learned.objects.get_or_create(topic=topic)
        know_essay = LearnedReflection.objects.create(know_id=know, question=validated_data['question'], score=validated_data['score'])
        
        return know_essay
    
class EditLearnedEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=False)
    score = serializers.IntegerField(required=False)
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
        fields = ('id', 'question', 'score', 'know' )