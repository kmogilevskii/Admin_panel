from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    related_name = 'genres',
    name = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')
        db_table = 'content"."genre'

    def __str__(self):
        return self.name


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    related_name = 'persons',
    full_name = models.CharField(_('полное имя'), max_length=255)
    birth_date = models.DateField(_('дата рождения'), blank=True)

    class Meta:
        verbose_name = _('участник')
        verbose_name_plural = _('участники')
        db_table = 'content"."person'

    def __str__(self):
        return self.full_name


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')


class FilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    related_name = 'films',
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    creation_date = models.DateField(_('дата создания фильма'), blank=True)
    certificate = models.TextField(_('сертификат'), blank=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True)
    type = models.CharField(_('тип'), max_length=20, choices=FilmWorkType.choices)
    genres = models.ManyToManyField(
        Genre,
        through='GenreFilmWork',
        through_fields=('film_work', 'genre'),
    )
    persons = models.ManyToManyField(
        Person,
        through='PersonFilmWork',
        through_fields=('film_work', 'person'),
        related_name='persons',
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')
        db_table = 'content"."film_work'

    def __str__(self):
        return self.title


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = (('film_work', 'genre'),)


class RoleType(models.TextChoices):
    DIRECTOR = 'director', _('режиссёр')
    WRITER = 'writer', _('сценарист')
    ACTOR = 'actor', _('актёр')


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(_('роль'), max_length=20, choices=RoleType.choices)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = (('film_work', 'person', 'role'),)


class RolesManager(models.Manager):
    def __init__(self, role):
        self.role = role
        super().__init__()

    def get_queryset(self):
        return super().get_queryset().filter(role=self.role)


class Directors(PersonFilmWork):
    objects = RolesManager(role='director')

    class Meta:
        proxy = True


class Writers(PersonFilmWork):
    objects = RolesManager(role='writer')

    class Meta:
        proxy = True


class Actors(PersonFilmWork):
    objects = RolesManager(role='actor')

    class Meta:
        proxy = True
