(function($) {
    console.log("product_variant_filter.js loaded");    
    $(document).ready(function() {
        const productSelect = $('#id_product');
        const variantSelect = $('#id_variant');

        function updateVariants(productId) {
            if (!productId) return;

            $.ajax({
                url: window.location.pathname + 'get-variants/',
                data: {
                    product_id: productId
                },
                success: function(data) {
                    variantSelect.empty();
                    variantSelect.append('<option value="" selected>---------</option>');
                    data.forEach(function(variant) {
                        variantSelect.append(
                            $('<option></option>').attr('value', variant.id).text(variant.name)
                        );
                    });
                }
            });
        }

        // Trigger on page load (edit form)
        if (productSelect.val()) {
            updateVariants(productSelect.val());
        }

        // Trigger on product change
        productSelect.change(function() {
            const productId = $(this).val();
            updateVariants(productId);
        });
    });
})(django.jQuery);
