from rest_framework import serializers
from ..models import Kuesioner, Question, Choice, GuestQuizAttempt


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'number', 'question_text', 'time_limit', 'score', 'choices', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class KuesionerListSerializer(serializers.ModelSerializer):
    """
    Serializer untuk list kuesioner (tanpa questions detail)
    """
    questions_count = serializers.SerializerMethodField()
    lecturer_team = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Kuesioner
        fields = [
            'id', 'title', 'description', 'question_type', 'visibility', 'lecturer_team',
            'pin', 'is_started', 'is_lobby', 'if_finished', 
            'questions_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'pin', 'created_at', 'updated_at']
    
    def get_questions_count(self, obj):
        return obj.questions.count()
    

# ============= SERIALIZERS UNTUK WRITE OPERATIONS =============

class ChoiceWriteSerializer(serializers.Serializer):
    """Serializer untuk write choice data"""
    choice_text = serializers.CharField(max_length=500)
    is_correct = serializers.BooleanField(default=False)

class QuestionWriteSerializer(serializers.Serializer):
    """Serializer untuk write question data"""
    question_text = serializers.CharField()
    time_limit = serializers.IntegerField(default=60)
    score = serializers.IntegerField(default=10)
    choices = ChoiceWriteSerializer(many=True, required=False)  # Optional untuk Open Ended
    number = serializers.IntegerField(required=False)  # Optional field for question number

class KuesionerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer untuk create kuesioner DENGAN questions
    """
    questions = QuestionWriteSerializer(many=True, required=False)
    
    class Meta:
        model = Kuesioner
        fields = ['title', 'description', 'question_type', 'visibility', 'questions']
    
    def validate(self, data):
        """Validasi berdasarkan question_type"""
        question_type = data.get('question_type')
        questions_data = data.get('questions', [])
        
        # Validasi untuk Multiple Choice dan Polling - harus ada choices
        if question_type in ['Multiple Choice', 'Polling']:
            for question in questions_data:
                choices = question.get('choices', [])
                if not choices or len(choices) == 0:
                    raise serializers.ValidationError({
                        'questions': f'{question_type} questions must have at least one choice'
                    })
                
                # Validasi Multiple Choice harus ada yang correct
                if question_type == 'Multiple Choice':
                    has_correct = any(choice.get('is_correct', False) for choice in choices)
                    if not has_correct:
                        raise serializers.ValidationError({
                            'questions': 'Multiple Choice questions must have at least one correct answer'
                        })
        
        return data
    
    def create(self, validated_data):
        """Create kuesioner beserta questions dan choices"""
        questions_data = validated_data.pop('questions', [])
        
        # Set default values
        validated_data['is_started'] = False
        validated_data['if_finished'] = False
        validated_data['is_lobby'] = False
        
        # Create kuesioner
        kuesioner = Kuesioner.objects.create(**validated_data)
        
        # Create questions dan choices
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            
            # Create question
            question = Question.objects.create(
                kuesioner=kuesioner,
                question_text=question_data['question_text'],
                time_limit=question_data.get('time_limit', 60),
                score=question_data.get('score', 10),
                number=question_data.get('number', None)
            )
            
            # Create choices (jika ada)
            for choice_data in choices_data:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_data['choice_text'],
                    is_correct=choice_data.get('is_correct', False)
                )
        
        return kuesioner


class KuesionerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer untuk detail kuesioner (dengan questions)
    """
    questions = QuestionSerializer(many=True, read_only=True)
    lecturer_team = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Kuesioner
        fields = [
            'id', 'title', 'description', 'question_type', 'visibility', 'lecturer_team',
            'pin', 'is_started', 'is_lobby', 'if_finished', 
            'questions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'pin', 'created_at', 'updated_at']


class KuesionerUpdateSerializer(serializers.ModelSerializer):
    """Serializer untuk update kuesioner lengkap dengan questions"""
    questions = QuestionWriteSerializer(many=True, required=False)

    class Meta:
        model = Kuesioner
        fields = ['title', 'description', 'question_type', 'visibility', 'questions']

    def validate(self, data):
        """Validation logic yang sama dengan create"""
        question_type = data.get('question_type')
        questions_data = data.get('questions', [])
        
        # Validasi untuk Multiple Choice dan Polling - harus ada choices
        if question_type in ['Multiple Choice', 'Polling']:
            for question in questions_data:
                choices = question.get('choices', [])
                if not choices or len(choices) == 0:
                    raise serializers.ValidationError({
                        'questions': f'{question_type} questions must have at least one choice'
                    })
                
                if question_type == 'Multiple Choice':
                    has_correct = any(choice.get('is_correct', False) for choice in choices)
                    if not has_correct:
                        raise serializers.ValidationError({
                            'questions': 'Multiple Choice questions must have at least one correct answer'
                        })
        
        return data

    def update(self, instance, validated_data):
        """Update kuesioner dengan basic info dan questions"""
        questions_data = validated_data.pop('questions', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if questions_data is not None:
            instance.questions.all().delete()
            
            for question_data in questions_data:
                choices_data = question_data.pop('choices', [])
                
                question = Question.objects.create(
                    kuesioner=instance,
                    question_text=question_data['question_text'],
                    time_limit=question_data.get('time_limit', 60),
                    score=question_data.get('score', 10)
                )
                
                for choice_data in choices_data:
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_data['choice_text'],
                        is_correct=choice_data['is_correct']
                    )
        
        return instance


# ============= SERIALIZERS UNTUK GUEST =============

class GuestJoinKuesionerSerializer(serializers.Serializer):
    """Serializer untuk guest join kuesioner"""
    guest_name = serializers.CharField(max_length=255)

class GuestKuesionerAttemptSerializer(serializers.ModelSerializer):
    """Serializer untuk response guest attempt"""
    kuesioner_info = serializers.SerializerMethodField()
    
    class Meta:
        model = GuestQuizAttempt
        fields = ['id', 'guest_name', 'score', 'completed_at', 'created_at', 'kuesioner_info']
        read_only_fields = ['id', 'score', 'completed_at', 'created_at']
    
    def get_kuesioner_info(self, obj):
        return {
            'id': obj.kuesioner.id,
            'title': obj.kuesioner.title,
            'description': obj.kuesioner.description,
            'pin': obj.kuesioner.pin
        }

class UpdateGuestNameSerializer(serializers.Serializer):
    """Serializer untuk update guest name"""
    guest_name = serializers.CharField(max_length=255)