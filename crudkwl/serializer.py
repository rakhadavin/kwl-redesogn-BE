from rest_framework import serializers
from .views import Know, WantToKnow, Learned, KnowQuiz, KnowQuizAnswer, WantToKnowPoll, WantToKnowPollChoice

class KnowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Know
        fields = '__all__'

class WantToKnowSerializer(serializers.ModelSerializer):
    class Meta:
        model = WantToKnow
        fields = '__all__'

class LearnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Learned
        fields = '__all__'

class KnowQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowQuiz
        fields = '__all__'

class KnowQuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowQuizAnswer
        fields = '__all__'

class WantToKnowPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = WantToKnowPoll
        fields = '__all__'

class WantToKnowPollChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WantToKnowPollChoice
        fields = '__all__'

