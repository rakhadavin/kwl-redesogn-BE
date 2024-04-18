from .views import PollingView, add_prereading, edit_prereading, get_prereading_by_wtk_id, WtkEssayView
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('poll/add', PollingView.add_polling_question),
    path('poll/vote', PollingView.vote_multiple_choice),
    path('poll/count/<int:question_id>', PollingView.count_votes),
    path('poll/<int:question_id>', PollingView.get_polling_question),
    path('poll/edit', PollingView.edit_polling_question),
    path('preread/add', add_prereading),
    path('preread/edit', edit_prereading),
    path('preread/', get_prereading_by_wtk_id),
    path('essay/add', WtkEssayView.add_wtk_essay),
    path('essay/edit/<int:ref_id>', WtkEssayView.edit_wtk_essay),
    path('essay/<int:essay_id>', WtkEssayView.get_wtk_essay),
    # path('word-cloud/', WordCloudAPIView.as_view(), name='word_cloud_api'),



] 