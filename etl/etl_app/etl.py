import json
import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Union

import backoff
import psycopg2
import requests
from conflow import Config, from_yaml
from psycopg2.extras import RealDictCursor, RealDictRow

import state as state_file

logger = logging.getLogger()
logger.info('Logger initialized')

BASE_DIR = Path(__file__).resolve(strict=True).parent
settings = from_yaml(BASE_DIR.joinpath('etl_configs/config.yaml'))
config = Config().merge(settings)
logger.info('Settings merged into config successfully')

state_storage = state_file.JsonFileStorage('etl_configs/state_values.json')
# state_storage.save_state({'last_updated_item_timestamp': '2000-01-01T01:00:01.000001'})
state = state_file.State(state_storage)


def extractor(target):
    """
    Функция, которая достаёт из постгреса все фильмы, изменённые после last_updated_item_timestamp,
    парсит участников и отдаёт фильмы по одному через yield. В конце отправляет строку 'Quit'.
    """
    last_updated = state.get_state('last_updated_item_timestamp')
    if last_updated is None:
        last_updated = '2000-01-01T01:00:01.000001'
    dsn = config.db()

    logger.info('Starting movie-extracting generator')
    with psycopg2.connect(**dsn, cursor_factory=RealDictCursor) as pg_conn, pg_conn.cursor() as cur:
        pg_extract_query = cur.mogrify(f'''SELECT F.ID,
            TITLE,
            RATING,
            ARRAY_AGG(DISTINCT G.NAME) AS GENRES,
            ARRAY_AGG(DISTINCT MP.ROLE || ':' || P.FULL_NAME || ':' || P.ID) AS PERSONS,
            F.DESCRIPTION,
            F.UPDATED_AT
        FROM CONTENT.FILM_WORK F
        LEFT JOIN CONTENT.PERSON_FILM_WORK MP ON F.ID = MP.FILM_WORK_ID
        LEFT JOIN CONTENT.PERSON P ON MP.PERSON_ID = P.ID
        LEFT JOIN CONTENT.GENRE_FILM_WORK GF ON F.ID = GF.FILM_WORK_ID
        LEFT JOIN CONTENT.GENRE G ON GF.GENRE_ID = G.ID
        WHERE (F.UPDATED_AT > TIMESTAMP WITH TIME ZONE '{last_updated}'
                                    OR G.UPDATED_AT > TIMESTAMP WITH TIME ZONE '{last_updated}'
                                    OR P.UPDATED_AT > TIMESTAMP WITH TIME ZONE '{last_updated}')
        GROUP BY F.ID
        ORDER BY F.UPDATED_AT
        ''')
        cur.execute(pg_extract_query)
        for dict_movie in cur:
            logger.info('Sending \'%s\' movie\'s raw data to transform-coroutine', dict_movie['title'])
            target.send(dict_movie)
        target.send('Quit')


def parse_persons(m: RealDictRow):
    """
    Парсит участников фильма и разносит их по разным полям.
    """
    logger.info('Parsing persons of %s', m['title'])
    m.update({'directors': [], 'actors': [], 'writers': []})
    for person in m.get('persons'):
        if not person:
            continue
        role, person, id = person.split(':')
        if role == 'director':
            m['directors'].append(person)
        if role == 'actor':
            m['actors'].append({'id': id, 'name': person})
        if role == 'writer':
            m['writers'].append({'id': id, 'name': person})
    m.pop('persons', None)


def no_none_needed(func):
    # Это может быть не слишком красиво звучит,
    # но это название настолько явное, насколько возможно.
    # И поэтому оно мне больше нравится, чем туманное "coroutine"
    # Я к тому, что зачем нужно такое название,
    # которое заставляет тебя судорожно рыться в коде и искать:
    # "Что же всё таки этот декоратор делает?!"
    # Explicit is better than implicit.
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner


@no_none_needed
def transform_raw_data(target):
    prepared_query = []
    temp_timestamp = None
    while dict_movie := (yield):
        dict_movie: Union[RealDictRow, str]
        if dict_movie == 'Quit':
            target.send((prepared_query, temp_timestamp))
            continue
        logger.info('Starting transformation')
        parse_persons(dict_movie)
        prepared_query.append(json.dumps({"index": {"_index": "movies", "_id": dict_movie['id']}}))
        prepared_query.append(json.dumps({"imdb_rating": dict_movie['rating'],
                                          "genre": dict_movie['genres'],
                                          "title": dict_movie['title'],
                                          "description": dict_movie['description'],
                                          "director": ', '.join(dict_movie['directors']),
                                          "actors_names": [x['name'] for x in dict_movie['actors']],
                                          "writers_names": [x['name'] for x in dict_movie['writers']],
                                          "actors": dict_movie['actors'],
                                          "writers": dict_movie['writers'],
                                          }))
        temp_timestamp = datetime.isoformat(dict_movie['updated_at'])
        if len(prepared_query) == 200:
            target.send((prepared_query, temp_timestamp))
            prepared_query.clear()


def backoff_hdlr(details):
    logger.error("Backing off {wait:0.1f} seconds afters {tries} tries "
                 "calling function {target} with args {args} and kwargs "
                 "{kwargs}".format(**details))


@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      on_backoff=backoff_hdlr)
@no_none_needed
def load_to_es():
    while True:
        prepared_query, temp_timestamp = (yield)
        if not prepared_query:
            continue
        if not isinstance(prepared_query, list):
            raise TypeError('prepared_query must be list')
        str_query = '\n'.join(prepared_query) + '\n'
        logger.info('Sending %s movies long query to es', (len(prepared_query) // 2))

        try:
            response = requests.post(url=config.es_url() + '/_bulk',
                                     data=str_query,
                                     headers={'Content-Type': 'application/x-ndjson'}
                                     )
        except Exception as err:
            logger.error(err)
            raise err

        json_response = json.loads(response.content.decode())
        for item in json_response['items']:
            error_message = item['index'].get('error')
            if error_message is None:
                state.set_state(key='last_updated_item_timestamp',
                                value=temp_timestamp)
            else:
                logger.error(error_message)
        logger.info('Query loaded, response - ', json_response)


if __name__ == '__main__':
    load = load_to_es()
    transform = transform_raw_data(load)
    extractor(transform)
