from django.db.models import Count

from rest_framework import serializers

from product.models import (
    Product,
    ProductVariantPrice,
    ProductVariant
)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


class ProductVariantPriceSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariantPrice
        fields = (
            "id",
            "product_variant_one",
            "product_variant_two",
            "product_variant_three",
            "price",
            "stock",
            "title",
        )

    def get_title(self, obj):
        variant_list = []
        
        if obj.product_variant_one:
            variant_list.append(obj.product_variant_one.variant_title)
        if obj.product_variant_two:
            variant_list.append(obj.product_variant_two.variant_title)
        if obj.product_variant_three:
            variant_list.append(obj.product_variant_three.variant_title)

        return "/".join(variant_list) + '/'
            

class ProductDetailsSerializer(serializers.ModelSerializer):

    product_variant_prices = serializers.SerializerMethodField()
    product_variant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "title",
            "sku",
            "description",
            "product_variant_prices",
            "product_variant",
        )

    def get_product_variant_prices(self, obj):
        return ProductVariantPriceSerializer(obj.variations, many=True).data
    
    def get_product_variant(self, obj):
        context = ProductVariant.objects.filter(product__id=obj.id)
        variants = context.values("variant").annotate(Count("variant"))
        return []