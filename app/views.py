from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponseForbidden, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views import View
from django.forms import ValidationError
from django.views.generic import CreateView, ListView, DetailView, FormView, DeleteView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import login as auth_login
from django.template.loader import render_to_string

from .models import List, Item, Stopword
from .forms import SignUpForm, NewItemForm, InviteUserForm, LoginForm

from datetime import datetime
from urllib.parse import parse_qs
import json
from fuzzywuzzy import fuzz
import random

STOPWORD_MESSAGES = [
    'Disallowed words used. NO!',
    'Stop trying to add naughty words m8.',
    'Please be more specific in your quantity.',
    'Am I a joke to you?!',
    'Are you trying to break me? :(',
    'Stop, or so help me God, I will hit you with my ring hand.',
    'That joke isn\'t funny anymore.',
    'LOL!!!!!! Nice try.',
    'HAHAHA, that\'s really funny. Oh wait, no it\'s not',
]


class UserOwnsListMixin(UserPassesTestMixin):
    def test_func(self):
        """
        Checks if the current user is the list owner.
        Denies access otherwise.
        """
        return self.request.user == self.get_object().owner


class UserCanInteractWithListMixin(UserPassesTestMixin):
    def test_func(self):
        """
        Checks if the current user is the list owner or a guest.
        Denies access otherwise.
        """
        return self.request.user == self.get_object().owner or self.request.user in self.get_object().guest.all()


class ShoppingListDeleteView(UserOwnsListMixin, DeleteView):
    model = List
    success_url = reverse_lazy('my_lists')


class ShoppingListHideView(UserCanInteractWithListMixin, UpdateView):
    success_url = 'my_lists.html'
    model = List

    def post(self, request, *args, **kwargs):
        current_list = List.objects.get(pk=kwargs['pk'])
        current_list.guest.remove(request.user)
        current_list.save()
        return redirect('my_lists')


class HomepageDisplayView(UserPassesTestMixin, TemplateView):
    template_name = 'index.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('my_lists')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        context['registration_form'] = SignUpForm()
        return context


