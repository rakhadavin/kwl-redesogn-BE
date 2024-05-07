
from django.urls import path
from .views import WordCloudAPIView, KwlPointLadderView, KwlParticipantCountView


urlpatterns = [
    path('wordcloud/<str:type>/<int:topic>', WordCloudAPIView.as_view(), name="wordcloud"),
    path('topic-ladder/<int:topic>', KwlPointLadderView.as_view(), name="kwl-point-ladder"),
    path('kwl-participants/<int:topic>', KwlParticipantCountView.as_view(), name="kwl-participants"),
   

]