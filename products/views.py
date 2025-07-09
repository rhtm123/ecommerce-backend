from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Variant

@staff_member_required
def get_variants_for_product(request):
    product_id = request.GET.get('product_id')
    variants = Variant.objects.filter(product_id=product_id).values('id', 'name')
    return JsonResponse(list(variants), safe=False)

