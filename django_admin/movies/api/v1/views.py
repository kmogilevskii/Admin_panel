from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, json_dumps_params={'separators': [',', ': '], 'indent': ' '})


class Movies(MoviesApiMixin, BaseListView):
    def get_queryset(self):
        return FilmWork.objects.all().values()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'results': list(self.get_queryset()),
        }
        # paginate_queryset(self, )

        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    pass
