from django.db.models import Min, Max

def generate_category_filters(category_id):
    category = Category.objects.get(id=category_id)
    listings = ProductListing.objects.filter(
        Q(category=category) | Q(category__in=category.get_descendants())
    )
    filters = {}

    for feature in Feature.objects.filter(listing__in=listings):
        name = feature.name
        value = feature.value

        # Determine if the filter is categorical or numerical
        try:
            numerical_value = float(value)
            if name not in filters:
                filters[name] = {"type": "numerical", "values": []}
            filters[name]["values"].append(numerical_value)
        except ValueError:
            if name not in filters:
                filters[name] = {"type": "categorical", "values": set()}
            filters[name]["values"].add(value)

    # Process filters for storage and optimization
    for name, data in filters.items():
        if data["type"] == "categorical":
            filters[name]["values"] = list(data["values"])  # Convert set to list
        elif data["type"] == "numerical":
            values = data["values"]
            filters[name]["range"] = [min(values), max(values)]
            del filters[name]["values"]  # Remove raw values to save space

    # Save to the database
    category_filter, created = CategoryFilter.objects.update_or_create(
        category=category,
        defaults={"filters": filters},
    )
    return category_filter



from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductListing, Feature

@receiver([post_save, post_delete], sender=Feature)
def update_category_filters_on_feature_change(sender, instance, **kwargs):
    listing = instance.listing
    if listing and listing.category:
        generate_category_filters(listing.category.id)

@receiver([post_save, post_delete], sender=ProductListing)
def update_category_filters_on_listing_change(sender, instance, **kwargs):
    if instance.category:
        generate_category_filters(instance.category.id)
