from .views import PollingListView, PollingDetailView, WtkEssayDetailView, WtkEssayListView, PrereadingDetailView, PrereadingListView
from django.urls import path


urlpatterns = [

    path('poll', PollingListView.as_view()),
    path('poll/<int:topic_id>', PollingDetailView.as_view()),
    path('essay', WtkEssayListView.as_view()),
    path('essay/<int:topic_id>', WtkEssayDetailView.as_view()),
    path('preread', PrereadingListView.as_view()),
    path('preread/<int:topic_id>', PrereadingDetailView.as_view()),

    # path('poll/add', PollingView.add_polling_question),
    # path('poll/vote', PollingView.vote_multiple_choice),
    # path('poll/count/<int:question_id>', PollingView.count_votes),
    # path('poll/<int:question_id>', PollingView.get_polling_question),
    # path('poll/edit', PollingView.edit_polling_question),
    # path('preread/add', add_prereading),
    # path('preread/edit', edit_prereading),
    # path('preread/', get_prereading_by_wtk_id),
    # path('essay/add', WtkEssayView.add_wtk_essay),
    # path('essay/edit/<int:ref_id>', WtkEssayView.edit_wtk_essay),
    # path('essay/<int:essay_id>', WtkEssayView.get_wtk_essay),
    # path('is_exist/<int:topic_id>', is_wtk_exist_by_topic_id),




] 