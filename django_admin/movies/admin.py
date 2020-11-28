from django.contrib import admin

from .models import FilmWork, Genre, PersonFilmWork, GenreFilmWork, Person, Actors, Directors, Writers, RoleType


class MoviePersonsInline(admin.TabularInline):
    model = PersonFilmWork
    extra = 0
    fields = ('person', 'role')
    autocomplete_fields = ('person',)


class MovieGenresInLine(admin.TabularInline):
    model = GenreFilmWork
    extra = 0
    fields = ('genre',)
    autocomplete_fields = ('genre',)


class PersonMoviesInLine(admin.TabularInline):
    model = PersonFilmWork
    extra = 0
    fields = ('film_work', 'role')
    autocomplete_fields = ('film_work',)


class GenreMoviesInLine(admin.TabularInline):
    model = GenreFilmWork
    extra = 0
    fields = ('film_work',)
    autocomplete_fields = ('film_work',)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating')

    # фильтрация в списке
    list_filter = ('type',)

    # поиск по полям
    search_fields = ('title', 'description', 'id')

    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating',
    )

    inlines = [
        MoviePersonsInline,
        MovieGenresInLine
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

    fields = ('name', 'description')

    search_fields = ('id', 'name')

    inlines = [
        GenreMoviesInLine,
    ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date',)

    fields = ('full_name', 'birth_date',)

    search_fields = ('full_name', 'id')

    inlines = [
        PersonMoviesInLine,
    ]
