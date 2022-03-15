import itertools

from django.shortcuts import get_object_or_404

from django.contrib import messages

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from product.models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductVariantPrice,
    Variant
)
from .serializers import (
    ProductSerializer,
    ProductDetailsSerializer,
    ProductVariantPriceSerializer
)


class CreateProductApi(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, *args, **kwargs):
        data = self.request.data
        product_images = data['product_image']
        product_variants = data['product_variant']
        product_variant_prices = data['product_variant_prices']
        tag_list = []
        new_tags = []

        serializer = ProductSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        for image in product_images:
            ProductImage.objects.create(
                product=product,
                file_path=image
            )

        for variant in product_variants:
            option = variant['option']
            tags = variant['tags']
            attribute = Variant.objects.get(pk=option)
            
            for tag in tags:
                product_variant = ProductVariant.objects.create(
                    variant_title=tag,
                    variant=attribute,
                    product=product
                )
                new_tags.append(product_variant.id)

            tag_list.append(new_tags)
            new_tags = []

        for (index, tags) in enumerate(list(itertools.product(*tag_list))):
            number_of_tags = len(tags)

            if number_of_tags == 1:
                ProductVariantPrice.objects.create(
                    product_variant_one=ProductVariant.objects.get(id=tags[0]),
                    price=float(product_variant_prices[index]['price']),
                    stock=float(product_variant_prices[index]['stock']),
                    product=product

                )
            elif number_of_tags == 2:
                ProductVariantPrice.objects.create(
                    product_variant_one=ProductVariant.objects.get(id=tags[0]),
                    product_variant_two=ProductVariant.objects.get(id=tags[1]),
                    price=float(product_variant_prices[index]['price']),
                    stock=float(product_variant_prices[index]['stock']),
                    product=product
                )
            elif number_of_tags == 3:
                ProductVariantPrice.objects.create(
                    product_variant_one=ProductVariant.objects.get(id=tags[0]),
                    product_variant_two=ProductVariant.objects.get(id=tags[1]),
                    product_variant_three=ProductVariant.objects.get(id=tags[2]),
                    price=float(product_variant_prices[index]['price']),
                    stock=float(product_variant_prices[index]['stock']),
                    product=product
                )

        messages.success(self.request, "Product has been added successfully !")
        return Response(
            {"success": True, "success_url": "/product/list/"},
            status=status.HTTP_201_CREATED
        )


class RetrieveProductApi(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, *args, **kwargs):
        queryset = get_object_or_404(Product, pk=kwargs.get('pk'))
        serializer = ProductDetailsSerializer(queryset)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class EditProductApi(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('pk'))
        data = self.request.data
        product_variant_prices = data['product_variant_prices']
        
        serializer = ProductSerializer(product, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        for variant in product_variant_prices:
            product_variant = ProductVariantPrice.objects.get(pk=variant['id'])
            product_variant.price = variant['price']
            product_variant.stock = variant['stock']
            product_variant.save()

        messages.success(self.request, "Product has been updated successfully !")
        return Response(
            {"success": True, "success_url": "/product/list/"},
            status=status.HTTP_200_OK
        )


class DeleteProductVariantPrice(generics.DestroyAPIView):

    permission_classes = [permissions.IsAuthenticated, ]

    queryset = ProductVariantPrice.objects.all()
    serializer_class = ProductVariantPriceSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Deleted"}, status=status.HTTP_200_OK)