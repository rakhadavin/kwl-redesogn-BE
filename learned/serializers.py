from rest_framework import serializers

from course.models import Topic
from .models import Learned, LearnedReflection

learned_choices = (("reflection", "Reflection"), ("quiz", "Quiz"))

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