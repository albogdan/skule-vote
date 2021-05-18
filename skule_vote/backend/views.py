from backend.models import (
    Election,
    ElectionSession,
    Eligibility,
    Candidate,
    Voter,
    Ballot,
)

from rest_framework import generics
from backend.serializers import ElectionSerializer


class ElectionListView(generics.ListAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
