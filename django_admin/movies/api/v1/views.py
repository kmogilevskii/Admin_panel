from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, json_dumps_params={'indent': ' '})

    def get_queryset(self):
        query_set = FilmWork.objects.prefetch_related().all().values().annotate(
            genres=ArrayAgg("genres__name", distinct=True)).annotate(
            directors=ArrayAgg("persons__full_name", distinct=True,
                               filter=Q(personfilmwork__role="director"))).annotate(
            writers=ArrayAgg("persons__full_name", distinct=True,
                             filter=Q(personfilmwork__role="writer"))).annotate(
            actors=ArrayAgg("persons__full_name", distinct=True,
                            filter=Q(personfilmwork__role="actor")))
        return query_set


class Movies(MoviesApiMixin, BaseListView):

    def get_context_data(self, *, object_list=None, **kwargs):
        query_set = self.get_queryset()
        paginator = Paginator(query_set, 50)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'results': list(page_obj),
                   'page_number': page_number}
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data().get('object')
        return context
