from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from authentication.permissions import isLecturer
from kuesioner.models import Kuesioner, KuesionerSession, GuestQuizAttempt, GuestQuizAnswer
import json


@api_view(['GET'])
@permission_classes([isLecturer])
def get_session_recap(request, kuesioner_id):
    """
    Endpoint untuk mendapatkan rekap semua sesi kuesioner untuk Polling dan Open Ended
    """
    try:
        kuesioner = get_object_or_404(Kuesioner, id=kuesioner_id)
        
        # Hanya untuk Polling dan Open Ended
        if kuesioner.question_type not in ['Polling', 'Open Ended']:
            return Response({
                'error': 'Session recap is only available for Polling and Open Ended questions'
            }, status=400)

        # Get semua sesi untuk kuesioner ini
        sessions = KuesionerSession.objects.filter(
            kuesioner=kuesioner
        ).order_by('-started_at')

        session_data = []
        
        for session in sessions:
            # Get participants untuk sesi ini
            participants = GuestQuizAttempt.objects.filter(session=session)
            participant_count = participants.count()
            
            # Get semua answers untuk sesi ini
            answers = GuestQuizAnswer.objects.filter(
                guest__session=session
            ).select_related('question', 'guest').prefetch_related('selected_choices')
            
            # Group answers by question
            questions_data = {}
            
            for answer in answers:
                question_id = str(answer.question.id)
                if question_id not in questions_data:
                    questions_data[question_id] = {
                        'question_id': question_id,
                        'question_text': answer.question.question_text,
                        'question_number': answer.question.number,
                        'answers': []
                    }
                
                # Format answer berdasarkan tipe
                if kuesioner.question_type == 'Polling':
                    # Untuk polling, ambil selected choices
                    selected_choices = list(answer.selected_choices.values('id', 'choice_text'))
                    questions_data[question_id]['answers'].append({
                        'guest_name': answer.guest.guest_name,
                        'guest_id': str(answer.guest.id),
                        'selected_choices': selected_choices,
                        'answered_at': answer.created_at.isoformat()
                    })
                elif kuesioner.question_type == 'Open Ended':
                    # Untuk open ended, ambil text answer
                    questions_data[question_id]['answers'].append({
                        'guest_name': answer.guest.guest_name,
                        'guest_id': str(answer.guest.id),
                        'text_answer': answer.text_answer,
                        'answered_at': answer.created_at.isoformat()
                    })
            
            # Convert questions_data dict to list dan sort by question number
            questions_list = list(questions_data.values())
            questions_list.sort(key=lambda x: x.get('question_number', 0))
            
            session_info = {
                'session_id': str(session.id),
                'session_number': session.session_number,
                'started_at': session.started_at.isoformat(),
                'finished_at': session.finished_at.isoformat() if session.finished_at else None,
                'total_participants': participant_count,
                'started_by': session.started_by.user.username if session.started_by else None,
                'is_active': session.is_active,
                'questions': questions_list,
                'participants': [
                    {
                        'guest_id': str(participant.id),
                        'guest_name': participant.guest_name,
                        'joined_at': participant.created_at.isoformat()
                    } for participant in participants
                ]
            }
            
            session_data.append(session_info)

        return Response({
            'success': True,
            'kuesioner': {
                'id': str(kuesioner.id),
                'title': kuesioner.title,
                'description': kuesioner.description,
                'question_type': kuesioner.question_type,
                'pin': kuesioner.pin
            },
            'total_sessions': len(session_data),
            'sessions': session_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([isLecturer])
def get_detailed_session_recap(request, kuesioner_id, session_id):
    """
    Endpoint untuk mendapatkan rekap detail satu sesi spesifik
    """
    try:
        kuesioner = get_object_or_404(Kuesioner, id=kuesioner_id)
        session = get_object_or_404(KuesionerSession, id=session_id, kuesioner=kuesioner)
        
        # Hanya untuk Polling dan Open Ended
        if kuesioner.question_type not in ['Polling', 'Open Ended']:
            return Response({
                'error': 'Session recap is only available for Polling and Open Ended questions'
            }, status=400)

        # Get participants untuk sesi ini
        participants = GuestQuizAttempt.objects.filter(session=session)
        
        # Get semua answers untuk sesi ini dengan analisis lebih detail
        answers = GuestQuizAnswer.objects.filter(
            guest__session=session
        ).select_related('question', 'guest').prefetch_related('selected_choices')
        
        # Analysis per question
        questions_analysis = {}
        
        for answer in answers:
            question_id = str(answer.question.id)
            if question_id not in questions_analysis:
                questions_analysis[question_id] = {
                    'question_id': question_id,
                    'question_text': answer.question.question_text,
                    'question_number': answer.question.number,
                    'total_responses': 0,
                    'responses': []
                }
            
            questions_analysis[question_id]['total_responses'] += 1
            
            if kuesioner.question_type == 'Polling':
                # Untuk polling, hitung statistik pilihan
                selected_choices = list(answer.selected_choices.values('id', 'choice_text'))
                questions_analysis[question_id]['responses'].append({
                    'guest_name': answer.guest.guest_name,
                    'guest_id': str(answer.guest.id),
                    'selected_choices': selected_choices,
                    'answered_at': answer.created_at.isoformat()
                })
                
                # Tambah statistik pilihan jika belum ada
                if 'choice_statistics' not in questions_analysis[question_id]:
                    questions_analysis[question_id]['choice_statistics'] = {}
                
                for choice in selected_choices:
                    choice_text = choice['choice_text']
                    if choice_text not in questions_analysis[question_id]['choice_statistics']:
                        questions_analysis[question_id]['choice_statistics'][choice_text] = 0
                    questions_analysis[question_id]['choice_statistics'][choice_text] += 1
                    
            elif kuesioner.question_type == 'Open Ended':
                # Untuk open ended, kumpulkan semua text responses
                questions_analysis[question_id]['responses'].append({
                    'guest_name': answer.guest.guest_name,
                    'guest_id': str(answer.guest.id),
                    'text_answer': answer.text_answer,
                    'answered_at': answer.created_at.isoformat()
                })
        
        # Convert to list dan sort by question number
        questions_list = list(questions_analysis.values())
        questions_list.sort(key=lambda x: x.get('question_number', 0))
        
        return Response({
            'success': True,
            'session': {
                'session_id': str(session.id),
                'session_number': session.session_number,
                'started_at': session.started_at.isoformat(),
                'finished_at': session.finished_at.isoformat() if session.finished_at else None,
                'total_participants': participants.count(),
                'started_by': session.started_by.user.username if session.started_by else None,
                'is_active': session.is_active
            },
            'kuesioner': {
                'id': str(kuesioner.id),
                'title': kuesioner.title,
                'description': kuesioner.description,
                'question_type': kuesioner.question_type,
                'pin': kuesioner.pin
            },
            'participants': [
                {
                    'guest_id': str(participant.id),
                    'guest_name': participant.guest_name,
                    'joined_at': participant.created_at.isoformat(),
                    'score': participant.score
                } for participant in participants
            ],
            'questions_analysis': questions_list
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([isLecturer])
def export_session_data(request, kuesioner_id):
    """
    Endpoint untuk export data semua sesi dalam format yang bisa didownload
    """
    try:
        kuesioner = get_object_or_404(Kuesioner, id=kuesioner_id)
        
        # Hanya untuk Polling dan Open Ended
        if kuesioner.question_type not in ['Polling', 'Open Ended']:
            return Response({
                'error': 'Export is only available for Polling and Open Ended questions'
            }, status=400)

        # Get semua data lengkap
        sessions = KuesionerSession.objects.filter(
            kuesioner=kuesioner
        ).order_by('-started_at')

        export_data = {
            'kuesioner_info': {
                'id': str(kuesioner.id),
                'title': kuesioner.title,
                'description': kuesioner.description,
                'question_type': kuesioner.question_type,
                'pin': kuesioner.pin,
                'created_at': kuesioner.created_at.isoformat()
            },
            'export_timestamp': timezone.now().isoformat(),
            'total_sessions': sessions.count(),
            'sessions_data': []
        }

        for session in sessions:
            participants = GuestQuizAttempt.objects.filter(session=session)
            answers = GuestQuizAnswer.objects.filter(
                guest__session=session
            ).select_related('question', 'guest').prefetch_related('selected_choices')
            
            session_export = {
                'session_info': {
                    'session_id': str(session.id),
                    'session_number': session.session_number,
                    'started_at': session.started_at.isoformat(),
                    'finished_at': session.finished_at.isoformat() if session.finished_at else None,
                    'total_participants': participants.count()
                },
                'participants': [
                    {
                        'guest_id': str(p.id),
                        'guest_name': p.guest_name,
                        'joined_at': p.created_at.isoformat()
                    } for p in participants
                ],
                'answers': []
            }
            
            for answer in answers:
                answer_data = {
                    'question_id': str(answer.question.id),
                    'question_text': answer.question.question_text,
                    'question_number': answer.question.number,
                    'guest_name': answer.guest.guest_name,
                    'guest_id': str(answer.guest.id),
                    'answered_at': answer.created_at.isoformat()
                }
                
                if kuesioner.question_type == 'Polling':
                    answer_data['selected_choices'] = list(
                        answer.selected_choices.values('choice_text')
                    )
                elif kuesioner.question_type == 'Open Ended':
                    answer_data['text_answer'] = answer.text_answer
                
                session_export['answers'].append(answer_data)
            
            export_data['sessions_data'].append(session_export)

        return Response({
            'success': True,
            'export_data': export_data
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)