from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.recipes.models import Recipe
from apps.recipes.serializers import (
    RecipeListSerializer,
    RecipeDetailSerializer,
    RecipeCreateUpdateSerializer
)
from apps.stories.permissions import IsAdminOrReadOnly
from apps.shared.utils.custom_response import CustomResponse


class RecipeListCreateAPIView(ListCreateAPIView):
    """
    GET:  List all recipes (everyone)
    POST: Create recipe (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Recipe.objects.filter(is_active=True).prefetch_related(
            'ingredients__product',
            'steps'
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            request=request
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            recipe = serializer.save()
            response_serializer = RecipeDetailSerializer(recipe, context={'request': request})

            return CustomResponse.success(
                message_key="RECIPE_CREATED_SUCCESSFULLY",
                data=response_serializer.data,
                status_code=status.HTTP_201_CREATED,
                request=request
            )

        return CustomResponse.error(
            message_key="VALIDATION_ERROR",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            request=request
        )


class RecipeRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET:    Retrieve recipe (everyone)
    PUT:    Update recipe (admin only)
    DELETE: Delete recipe (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RecipeCreateUpdateSerializer
        return RecipeDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])

        serializer = self.get_serializer(instance, context={'request': request})

        return CustomResponse.success(
            message_key="SUCCESS_MESSAGE",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
            request=request
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            recipe = serializer.save()
            response_serializer = RecipeDetailSerializer(recipe, context={'request': request})

            return CustomResponse.success(
                message_key="RECIPE_UPDATED_SUCCESSFULLY",
                data=response_serializer.data,
                status_code=status.HTTP_200_OK,
                request=request
            )

        return CustomResponse.error(
            message_key="VALIDATION_ERROR",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            request=request
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])

        return CustomResponse.success(
            message_key="RECIPE_DELETED_SUCCESSFULLY",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT,
            request=request
        )