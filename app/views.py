from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, FormView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import View
from django.http import JsonResponse, HttpResponseForbidden

import json
from urllib.parse import parse_qs

from .forms import SignUpForm, NewItemForm
from .models import List, Item


class Registration(CreateView):
    template_name = 'registration/registration.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        random_username = get_random_string(length=32)
        while User.objects.filter(username=random_username):
            random_username = get_random_string(length=32)
        form.instance.username = random_username
        return super().form_valid(form)


class ShoppingListView(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    context_object_name = 'shopping_lists'
    model = List

    def get_queryset(self):
        return List.objects.filter(owner=self.request.user)


class ShoppingListDisplay(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'detail.html'
    context_object_name = 'shopping_list'
    model = List

    def test_func(self):
        """
        Checks if the current user is the list owner. 
        Denies access otherwise.
        """
        return self.request.user == self.get_object().owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(
            parent_list=self.object).order_by('date_created')
        context['form'] = NewItemForm()
        return context


class ShoppingListAddItem(SingleObjectMixin, UserPassesTestMixin, FormView):
    template_name = 'detail.html'
    form_class = NewItemForm
    model = List

    def test_func(self):
        """
        Checks if the current user is the list owner. 
        Denies access otherwise.
        """
        return self.request.user == self.get_object().owner

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            new_item_data = json.loads(request.POST.get('selected'))
            item = new_item_data['item']
            quantity = new_item_data['quantity']
            i = Item.objects.create(
                name=item,
                quantity=quantity,
                parent_list=self.get_object(),
                found=False,
            )
            i.save()
            data = {'item': item, 'quantity': quantity}
            return JsonResponse(data)


class ShoppingListRemoveItem(UserPassesTestMixin, DeleteView):
    template_name = 'detail.html'
    form_class = NewItemForm
    model = List

    def test_func(self):
        """
        Checks if the current user is the list owner. 
        Denies access otherwise.
        """
        return self.request.user == self.get_object().owner

    def delete(self, request, *args, **kwargs):
        item_name = request.GET['itemName']
        quantity = request.GET['quantity']
        i = Item.objects.filter(
            name=item_name,
            quantity=quantity,
            parent_list=self.get_object()
        )[0]
        i.delete()
        payload = {'delete': 'ok'}
        return JsonResponse(payload)


class ShoppingListDetailView(View):

    def get(self, request, *args, **kwargs):
        view = ShoppingListDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ShoppingListAddItem.as_view()
        return view(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        view = ShoppingListRemoveItem.as_view()
        return view(request, *args, **kwargs)


class CreateNewListView(LoginRequiredMixin, CreateView):
    template_name = 'new_list.html'
    model = List
    fields = ['name']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('list_detail', kwargs={'pk': self.object.pk})
