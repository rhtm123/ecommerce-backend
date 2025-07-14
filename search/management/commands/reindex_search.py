from django.core.management.base import BaseCommand
from search.index import index_product_listings, index_categories, index_brands

class Command(BaseCommand):
    help = "Reindex all products to Meilisearch"

    def handle(self, *args, **kwargs):
        index_product_listings()
        self.stdout.write(self.style.SUCCESS("Product listings reindexed to Meilisearch.")) 
        index_categories()
        self.stdout.write(self.style.SUCCESS("Categories reindexed to Meilisearch."))
        index_brands()
        self.stdout.write(self.style.SUCCESS("Brands reindexed to Meilisearch."))
