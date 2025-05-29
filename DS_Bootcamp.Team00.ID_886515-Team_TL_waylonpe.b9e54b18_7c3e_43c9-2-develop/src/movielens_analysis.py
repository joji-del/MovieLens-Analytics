import csv
from collections import Counter,defaultdict, OrderedDict
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time, json, os, re, pytest
from unittest.mock import patch, MagicMock

class Movies:

    def __init__(self, path_to_the_file):
    
        self.path_to_the_file = path_to_the_file
        self.movies = []
        self.data_load()

    def data_load(self):
        try :
            with open(self.path_to_the_file, mode ='r', encoding = 'UTF-8') as file:
                reader = csv.DictReader(file, delimiter=',', quotechar='"')
                for row in reader:
                    self.movies.append(
                        {
                            'movieId': row['movieId'],
                            'title': row['title'],
                            'genres':row['genres'].split('|')
                        }
                    )
        except FileNotFoundError:
            print(f"File {self.path_to_the_file} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def dist_by_release(self):
        """
        Метод возвращает словарь или OrderedDict, где ключи — это годы, а значения — это количества.
        Вам нужно извлечь годы из названий. Отсортируйте его по количеству по убыванию.
        """
        release_years = defaultdict(int)
        
        for movie in self.movies :
            title = movie['title']
            if '(' in title and ')' in title:
                year = title.split('(')[-1].split(')')[0]
                if year.isdigit():
                    release_years[year] += 1
        
        release_years = OrderedDict(sorted(release_years.items(), key=lambda item: item[1], reverse=True))
        release_years = OrderedDict((int(key), value) for key, value in release_years.items())
            
        return release_years
    
    def dist_by_genres(self):
        """
        Метод возвращает словарь, где ключи — это жанры, а значения — это количества.
        Отсортируйте его по количеству по убыванию.
        """
        genres = defaultdict(int)
        
        for movie in self.movies :
            genre_list = movie['genres']
            for genre in genre_list:
                genres[genre] += 1
        
        genres = OrderedDict(sorted(genres.items(), key=lambda item: item[1], reverse=True))

        return genres
        
    def most_genres(self, n):
        """
        Метод возвращает словарь с n лучшими фильмами, где ключи — это названия фильмов, 
        а значения — это количество жанров фильма. Сортировать по номерам в порядке убывания.
        """
        movies = defaultdict(int)
        for movie in self.movies:
            title = movie['title']
            genre_list = [g for g in movie['genres'] if g != '(no genres listed)']
            movies[title] = len(genre_list)

        movies = OrderedDict(sorted(movies.items(), key=lambda item: item[1], reverse=True))
        movies = dict(list(movies.items())[:n])
        return movies    

class Ratings:

    def __init__(self, path_to_the_file_ratings, path_to_the_file_movies, limit=1000):

        self.ratings = []
        self.movies = {}  
        self.path_to_the_file_ratings = path_to_the_file_ratings
        self.path_to_the_file_movies = path_to_the_file_movies 
        self.movie_ratings = defaultdict(list)
        self.user_ratings = defaultdict(list)
        self.load_movies()  
        self.data_load(limit)
        self.Movies = self.Movies(self.movie_ratings, self.movies) 
        self.users = self.Users(self.user_ratings)
    
    def load_movies(self):
        """Загружает данные о фильмах из CSV файла."""
        try:
            with open(self.path_to_the_file_movies, mode='r', encoding='UTF-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    movie_id = int(row['movieId'])
                    title = row['title']
                    genres = row['genres']
                    self.movies[movie_id] = {'title': title, 'genres': genres}
        except FileNotFoundError:
            print(f"File {self.path_to_the_file_movies} not found.")
        except Exception as e:
            print(f"An error occurred while loading movies: {e}")

    def data_load(self, limit):
        try:
            with open(self.path_to_the_file_ratings, mode='r', encoding='UTF-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    rating = {
                        'userId': int(row['userId']),
                        'movieId': int(row['movieId']),
                        'rating': float(row['rating']),
                        'timestamp': int(row['timestamp'])
                    }
                    self.ratings.append(rating)
                    self.movie_ratings[rating['movieId']].append((rating['rating'], datetime.fromtimestamp(rating['timestamp'])))
                    self.user_ratings[rating['userId']].append((rating['rating'], datetime.fromtimestamp(rating['timestamp'])))
        except FileNotFoundError:
            print(f"File {self.path_to_the_file} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    class Movies:   
        def __init__(self, movie_ratings, movies):
            self.movie_ratings = movie_ratings
            self.movies = movies 

        def get_movie_title(self, movie_id):
            """Возвращает название фильма по его ID."""
            if movie_id in self.movies:
                return self.movies[movie_id]['title']
            else:
                return f"Movie ID {movie_id} not found"
        
        def dist_by_year(self):
            """
            Метод возвращает словарь, где ключи — это годы, а значения — это счетчики.
            Сортируйте его по годам по возрастанию. Вам нужно извлечь годы из временных меток.
            """
            year_counts = defaultdict(int)
            for movie_id, ratings in self.movie_ratings.items():
                for rating, timestamp in ratings:
                    year_counts[timestamp.year] += 1
            
            ratings_by_year =  dict(sorted(year_counts.items()))
            return ratings_by_year
        
        def dist_by_rating(self):
            """
            Метод возвращает словарь, где ключами являются рейтинги, а значениями — количества.

            Сортировать его по возрастанию рейтингов.
            """
            rating_counts = defaultdict(int)
            for movie_id, ratings in self.movie_ratings.items():
                for rating, _ in ratings:
                    rating_counts[rating] += 1
            
            ratings_distribution =  dict(sorted(rating_counts.items()))
            return ratings_distribution
        
        def top_by_num_of_ratings(self, n):
            """
            Метод возвращает n лучших фильмов по количеству оценок.
            Это словарь, где ключами являются названия фильмов, а значениями — числа.

            Сортировать по числам по убыванию.
            """
            movie_counts = {
                movie_id: len(ratings)
                for movie_id, ratings in self.movie_ratings.items()
            }
            
            top_movies =  dict(sorted((movie_counts.items()), key=lambda x: x[1], reverse=True)[:n])
            return top_movies
        
        def calculate_average(self, values):
            if values:
                average = round(sum(values) / len(values), 2)
            else:
                average = 0
            return average
        
        def calculate_median(self, values):
            sorted_values = sorted(values)
            length = len(sorted_values)
            if length == 0:
                median = 0
            elif length % 2 == 1:
                median = round(sorted_values[length // 2], 2)
            else:
                median = round((sorted_values[length // 2 - 1] + sorted_values[length // 2]) / 2, 2) 
            return median
        
        def calculate_variance(self, values):
            if len(values) < 2:
                variance = 0
            else:
                average = self.calculate_average(values)
                variance = sum((x - average) ** 2 for x in values) / len(values)
            return round(float(variance), 2)

        def top_by_ratings(self, n, metric='average'):
            """
            Метод возвращает n лучших фильмов по среднему или медианному значению оценок.
            Это словарь, где ключами являются названия фильмов, а значениями — значения метрик.
            Сортируйте его по метрике по убыванию.
            Значения следует округлить до 2 десятичных знаков.
            """
            movie_stats = {}
    
            for movie_id, ratings in self.movie_ratings.items():
                rating_values = [r for r, _ in ratings]

                if len(rating_values) == 0:
                    continue
                    
                if metric == 'average':
                    value = self.calculate_average(rating_values)
                elif metric == 'median':
                    value = self.calculate_median(rating_values)
                else:
                    raise ValueError("metric must be 'average' or 'median'")
                
                movie_stats[movie_id] = value

            top_movies = dict(sorted(movie_stats.items(),key=lambda x: x[1],reverse=True)[:n])

            return top_movies
        
        def top_controversial(self, n):
            """
            Метод возвращает n лучших фильмов по дисперсии оценок.
            Это словарь, где ключами являются названия фильмов, а значениями — дисперсии.
            Сортируйте его по убыванию дисперсии.
            Значения должны быть округлены до 2 десятичных знаков.
            """
            movie_vars = {}
    
            for movie_id, ratings in self.movie_ratings.items():
                rating_values = [r for r, _ in ratings]
                variance = self.calculate_variance(rating_values)
                movie_vars[movie_id] = variance

            top_movies = dict(sorted(movie_vars.items(),key=lambda x: x[1], reverse=True)[:n])
            
            return top_movies


    class Users(Movies):
        """
        В этом классе должны работать три метода.
        Первый возвращает распределение пользователей по количеству оценок, сделанных ими.
        Второй возвращает распределение пользователей по средним или медианным оценкам, сделанным ими.
        Третий возвращает n лучших пользователей с самой большой дисперсией их оценок.
        Наследуется от класса Фильмы. Несколько методов похожи на методы из него.
        """
        def __init__(self, user_ratings):
            self.user_ratings = user_ratings

        def rating_counts_distribution(self,n):
            user_counts = {user_id: len(ratings) for user_id, ratings in self.user_ratings.items()}
            return dict(sorted(user_counts.items(), key=lambda x: -x[1])[:n])
        

        def rating_stats_distribution(self, n,metric='average'):
            dist = {}
            for user_id,ratings in self.user_ratings.items():
                values = [r for r, _ in ratings]
                if not values:
                    continue
                if metric == 'average':
                    value = self.calculate_average(values)
                elif metric == 'median':
                    value = self.calculate_median(values)
                else:
                    raise ValueError("metric must be 'average' or 'median'")
                dist[user_id] = value
            return dict(sorted(dist.items(),key=lambda x: -x[1])[:n])

        def top_by_variance(self, n):
            user_vars = {}
            for user_id, ratings in self.user_ratings.items():
                values = [r for r, _ in ratings]
                if len(values) < 2:
                    continue
                variance = self.calculate_variance(values)
                user_vars[user_id] = variance
            return OrderedDict(sorted(user_vars.items(), key=lambda x: -x[1])[:n])


class Links:
    def __init__(self, path_to_the_file):
        '''Инициализирует класс Links, загружает данные и кэш.'''
        self.path_to_the_file = path_to_the_file
        self.links = []
        self.movieId_to_imdbId = {}
        self.imdb_data_cache = {}
        self.cache_filepath = "imdb_data_cache.json"
        self.data_load()
        self._load_cache_from_json()

    def data_load(self):
        '''Загружает данные из CSV файла links.csv.'''
        try:
            with open(self.path_to_the_file, mode='r', encoding='UTF-8') as file:
                reader = csv.DictReader(file, delimiter=',', quotechar='"')
                for row in reader:
                    link_data = {
                        'movieId': row['movieId'],
                        'imdbId': row['imdbId'],
                        'tmdbId': row['tmdbId']
                    }
                    self.links.append(link_data)
                    self.movieId_to_imdbId[row['movieId']] = row['imdbId']

        except FileNotFoundError:
            print(f"Ошибка: Файл {self.path_to_the_file} не найден.")
            self.links = []
            self.movieId_to_imdbId = {}

        except Exception as e:
            print(f"Произошла ошибка при загрузке данных: {e}")
            self.links = []
            self.movieId_to_imdbId = {}

    def _load_cache_from_json(self):
        '''Загружает кэш из JSON файла при инициализации.'''
        if os.path.exists(self.cache_filepath):
            try:
                with open(self.cache_filepath, 'r', encoding='utf-8') as f:
                    self.imdb_data_cache = json.load(f)
            except json.JSONDecodeError:
                print(f"Ошибка чтения кэш-файла {self.cache_filepath}. Кэш будет создан заново.")
                self.imdb_data_cache = {}
            except Exception as e:
                print(f"Ошибка при загрузке кэша из файла {self.cache_filepath}: {e}")
                self.imdb_data_cache = {}
        else:
            self.imdb_data_cache = {}


    def _save_cache_to_json(self):
        '''Сохраняет кэш в JSON файл.'''
        try:
            with open(self.cache_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.imdb_data_cache, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении кэша в файл {self.cache_filepath}: {e}")


    def _safe_extract_text(self, element):
        '''Безопасно извлекает текст из элемента BeautifulSoup.'''
        return element.get_text(strip=True) if element else None

    def _parse_director(self, soup):
        """Извлекает имя(имена) режиссера со страницы."""
        director_elements = soup.select('li[data-testid="title-pc-principal-credit"]:has(a[href*="dr_"]) a')
        if not director_elements:
            print("Режиссеры не найдены с использованием селектора 'li[data-testid=\"title-pc-principal-credit\"]:has(a[href*=\"dr_\"]) a'") # Отладочное сообщение
            return None

        seen_directors = set()
        director_names = []

        for a in director_elements:
            name = self._safe_extract_text(a)
            if name and name not in seen_directors:
                director_names.append(name)
                seen_directors.add(name)

        return ', '.join(director_names) if director_names else None


    def _parse_generic_boxoffice(self, soup, testid):
         '''Извлекает значения Box Office (бюджет, сборы) по testid.'''
         section = soup.find('li', {'data-testid': testid})
         if not section:
             return None

         value_element = section.find('span', class_='ipc-metadata-list-item__list-content-item')
         if not value_element:
             value_element = section.find('div', class_='ipc-metadata-list-item__content-container')
         return self._safe_extract_text(value_element)

    def _parse_runtime(self, soup):
        '''Извлекает продолжительность фильма со страницы.'''
        runtime_section = soup.find('li', {'data-testid': 'title-techspec_runtime'})
        if not runtime_section:
            return None

        value_div = runtime_section.find('div', class_='ipc-metadata-list-item__content-container')
        return self._safe_extract_text(value_div)

    def _parse_title(self, soup):
        '''Извлекает название фильма.'''
        title_element = soup.select_one('h1[data-testid="hero__pageTitle"]')
        return self._safe_extract_text(title_element)

    def _parse_imdb_page(self, soup, field):
        '''Диспетчер парсинга для разных полей.'''
        try:
            if field == 'Director':
                return self._parse_director(soup)
            elif field == 'Budget':
                return self._parse_generic_boxoffice(soup, 'title-boxoffice-budget')
            elif field == 'Cumulative Worldwide Gross':
                return self._parse_generic_boxoffice(soup, 'title-boxoffice-cumulativeworldwidegross')
            elif field == 'Runtime':
                runtime_str = self._parse_runtime(soup)
                return runtime_str
            elif field == 'Title':
                return self._parse_title(soup)
            else:
                return None
        except Exception as e:
            return None

    def _generate_cache_filename(self, movie_ids, fields):
        '''Генерирует имя файла кэша.'''
        filename = "imdb_data_cache.json"
        return filename

    def get_imdb(self, list_of_movies, list_of_fields, use_cache=True, force_fetch=False):
        '''Возвращает словарь {movieId: {field: value, ...}} для заданных фильмов.'''
        imdb_info = {}
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        session.headers.update(headers)
        processed_movie_ids = set()

        for movie_id in list_of_movies:
            if movie_id in processed_movie_ids:
                continue
            processed_movie_ids.add(movie_id)

            if use_cache and not force_fetch and movie_id in self.imdb_data_cache:
                imdb_info[movie_id] = self.imdb_data_cache[movie_id]
                continue

            imdb_id = self.movieId_to_imdbId.get(movie_id)
            if not imdb_id:
                print(f"Предупреждение: IMDB ID не найден для movieId {movie_id}. Пропускается.")
                continue

            imdb_id_formatted = f"tt{imdb_id.zfill(7)}" if not imdb_id.startswith('tt') else imdb_id
            url = f"https://www.imdb.com/title/{imdb_id_formatted}/"

            try:
                response = session.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')

                field_data_dict = {}
                for field in list_of_fields:
                    parsed_value = self._parse_imdb_page(soup, field)
                    field_data_dict[field] = parsed_value

                imdb_info[movie_id] = field_data_dict
                self.imdb_data_cache[movie_id] = field_data_dict
                time.sleep(1.2)

            except requests.exceptions.Timeout:
                 print(f"Ошибка: Таймаут при запросе {url} для movieId {movie_id}")
                 field_data_dict = {field: "Ошибка: Таймаут" for field in list_of_fields}
                 imdb_info[movie_id] = field_data_dict
                 self.imdb_data_cache[movie_id] = field_data_dict


            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе {url} для movieId {movie_id}: {e}")
                field_data_dict = {field: f"Ошибка сети: {e}" for field in list_of_fields}
                imdb_info[movie_id] = field_data_dict
                self.imdb_data_cache[movie_id] = field_data_dict

            except Exception as e:
                print(f"Неожиданная ошибка для movieId {movie_id}: {e}")
                field_data_dict = {field: f"Ошибка обработки: {e}" for field in list_of_fields}
                imdb_info[movie_id] = field_data_dict
                self.imdb_data_cache[movie_id] = field_data_dict


        if use_cache and force_fetch:
            self._save_cache_to_json()
        elif use_cache and not force_fetch and not os.path.exists(self.cache_filepath):
            self._save_cache_to_json()

        return imdb_info

    def fetch_initial_data(self, movie_ids, fields):
        '''Предварительно загружает данные для movie_ids и сохраняет в кэш.'''
        self.get_imdb(movie_ids, fields, use_cache=True, force_fetch=True)


    def top_directors(self, n, process_limit=100):
        '''Возвращает топ-N режиссеров по количеству фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить топ режиссеров.")
            return {}

        actual_limit = min(process_limit, len(all_movie_ids))
        movie_ids_to_process = all_movie_ids[:actual_limit]
        director_counts = Counter()

        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Director' not in movie_data or not movie_data['Director']:
                continue

            director_string = movie_data['Director']

            if isinstance(director_string, str) and director_string.startswith("Ошибка:"):
                continue
            directors = [d.strip() for d in director_string.split(',')]
            for director in directors:
                if director:
                    director_counts[director] += 1

        top_n_list = director_counts.most_common(n)
        top_directors_dict = dict(top_n_list)
        return top_directors_dict


    def _parse_budget_string(self, budget_str):
        '''Преобразует строку бюджета в числовое значение (int).'''
        if not budget_str or not isinstance(budget_str, str):
            return None

        cleaned_str = re.sub(r'[$,€£\s]|(GBP)|(USD)|(EUR)|(CAD)|(AUD)|(NZD)|(CHF)|(CNY)|(JPY)|(KRW)|(RUB)|[,\s]\(.*\)', '', budget_str, flags=re.IGNORECASE).strip()
        numeric_part = ''.join(re.findall(r'\d', cleaned_str))

        if not numeric_part:
            return None

        try:
            return int(numeric_part)
        except ValueError:
            return None


    def most_expensive(self, n, process_limit=1000):
        '''Возвращает словарь топ-N самых дорогих фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_budgets = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Budget' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            budget_str = movie_data['Budget']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                 continue
            if budget_str is None or isinstance(budget_str, str) and budget_str.startswith("Ошибка:"):
                continue

            budget_num = self._parse_budget_string(budget_str)
            if budget_num is not None and title:
                 movies_with_budgets.append((title, budget_num))

        movies_with_budgets.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_budgets[:n]
        budgets = dict(top_n_movies)
        return budgets


    def most_profitable(self, n, process_limit=1000):
        '''Возвращает словарь топ-N самых прибыльных фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить самые прибыльные фильмы.")
            return {}

        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_profits = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Budget' not in movie_data or 'Cumulative Worldwide Gross' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            budget_str = movie_data['Budget']
            gross_str = movie_data['Cumulative Worldwide Gross']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                continue
            if budget_str is None or isinstance(budget_str, str) and budget_str.startswith("Ошибка:"):
                continue
            if gross_str is None or isinstance(gross_str, str) and gross_str.startswith("Ошибка:"):
                continue

            budget_num = self._parse_budget_string(budget_str)
            gross_num = self._parse_budget_string(gross_str)

            if budget_num is not None and gross_num is not None and title:
                profit = gross_num - budget_num
                movies_with_profits.append((title, profit))

        if not movies_with_profits:
            print("Не найдено фильмов с корректно извлеченными бюджетами и сборами.")
            return {}

        movies_with_profits.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_profits[:n]
        profits = dict(top_n_movies)
        return profits

    def _parse_runtime_minutes(self, runtime_str):
        '''Преобразует строку продолжительности в минуты (int).'''
        if not runtime_str or not isinstance(runtime_str, str):
            return None

        runtime_str = runtime_str.lower().replace('мин', 'minutes').replace('ч', 'hours').strip()
        total_minutes = 0
        try:
            hours_match = re.search(r'(\d+)(?:hours|h)', runtime_str)
            minutes_match = re.search(r'(\d+)(?:minutes|min)', runtime_str)

            hours = int(hours_match.group(1)) if hours_match else 0
            minutes = int(minutes_match.group(1)) if minutes_match else 0

            if not hours_match and not minutes_match:
                return None

            total_minutes = hours * 60 + minutes

        except (AttributeError, ValueError):
            return None

        return total_minutes

    def longest(self, n, process_limit=1000):
        '''Возвращает словарь топ-N самых длинных фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить самые длинные фильмы.")
            return {}

        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_runtimes = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Runtime' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            runtime_str = movie_data['Runtime']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                continue
            if runtime_str is None or isinstance(runtime_str, str) and runtime_str.startswith("Ошибка:"):
                continue

            runtime_minutes = self._parse_runtime_minutes(runtime_str)

            if runtime_minutes is not None and title:
                movies_with_runtimes.append((title, runtime_minutes))

        if not movies_with_runtimes:
            print("Не найдено фильмов с корректно извлеченной продолжительностью.")
            return {}

        movies_with_runtimes.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_runtimes[:n]
        runtimes = dict(top_n_movies)
        return runtimes


    def top_cost_per_minute(self, n, process_limit=1000):
        '''Возвращает словарь топ-N фильмов с самой высокой стоимостью минуты, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить стоимость минуты.")
            return {}

        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_costs = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Budget' not in movie_data or 'Runtime' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            budget_str = movie_data['Budget']
            runtime_str = movie_data['Runtime']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                continue
            if budget_str is None or isinstance(budget_str, str) and budget_str.startswith("Ошибка:"):
                continue
            if runtime_str is None or isinstance(runtime_str, str) and runtime_str.startswith("Ошибка:"):
                continue

            budget_num = self._parse_budget_string(budget_str)
            runtime_minutes = self._parse_runtime_minutes(runtime_str)

            if budget_num is not None and runtime_minutes is not None and runtime_minutes > 0 and title:
                cost_per_minute = budget_num / runtime_minutes
                movies_with_costs.append((title, cost_per_minute))

        if not movies_with_costs:
            print("Не найдено фильмов с корректно извлеченными бюджетами и продолжительностью.")
            return {}

        movies_with_costs.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_costs[:n]
        costs = {title: round(cost, 2) for title, cost in top_n_movies}
        return costs


class Tags:

    def __init__(self, path_to_the_file):

        self.path_to_the_file = path_to_the_file
        self.tags = []
        self.data_load()

    def data_load(self):
        try :
            with open(self.path_to_the_file, mode ='r', encoding = 'UTF-8') as file:
                reader = csv.DictReader(file, delimiter=',', quotechar='"')
                for row in reader:
                    self.tags.append(
                        {
                            'userId': row['userId'],
                            'movieId': row['movieId'],
                            'tag': row['tag'],
                            'timestamp':row['timestamp']
                        }
                    )
        except FileNotFoundError:
            print(f"File {self.path_to_the_file} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")  
    

    def most_words(self, n):
        """
        Метод возвращает теги с наибольшим количеством слов внутри. Это dict 
        где ключами являются теги, а значениями - количество слов внутри тега.
        Удалите дубликаты. Отсортируйте их по убыванию чисел.
        """
        tag_word_counts = defaultdict(int)
        unique_tags = set()

        for tag_data in self.tags:
            tag = tag_data['tag']

            if tag not in unique_tags:
                unique_tags.add(tag)
                word_count = len(tag.split())
                tag_word_counts[tag] = word_count


        sorted_tags = sorted(tag_word_counts.items(), key=lambda item: item[1], reverse=True)
        top_tags = dict(sorted_tags[:n])

        return top_tags

    def longest(self, n):
        """
        Метод возвращает n самых длинных тегов по количеству символов.
        Это список тегов. Удалите дубликаты. Отсортируйте его по номерам в порядке убывания.
        """
        tag_lengths = {}
        unique_tags = set()

        for tag_data in self.tags:
            tag = tag_data['tag']
        
            if tag not in unique_tags:
                unique_tags.add(tag)
                tag_lengths[tag] = len(tag)
        
        sorted_tags = sorted(tag_lengths.items(), key=lambda item: item[1], reverse=True)
        top_tags = [tag for tag, length in sorted_tags[:n]]
        return top_tags

    def most_words_and_longest(self, n):
        """
        Метод возвращает пересечение между тегами с наибольшим количеством слов внутри и
        тегами с наибольшей длиной по количеству символов.
        Удалите дубликаты. Это список тегов.
        """
        top_words_tags = set(self.most_words(n).keys())
        top_longest_tags = set(self.longest(n))
        intersection = list(top_words_tags.intersection(top_longest_tags))
        return intersection
        
    def most_popular(self, n):
        """
        Метод возвращает наиболее популярные теги. 
        Это dict, в котором ключами являются теги, а значениями - значения количества.
        Удалите дубликаты. Отсортируйте его по количеству в порядке убывания.
        """
        tag_counts = defaultdict(int)
        for tag_data in self.tags:
            tag = tag_data['tag']
            tag_counts[tag] += 1

        sorted_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
        top_tags = dict(sorted_tags[:n])
        return top_tags
        
    def tags_with(self, word):
        """
        Метод возвращает все уникальные теги, содержащие слово, указанное в качестве аргумента.
        Удалите дубликаты. Это список тегов. Отсортируйте его по названиям тегов в алфавитном порядке.
        """
        unique_tags = set()
        result = []
        
        for tag_data in self.tags:
            tag = tag_data['tag']
            if word in tag and tag not in unique_tags:
                unique_tags.add(tag)
                result.append(tag)
        result.sort()
        return result
    

TAGS_CSV_FILE = "../datasets/ml-latest-small/tags.csv"

@pytest.fixture()
def tags_instance():
    return Tags(TAGS_CSV_FILE)


class TestTagsClass:

    def test_data_load_file_not_found(self):

        non_existent_file = "non_existent_tags.csv"
        tags_instance = Tags(non_existent_file)
        assert isinstance(tags_instance.tags, list)
        assert len(tags_instance.tags) == 0


    def test_data_load_success(self, tags_instance):

        assert isinstance(tags_instance.tags, list)
        assert len(tags_instance.tags) > 0
        for item in tags_instance.tags:
            assert isinstance(item, dict)
            assert 'userId' in item
            assert 'movieId' in item
            assert 'tag' in item
            assert 'timestamp' in item
            assert isinstance(item['userId'], str)
            assert isinstance(item['movieId'], str)
            assert isinstance(item['tag'], str)
            assert isinstance(item['timestamp'], str)


    def test_most_words_returns_dict(self, tags_instance):

        result = tags_instance.most_words(2)
        assert isinstance(result, dict)


    def test_most_words_dict_key_value_types(self, tags_instance):

        result = tags_instance.most_words(2)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_most_words_sorted_descending(self, tags_instance):

        result = tags_instance.most_words(5)
        word_counts = list(result.values())
        assert all(word_counts[i] >= word_counts[i+1] for i in range(len(word_counts)-1))


    def test_longest_returns_list(self, tags_instance):

        result = tags_instance.longest(2)
        assert isinstance(result, list)


    def test_longest_sorted_descending_length(self, tags_instance):

        result = tags_instance.longest(5)
        lengths = [len(tag) for tag in result]
        assert all(lengths[i] >= lengths[i+1] for i in range(len(lengths)-1))


    def test_most_words_and_longest_returns_list(self, tags_instance):

        result = tags_instance.most_words_and_longest(2)
        assert isinstance(result, list)


    def test_most_words_and_longest_list_element_type(self, tags_instance):

        result = tags_instance.most_words_and_longest(2)
        for item in result:
            assert isinstance(item, str)


    def test_most_popular_returns_dict(self, tags_instance):

        result = tags_instance.most_popular(2)
        assert isinstance(result, dict)


    def test_most_popular_dict_key_value_types(self, tags_instance):

        result = tags_instance.most_popular(2)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_most_popular_sorted_descending(self, tags_instance):
        result = tags_instance.most_popular(5)
        counts = list(result.values())
        assert all(counts[i] >= counts[i+1] for i in range(len(counts)-1))


    def test_tags_with_returns_list(self, tags_instance):

        result = tags_instance.tags_with("comedy")
        assert isinstance(result, list)


    def test_tags_with_list_element_type(self, tags_instance):

        result = tags_instance.tags_with("comedy")
        for item in result:
            assert isinstance(item, str)


    def test_tags_with_sorted_alphabetically(self, tags_instance):

        result = tags_instance.tags_with("drama")
        if len(result) > 1:
            assert all(result[i] <= result[i+1] for i in range(len(result)-1))

LINKS_CSV_FILE = "../datasets/ml-latest-small/links.csv"


@pytest.fixture()
def links_instance():
    return Links(LINKS_CSV_FILE)

class TestLinksClass:
    def test_links_data_load_success(self, links_instance):
        """Тест загрузки данных Links."""
        assert isinstance(links_instance.links, list)
        assert len(links_instance.links) > 0

    def test_links_top_directors_returns_dict_sorted(self, links_instance):
        """Тест top_directors возвращает словарь и отсортирован."""
        result = links_instance.top_directors(3, process_limit=10)
        assert isinstance(result, dict)
        director_counts = list(result.values())
        if director_counts:
            assert all(director_counts[i] >= director_counts[i+1] for i in range(len(director_counts)-1))

    def test__parse_budget_string_success(self, links_instance):
        """Тест метода _parse_budget_string, успешное преобразование."""
        budget_str = "$123,456,789 (estimated)"
        parsed_budget = links_instance._parse_budget_string(budget_str)
        assert parsed_budget == 123456789
        assert isinstance(parsed_budget, int)

    def test__parse_runtime_minutes_success(self, links_instance):
        """Тест метода _parse_runtime_minutes, успешное преобразование."""
        runtime_str = "2hours 30minutes"
        runtime_minutes = links_instance._parse_runtime_minutes(runtime_str)
        assert runtime_minutes == 150
        assert isinstance(runtime_minutes, int)

    @patch('requests.Session.get')
    def test_get_imdb_returns_dict_of_dicts(self, mock_get, links_instance):
        """Тест get_imdb возвращает словарь словарей."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<h1 data-testid=\"hero__pageTitle\">Test Movie</h1>" 
        mock_get.return_value = mock_response

        movie_ids_to_test = ['1']
        fields_to_test = ['Title']
        result = links_instance.get_imdb(movie_ids_to_test, fields_to_test, use_cache=False)
        assert isinstance(result, dict) 
        assert '1' in result 
        movie_data = result['1']
        assert isinstance(movie_data, dict) 
        assert 'Title' in movie_data 
        assert movie_data['Title'] == 'Test Movie' 

    def test_most_expensive_returns_dict_sorted(self, links_instance):
        """Тест most_expensive возвращает словарь и отсортирован."""
        result = links_instance.most_expensive(2, process_limit=5)
        assert isinstance(result, dict)
        budgets = list(result.values())
        if budgets:
            assert all(budgets[i] >= budgets[i+1] for i in range(len(budgets)-1))

    def test_most_profitable_returns_dict_sorted(self, links_instance):
        """Тест most_profitable возвращает словарь и отсортирован."""
        result = links_instance.most_profitable(2, process_limit=5)
        assert isinstance(result, dict)
        profits = list(result.values())
        if profits:
            assert all(profits[i] >= profits[i+1] for i in range(len(profits)-1))

    def test_longest_returns_dict_sorted(self, links_instance):
        """Тест longest возвращает словарь и отсортирован."""
        result = links_instance.longest(2, process_limit=5)
        assert isinstance(result, dict)
        runtimes = list(result.values())
        if runtimes:
            assert all(runtimes[i] >= runtimes[i+1] for i in range(len(runtimes)-1))

    def test_top_cost_per_minute_returns_dict_sorted(self, links_instance):
        """Тест top_cost_per_minute возвращает словарь и отсортирован."""
        result = links_instance.top_cost_per_minute(2, process_limit=5)
        assert isinstance(result, dict)
        costs = list(result.values())
        if costs:
            assert all(costs[i] >= costs[i+1] for i in range(len(costs)-1))


MOVIE_CSV_FILE = '../ml-latest-small/datasets/movies.csv'


@pytest.fixture
def movies_instance():
    return Movies(MOVIE_CSV_FILE)

class TestMovies:

    def test_data_load(self, movies_instance):
        assert isinstance(movies_instance.movies, list), "Movies data should be a list."
        if movies_instance.movies:
            first_movie = movies_instance.movies[0]
            assert isinstance(first_movie, dict), "Each movie should be a dictionary."
            assert 'movieId' in first_movie and 'title' in first_movie and 'genres' in first_movie, "Dictionary keys are incorrect."
            assert isinstance(first_movie['genres'], list), "Genres should be a list."

    def test_dist_by_release(self, movies_instance):
        """Тестирует метод dist_by_release."""
        release_years = movies_instance.dist_by_release()
        assert isinstance(release_years, OrderedDict), "Should return an OrderedDict."
        if release_years:
            first_key = next(iter(release_years))
            first_value = release_years[first_key]
            assert isinstance(first_key, int), "Keys should be integers (years)."
            assert isinstance(first_value, int), "Values should be integers (counts)."

        values = list(release_years.values())
        for i in range(len(values) - 1):
            assert values[i] >= values[i+1], "Should be sorted in descending order by count."

    def test_dist_by_genres(self, movies_instance):
        """Тестирует метод dist_by_genres."""
        genres = movies_instance.dist_by_genres()
        assert isinstance(genres, OrderedDict), "Should return an OrderedDict."
        if genres:
            first_key = next(iter(genres))
            first_value = genres[first_key]
            assert isinstance(first_key, str), "Keys should be strings (genres)."
            assert isinstance(first_value, int), "Values should be integers (counts)."

        values = list(genres.values())
        for i in range(len(values) - 1):
            assert values[i] >= values[i+1], "Should be sorted in descending order by count."

    def test_most_genres(self, movies_instance):
        """Тестирует метод most_genres."""
        n = 2 
        top_movies = movies_instance.most_genres(n)
        assert isinstance(top_movies, dict), "Should return a dictionary."
        assert len(top_movies) <= n, f"Should return at most {n} items."

        if top_movies:
            first_key = next(iter(top_movies))
            first_value = top_movies[first_key]
            assert isinstance(first_key, str), "Keys should be strings (movie titles)."
            assert isinstance(first_value, int), "Values should be integers (genre counts)."

        values = list(top_movies.values())
        for i in range(len(values) - 1):
           pass


TEST_RATINGS_FILE = '../datasets/ml-latest-small/ratings.csv'
path_to_movies = '../datasets/ml-latest-small/movies.csv'
@pytest.fixture
def ratings_instance():
    """Создает экземпляр класса Ratings для каждого теста."""
    return Ratings(TEST_RATINGS_FILE, path_to_movies, limit=100)


class TestRatings:

    def test_data_load(self, ratings_instance):
        """Тестирует метод data_load."""
        assert isinstance(ratings_instance.ratings, list), "Ratings data should be a list."
        if ratings_instance.ratings:
            first_rating = ratings_instance.ratings[0]
            assert isinstance(first_rating, dict), "Each rating should be a dictionary."
            assert 'userId' in first_rating and 'movieId' in first_rating and 'rating' in first_rating and 'timestamp' in first_rating, "Dictionary keys are incorrect."
            assert isinstance(first_rating['userId'], int), "userId should be an integer."
            assert isinstance(first_rating['movieId'], int), "movieId should be an integer."
            assert isinstance(first_rating['rating'], float), "rating should be a float."
            assert isinstance(first_rating['timestamp'], int), "timestamp should be an integer."

        assert isinstance(ratings_instance.movie_ratings, defaultdict), "movie_ratings should be a defaultdict."
        if ratings_instance.movie_ratings:
            movie_id = next(iter(ratings_instance.movie_ratings))
            ratings_list = ratings_instance.movie_ratings[movie_id]
            assert isinstance(ratings_list, list), "movie_ratings values should be lists."
            if ratings_list:
                rating, timestamp = ratings_list[0]
                assert isinstance(rating, float), "Rating in movie_ratings should be a float."
                assert isinstance(timestamp, datetime), "Timestamp in movie_ratings should be a datetime object."

        assert isinstance(ratings_instance.user_ratings, defaultdict), "user_ratings should be a defaultdict."
        if ratings_instance.user_ratings:
            user_id = next(iter(ratings_instance.user_ratings))
            ratings_list = ratings_instance.user_ratings[user_id]
            assert isinstance(ratings_list, list), "user_ratings values should be lists."
            if ratings_list:
                rating, timestamp = ratings_list[0]
                assert isinstance(rating, float), "Rating in user_ratings should be a float."
                assert isinstance(timestamp, datetime), "Timestamp in user_ratings should be a datetime object."

    def test_load_movies(self, ratings_instance):
        """Тестирует метод load_movies."""
        assert isinstance(ratings_instance.movies, dict), "movies should be a dictionary."
        if ratings_instance.movies:
            movie_id = next(iter(ratings_instance.movies))
            movie_info = ratings_instance.movies[movie_id]
            assert isinstance(movie_info, dict), "movie_info should be a dictionary."
            assert 'title' in movie_info and 'genres' in movie_info, "movie_info keys are incorrect."
            assert isinstance(movie_info['title'], str), "title should be a string."
            assert isinstance(movie_info['genres'], str), "genres should be a string."

class Test_Rat_Movies:

    @pytest.fixture
    def movies_instance(self, ratings_instance):
        """Создает экземпляр вложенного класса Movies для каждого теста."""
        return ratings_instance.Movies

    def test_dist_by_year(self, movies_instance):
        """Тестирует метод dist_by_year."""
        year_distribution = movies_instance.dist_by_year()
        assert isinstance(year_distribution, dict), "Should return a dictionary."
        if year_distribution:
            first_year = next(iter(year_distribution))
            first_count = year_distribution[first_year]
            assert isinstance(first_year, int), "Keys should be integers (years)."
            assert isinstance(first_count, int), "Values should be integers (counts)."

        years = list(year_distribution.keys())
        for i in range(len(years) - 1):
            assert years[i] <= years[i+1], "Should be sorted in ascending order by year."

    def test_dist_by_rating(self, movies_instance):
        """Тестирует метод dist_by_rating."""
        rating_distribution = movies_instance.dist_by_rating()
        assert isinstance(rating_distribution, dict), "Should return a dictionary."
        if rating_distribution:
            first_rating = next(iter(rating_distribution))
            first_count = rating_distribution[first_rating]
            assert isinstance(first_rating, float), "Keys should be floats (ratings)."
            assert isinstance(first_count, int), "Values should be integers (counts)."

        ratings = list(rating_distribution.keys())
        for i in range(len(ratings) - 1):
            assert ratings[i] <= ratings[i+1], "Should be sorted in ascending order by rating."

    def test_top_by_num_of_ratings(self, movies_instance, ratings_instance):
        """Тестирует метод top_by_num_of_ratings."""
        n = 3

        top_movies = {ratings_instance.Movies.get_movie_title(movie_id): count for movie_id, count in movies_instance.top_by_num_of_ratings(n).items()}
        assert isinstance(top_movies, dict), "Should return a dictionary."
        assert len(top_movies) <= n, f"Should return at most {n} items."

        if top_movies:
            first_movie_title = next(iter(top_movies))
            first_count = top_movies[first_movie_title]
            assert isinstance(first_movie_title, str), "Keys should be strings (movie titles)."
            assert isinstance(first_count, int), "Values should be integers (counts)."

            found = False
            for movie_id, info in ratings_instance.movies.items():
                if info['title'] == first_movie_title:
                    found = True
                    break
            assert found, f"Movie title '{first_movie_title}' не найден в ratings_instance.movies."

        counts = list(top_movies.values())
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i+1], "Should be sorted in descending order by count."

    def test_calculate_average(self, movies_instance):
        """Тестирует метод calculate_average."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        average = movies_instance.calculate_average(values)
        assert isinstance(average, float), "Should return a float."
        assert average == 3.0, "Average calculation is incorrect."
        empty_average = movies_instance.calculate_average([])
        assert empty_average == 0, "Average of empty list should be 0."

    def test_calculate_median(self, movies_instance):
        """Тестирует метод calculate_median."""
        values_odd = [1.0, 2.0, 3.0, 4.0, 5.0]
        median_odd = movies_instance.calculate_median(values_odd)
        assert isinstance(median_odd, float), "Should return a float."
        assert median_odd == 3.0, "Median calculation (odd) is incorrect."

        values_even = [1.0, 2.0, 3.0, 4.0]
        median_even = movies_instance.calculate_median(values_even)
        assert median_even == 2.5, "Median calculation (even) is incorrect."

        empty_median = movies_instance.calculate_median([])
        assert empty_median == 0, "Median of empty list should be 0."

    def test_calculate_variance(self, movies_instance):
        """Тестирует метод calculate_variance."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        variance = movies_instance.calculate_variance(values)
        assert isinstance(variance, float), "Should return a float."
        assert variance == 2.0, "Variance calculation is incorrect."
        variance_one_value = movies_instance.calculate_variance([1.0])
        assert variance_one_value == 0, "Variance of one value list should be 0."

    def test_top_by_ratings(self, movies_instance, ratings_instance):
        """Тестирует метод top_by_ratings."""
        n = 2

        top_average =  {ratings_instance.Movies.get_movie_title(movie_id):rating for movie_id,rating in movies_instance.top_by_ratings(n, metric='average').items()}
        assert isinstance(top_average, dict), "Should return a dictionary."
        assert len(top_average) <= n, f"Should return at most {n} items."

        if top_average:
            movie_title = next(iter(top_average))  
            rating = top_average[movie_title]
            assert isinstance(movie_title, str), "Keys should be strings (movie titles)."
            assert isinstance(rating, float), "Values should be floats (ratings)."
 
            found = False
            for movie_id, info in ratings_instance.movies.items():
                if info['title'] == movie_title:
                    found = True
                    break
            assert found, f"Movie title '{movie_title}' не найден в ratings_instance.movies."


    def test_top_controversial(self, movies_instance, ratings_instance):
        """Тестирует метод top_controversial."""
        n = 2

        top_controversial = {ratings_instance.Movies.get_movie_title(movie_id):variance for movie_id,variance in movies_instance.top_controversial(n).items()}
        assert isinstance(top_controversial, dict), "Should return a dictionary."
        assert len(top_controversial) <= n, f"Should return at most {n} items."

        if top_controversial:
            movie_title = next(iter(top_controversial))  
            variance = top_controversial[movie_title]
            assert isinstance(movie_title, str), "Keys should be strings (movie titles)."
            assert isinstance(variance, float), "Values should be floats (variances)."

            found = False
            for movie_id, info in ratings_instance.movies.items():
                if info['title'] == movie_title:
                    found = True
                    break
            assert found, f"Movie title '{movie_title}' не найден в ratings_instance.movies."

        variances = list(top_controversial.values())
        for i in range(len(variances) - 1):
            assert variances[i] >= variances[i + 1], "Should be sorted in descending order."

    def test_get_movie_title(self, movies_instance, ratings_instance):
        """Тестирует метод get_movie_title."""

        if ratings_instance.movies:  
            movie_id = next(iter(ratings_instance.movies))
            expected_title = ratings_instance.movies[movie_id]['title']
            actual_title = movies_instance.get_movie_title(movie_id)
            assert actual_title == expected_title, "Should return the correct movie title."

            non_existent_movie_id = -1
            expected_error_message = f"Movie ID {non_existent_movie_id} not found"
            actual_error_message = movies_instance.get_movie_title(non_existent_movie_id)
            assert actual_error_message == expected_error_message, "Should return the error message for non-existent movie ID."
        else:
            pytest.skip("No movies loaded, skipping test.")



class Test_Rat_Users:
    @pytest.fixture
    def users_instance(self, ratings_instance):
        """Создает экземпляр вложенного класса Users для каждого теста."""
        return ratings_instance.users

    def test_rating_counts_distribution(self, users_instance):
        """Тестирует метод rating_counts_distribution."""
        n = 3
        distribution = users_instance.rating_counts_distribution(n)
        assert isinstance(distribution, dict), "Should return a dictionary."
        assert len(distribution) <= n, f"Should return at most {n} items."

        if distribution:
            user_id = next(iter(distribution))
            count = distribution[user_id]
            assert isinstance(user_id, int), "Keys should be integers (user IDs)."
            assert isinstance(count, int), "Values should be integers (counts)."

        counts = list(distribution.values())
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i + 1], "Should be sorted in descending order."

    def test_rating_stats_distribution(self, users_instance):
        """Тестирует метод rating_stats_distribution."""
        n = 2
        distribution = users_instance.rating_stats_distribution(n)
        assert isinstance(distribution, dict), "Should return a dictionary."
        assert len(distribution) <= n, f"Should return at most {n} items."

        if distribution:
            user_id = next(iter(distribution))
            stat = distribution[user_id]
            assert isinstance(user_id, int), "Keys should be integers (user IDs)."
            assert isinstance(stat, float), "Values should be floats (average/median)."

    def test_top_by_variance(self, users_instance):
        """Тестирует метод top_by_variance."""
        n = 2
        top_variance = users_instance.top_by_variance(n)
        assert isinstance(top_variance, OrderedDict), "Should return an OrderedDict."
        assert len(top_variance) <= n, f"Should return at most {n} items."

        if top_variance:
            user_id = next(iter(top_variance))
            variance = top_variance[user_id]
            assert isinstance(user_id, int), "Keys should be integers (user IDs)."
            assert isinstance(variance, float), "Values should be floats (variances)."

        variances = list(top_variance.values())
        for i in range(len(variances) - 1):
            assert variances[i] >= variances[i + 1], "Should be sorted in descending order."