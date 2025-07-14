import meilisearch
from decouple import config


client = meilisearch.Client(config("MEILISEARCH_URL"), config("MEILISEARCH_KEY"))