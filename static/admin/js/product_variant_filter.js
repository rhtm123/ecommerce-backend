(function($) {
    console.log("product_variant_filter.js loaded");

    $(document).ready(function() {
        const productSelect = $('#id_product');
        const variantSelect = $('#id_variant');

        function updateVariants(productId) {
            if (!productId) return;

            const preSelected = variantSelect.data("initial"); // ✔ store initial selection

            $.ajax({
                url: window.location.origin +'/view/product/admin/get-variants/',
                data: { product_id: productId },
                success: function(data) {
                    variantSelect.empty();
                    variantSelect.append('<option value="">---------</option>');

                    data.forEach(function(variant) {
                        variantSelect.append(
                            $('<option></option>')
                                .attr('value', variant.id)
                                .text(variant.name)
                        );
                    });

                    // ✔ Restore selected option if available
                    if (preSelected) {
                        variantSelect.val(preSelected);
                    }
                }
            });
        }

        // ✔ Capture initial value from Django admin
        if (variantSelect.val()) {
            variantSelect.attr("data-initial", variantSelect.val());
        }

        // Run for edit form
        if (productSelect.val()) {
            updateVariants(productSelect.val());
        }

        // On product change
        productSelect.change(function() {
            updateVariants($(this).val());
        });
    });
})(django.jQuery);
