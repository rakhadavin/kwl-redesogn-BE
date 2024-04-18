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

class KnowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Know
        fields = ('id', 'topic', 'type' )

class AddKnowQuizQuestionSerializer(serializers.ModelSerializer):
    option_a = serializers.CharField(max_length=255, required=True, write_only=True)
    option_b = serializers.CharField(max_length=255, required=True, write_only=True)
    option_c = serializers.CharField(max_length=255, required=False, write_only=True)
    option_d = serializers.CharField(max_length=255, required=False, write_only=True)
    correct_option = serializers.ChoiceField(choices=option_choices, required=True, write_only=True)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), write_only=True)
    type = serializers.ChoiceField(choices=know_choices, required=True, write_only=True)

    # option_a = serializers.CharField(max_length=255, required=True, write_only=True)
    # option_b = serializers.CharField(max_length=255, required=True, write_only=True)
    # option_c = serializers.CharField(max_length=255, required=False, write_only=True)
    # option_d = serializers.CharField(max_length=255, required=False, write_only=True)
    # question = serializers.CharField(max_length=255, required=True)
    # type = serializers.ChoiceField(choices=know_choices, required=True, write_only=True)
    # image = serializers.ImageField(required=False)
    # correct_option = serializers.ChoiceField(choices=option_choices, required=True, write_only=True)
    # score = serializers.IntegerField(required=True)
    # topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())
    # options = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = KnowQuizQuestion
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'question', 'type', 'image', 'correct_option', 'score', 'topic', 'know']
    
    def create(self, validated_data):
        topic = validated_data.pop('topic', None)

        
        options_data = [
        {'option_answer': validated_data.pop('option_a'), 'isCorrect': validated_data['correct_option'] == 'Opsi A', 'alias': 'option_a'},
        {'option_answer': validated_data.pop('option_b'), 'isCorrect': validated_data['correct_option'] == 'Opsi B', 'alias': 'option_b'},
        ]
        if validated_data['option_c']:
            options_data.append({'option_answer': validated_data.pop('option_c'), 'isCorrect': validated_data['correct_option'] == 'Opsi C', 'alias': 'option_c'})
        if validated_data['option_d']:
            options_data.append({'option_answer': validated_data.pop('option_d'), 'isCorrect': validated_data['correct_option'] == 'Opsi D', 'alias': 'option_d'})
    
        validated_data.pop('correct_option')   
        
    
       
        know, created = Know.objects.get_or_create(topic=topic, type=validated_data['type'])
        if not created:
            raise serializers.ValidationError("Know already exists")
        validated_data['know'] = know
        validated_data.pop('type')
        
        know_quiz = KnowQuizQuestion.objects.create(**validated_data)
        options = [KnowQuizOption(know_quiz_id=know_quiz, **option_data) for option_data in options_data]
        KnowQuizOption.objects.bulk_create(options)
        return know_quiz
     
    

     
        # topic = Topic.objects.get(pk=validated_data['topic_id'])
        # know, created = Know.objects.get_or_create(topic=self.topic)
        # know_quiz = KnowQuizQuestion.objects.create(know=know, question=validated_data['question'], score=validated_data['score'], image=validated_data['image_url'])
        # know_quiz_opt_a = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_a'], isCorrect=validated_data['correct_option'] == 'Opsi A')
        # know_quiz_opt_b = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_b'], isCorrect=validated_data['correct_option'] == 'Opsi B')
        # if validated_data['option_c']:
        #     know_quiz_opt_c = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_c'], isCorrect=validated_data['correct_option'] == 'Opsi C')
        # if validated_data['option_d']:
        #     know_quiz_opt_d = KnowQuizOption.objects.create(know_quiz_id=know_quiz, option_answer=validated_data['option_d'], isCorrect=validated_data['correct_option'] == 'Opsi D')
        # return know_quiz
    
    # def get_options(self, obj):
    #     options = KnowQuizOption.objects.filter(know_quiz_id=obj.id)
    #     return KnowQuizOptionsSerializer(options, many=True).data
    
    
class EditKnowQuizQuestionSerializer(serializers.Serializer):
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
   

        for i in ['option_a', 'option_b', 'option_c', 'option_d']:
            if i in validated_data:
                option = instance.get_answers().get(alias=i)
                option.option_answer = validated_data[i]
                if 'correct_option' in validated_data:
                    option.isCorrect = validated_data['correct_option'] == i
                option.save()

        return instance
class AddKnowEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=True)
    type = serializers.ChoiceField(choices=know_choices, required=True, write_only=True)
    score = serializers.IntegerField(required=True)
    topic_id = serializers.IntegerField(required=True, write_only=True)

    def create(self, validated_data):
        topic = Topic.objects.get(pk=validated_data['topic_id'])
        know, created = Know.objects.get_or_create(topic=topic)
        if not created:
            raise serializers.ValidationError("Know already exists")
        know_essay = KnowReflection.objects.create(know_id=know, question=validated_data['question'], score=validated_data['score'])
        
        return know_essay

class EditKnowEssaySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, required=False)
    score = serializers.IntegerField(required=False)
    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data['question']
        if 'score' in validated_data:
            instance.score = validated_data['score']
        instance.save()
        return instance
    
class KnowReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowReflection
        fields = ('id', 'question', 'score', 'know_id' )