class HomepageLoginView(LoginView):
    """
    Custom login view.
    """

    form_class = LoginForm
    template_name = 'index.html'
    success_url = reverse_lazy('my_lists')

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        data = {
            'redirect_url': self.success_url,
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        response = JsonResponse({
            'error': 'Unable to log in with the provided credentials.',
        })
        response.status_code = 500
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        context['registration_form'] = SignUpForm()
        return context


class HomepageRegistrationView(CreateView):
    """
    Custom registration view.
    """

    form_class = SignUpForm
    template_name = 'index.html'
    success_url = reverse_lazy('my_lists')

    def form_invalid(self, form):
        return HttpResponse(form.errors.as_json(), status=500, content_type='application/json')

    def form_valid(self, form):

        # generate random username
        random_username = get_random_string(length=32)
        while User.objects.filter(username=random_username):
            random_username = get_random_string(length=32)
        form.instance.username = random_username
        self.object = form.save()

        # log user in and redirect to logged home
        user = authenticate(
            username=self.request.POST['email'], password=self.request.POST['password1'])
        login(self.request, user)

        data = {
            'redirect_url': self.success_url,
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        context['registration_form'] = SignUpForm()
        return context


class HomepageView(View):

    def get(self, request, *args, **kwargs):
        view = HomepageDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_type = request.POST.get('requestType')
        if request_type == 'login':
            view = HomepageLoginView.as_view()
        elif request_type == 'registration' or 'registration' in request.POST:
            view = HomepageRegistrationView.as_view()

        return view(request, *args, **kwargs)


class ShoppingListView(LoginRequiredMixin, ListView):
    login_url = ''
    template_name = 'my_lists.html'
    context_object_name = 'shopping_lists'
    model = List

    def get_queryset(self):
        queryset = {
            'owned_lists': (List.objects.filter(owner=self.request.user) | List.objects.filter(guest__in=[self.request.user])).distinct(),
        }
        return queryset


class ShoppingListDisplay(LoginRequiredMixin, UserCanInteractWithListMixin, DetailView):
    template_name = 'detail.html'
    context_object_name = 'shopping_list'
    model = List

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(
            parent_list=self.object).order_by('date_created')
        context['new_item_form'] = NewItemForm()
        context['invite_user_form'] = InviteUserForm()
        return context


class FetchListView(LoginRequiredMixin, UpdateView):

    model = List
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        raw_items = request.POST.get('items').replace(u'\xa0', u' ') 
        
        browser_items = {int(k): v for k, v in json.loads(raw_items).items()}
        browser_pk = browser_items.keys()

        i = Item.objects.filter(parent_list=self.object).order_by('date_created')
        db_items = {}
        for item in i:
            db_items[item.pk] = {
                'name': item.name,
                'quantity': item.quantity,
                'found': item.found,
            }
        db_pk = db_items.keys()

        changes = {}
        
        # find items added to database
        new_items = Item.objects.filter(pk__in=list(set(db_pk) - set(browser_pk)))
        
        # if new items are found then generate html for each new entry
        c = {}
        for i in new_items:
            ctx = {'item': i}
            html = render_to_string('list_item.html', ctx, request)
            c[i.pk] = {'html': html}
        changes['new'] = c

        # find items removed from database
        changes['removed'] = {x: 'remove' for x in list(set(browser_pk) - set(db_pk))}

        # find updated items
        updated = {}
        for k, v in db_items.items():
            try:
                if str(v) != str(browser_items[k]):
                    updated[k] = v
            except KeyError: # catch keyerror in case any new stuff has been added
                pass 
        changes['updated'] = updated

        return JsonResponse({'changes': changes})


class ShoppingListAddItem(SingleObjectMixin, UserCanInteractWithListMixin, FormView):
    template_name = 'detail.html'
    form_class = NewItemForm
    model = List

    def post(self, request, *args, **kwargs):
        new_item_data = json.loads(request.POST.get('selected'))
        item = new_item_data['itemName'].replace(u'\xa0', u' ')
        quantity = new_item_data['quantity'].replace(u'\xa0', u' ')

        if _is_stopword(quantity):
            message = random.choice(STOPWORD_MESSAGES)
            return JsonResponse({'message': message}, status=500)

        i = Item.objects.create(
            name=item,
            quantity=quantity,
            parent_list=self.get_object(),
            found=False,
        )
        i.save()

        data = {
            'new_item': render_to_string('list_item.html', {'item': i}, request),
        }
        return JsonResponse(data)


def _is_stopword(word):
    """
        Takes the entered word and adds spaces between
        every letter. It then performs a comparison against
        all of the stopwords. If a similarity of 95% or 
        greater is found then disallow the word.

        Args:
            wrd = the user-entered value to test (str)

        Returns:
            True: if the user-entered value is disallowed
            False: if the user-entered value is allowed
    """
    stopwords = Stopword.objects.all().values_list('stopword', flat=True)

    wrd = word

    # if wrd is a number then return False, numbers cant
    # be disallowed
    if wrd.isdigit():
        return False

    # add spaces between each character
    wrd = ' '.join(wrd.lower())
    
    # if a direct match is found then return True
    if wrd in stopwords:
        return True

    # otherwise loop through stopwords looking for similarity
    for s in stopwords:
        ratio = fuzz.token_set_ratio(s, wrd)
        if ratio >= 95:
            print(f'Stopword detected: {word} ({ratio}%)')
            return True
    return False


class ShoppingListRemoveItem(UserCanInteractWithListMixin, DeleteView):
    template_name = 'detail.html'
    form_class = NewItemForm
    model = List

    def delete(self, request, *args, **kwargs):
        item_pk = request.GET['pk'].replace(u'\xa0', u' ')
        i = Item.objects.get(
            pk=item_pk
        )
        i.delete()
        payload = {'delete': 'ok'}
        return JsonResponse(payload)


class ShoppingListFoundItem(UserCanInteractWithListMixin, UpdateView):
    template_name = 'detail.html'
    model = List

    def post(self, request, *args, **kwargs):
        selected_item = json.loads(request.POST.get('selected'))
        item_pk = selected_item['pk']
        i = Item.objects.get(
            pk=item_pk
        )
        i.found = not i.found
        i.save()
        payload = {'update': 'ok'}
        return JsonResponse(payload)


class ShoppingListUpdateItem(UserCanInteractWithListMixin, UpdateView):
    template_name = 'detail.html'
    model = List

    def post(self, request, *args, **kwargs):
        new_data = json.loads(request.POST.get('updated_fields'))
        pk = new_data['pk']
        
        if _is_stopword(new_data['quantity']):
            message = random.choice(STOPWORD_MESSAGES)
            return JsonResponse({'message': message}, status=500)

        item = Item.objects.get(pk=pk)
        item.name = new_data['name']
        item.quantity = new_data['quantity']
        item.save()
        
        ctx = {'item': item}
        html = render_to_string('list_item.html', ctx, request)

        payload = {'html': html, 'update': 'ok'}
        return JsonResponse(payload)


class ShoppingListDetailView(View):

    def get(self, request, *args, **kwargs):
        view = ShoppingListDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_type = request.POST.get('requestType')
        if request_type == 'new':
            view = ShoppingListAddItem.as_view()
        elif request_type == 'found':
            view = ShoppingListFoundItem.as_view()
        elif request_type == 'invite':
            view = InviteToListView.as_view()
        elif request_type == 'fetch':
            view = FetchListView.as_view()
        elif request_type == 'update':
            view = ShoppingListUpdateItem.as_view()
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


class InviteToListView(SingleObjectMixin, FormView):
    template_name = 'detail.html'
    form_class = InviteUserForm
    model = List
    
    def post(self, request, *args, **kwargs):

        email_address = request.POST.get('email').lower()
        
        user_model = get_user_model()

        # see if user exists in DB
        try:
            user = user_model.objects.get(email=email_address)
        except user_model.DoesNotExist:
            response = JsonResponse({
                'error': 'User not registered on website.',
            })
            response.status_code = 500
            return response

        current_list = self.get_object()
        if current_list.owner.email == email_address:
            response = JsonResponse({
                'error': 'User {0} owns this list.'.format(email_address),
            })
            response.status_code = 500
            return response
        elif user in current_list.guest.all():
            response = JsonResponse({
                'error': 'User {0} has already been invited to this list.'.format(email_address),
            })
            response.status_code = 500
            return response
        else:
            current_list.guest.add(user)
            data = {
                'success': 'User {0} successfully invited to list.'.format(email_address),
            }
            return JsonResponse(data)

    def get_success_url(self):
        return reverse('list_detail', kwargs=self.kwargs)
