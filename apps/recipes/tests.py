from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.products.models import Product
from apps.recipes.models import Recipe, RecipeProduct, RecipeStep


class RecipeAPITestCase(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name='Guruch', price=5000)
        self.product2 = Product.objects.create(name='Sabzi', price=2000)
        self.product3 = Product.objects.create(name='Go‘sht', price=15000)

        self.recipe = Recipe.objects.create(
            name='Osh',
            description='An’anaviy palov',
            calories=600,
            time_minutes=50
        )
        RecipeProduct.objects.create(recipe=self.recipe, product=self.product1, quantity='100g')
        RecipeProduct.objects.create(recipe=self.recipe, product=self.product2, quantity='50g')
        RecipeProduct.objects.create(recipe=self.recipe, product=self.product3, quantity='200g')
        RecipeStep.objects.create(recipe=self.recipe, step_number=1, text='Guruchni yuving')
        RecipeStep.objects.create(recipe=self.recipe, step_number=2, text='Sabzini to‘g‘rang')


    def test_recipe_list(self):
        url = reverse('recipes:list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_recipe_retrieve(self):
        url = reverse('recipes:detail', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Osh')
        self.assertEqual(len(response.data['ingredients']), 3)
        self.assertEqual(len(response.data['steps']), 2)


    def test_recipe_create(self):
        url = reverse('recipes:list-create')
        data = {
            'name': 'Lagman',
            'description': 'Mazali lagman',
            'calories': 500,
            'time_minutes': 40,
            'ingredients': [
                {'product': self.product1.id, 'quantity': '200g'},
                {'product': self.product2.id, 'quantity': '100g'},
            ],
            'steps': [
                {'step_number': 1, 'text': 'Qisqalar'},
                {'step_number': 2, 'text': 'Qovurasiz'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)
        new_recipe = Recipe.objects.get(name='Lagman')
        self.assertEqual(new_recipe.ingredients.count(), 2)
        self.assertEqual(new_recipe.steps.count(), 2)


    def test_recipe_update_put(self):
        url = reverse('recipes:detail', args=[self.recipe.id])
        data = {
            'name': 'Osh Yangilandi',
            'description': 'Yangilangan osh ta’rif',
            'calories': 650,
            'time_minutes': 55,
            'ingredients': [
                {'product': self.product1.id, 'quantity': '150g'}
            ],
            'steps': [
                {'step_number': 1, 'text': 'Boshqacha boshlash'}
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.name, 'Osh Yangilandi')
        self.assertEqual(self.recipe.ingredients.count(), 1)
        self.assertEqual(self.recipe.steps.count(), 1)


    def test_recipe_update_patch(self):
        url = reverse('recipes:detail', args=[self.recipe.id])
        data = {'description': 'Yangi ovqat ta’rifi'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.description, 'Yangi ovqat ta’rifi')


    def test_recipe_delete(self):
        url = reverse('recipes:detail', args=[self.recipe.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())
