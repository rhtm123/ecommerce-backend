from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from products.models import ProductListing

# Define the index
product_listing_index = Index('product_listings')
product_listing_index.settings(
    number_of_shards=1,
    number_of_replicas=0
)

@registry.register_document
class ProductListingDocument(Document):
    class Index:
        name = 'product_listings'

    class Django:
        model = ProductListing
        fields = [
            'id',
            'name',
            'slug',
            'price',
            'mrp',
            'approved',
            'featured',
            'stock',
            'rating',
            'review_count',
        ]

    # For nested fields like related category or brand:
    category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'slug': fields.TextField()
    })

    brand = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField()
    })

    variant = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField()
    })

    # You can also index features or images if needed

