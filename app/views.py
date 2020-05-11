from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponseForbidden, Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views import View
from django.forms import ValidationError
from django.views.generic import CreateView, ListView, DetailView, FormView, DeleteView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import login as auth_login
from django.template.loader import render_to_string

from .models import List, Item
from .forms import SignUpForm, NewItemForm, InviteUserForm, LoginForm

from datetime import datetime
from urllib.parse import parse_qs
import json


class UserOwnsShoppingListMixin(UserPassesTestMixin):
    def test_func(self):
        """
        Checks if the current user is the list owner, or is a guest.
        Denies access otherwise.
        """
        return self.request.user == self.get_object().owner or self.request.user in self.get_object().guest.all()


class ShoppingListDeleteView(UserOwnsShoppingListMixin, DeleteView):
    
    model = List
    success_url = reverse_lazy('my_lists')

    def get_object(self, queryset=None):
        obj = super().get_object()
        if not obj.owner == self.request.user:
            raise Http404
        return obj


class HomepageDisplayView(TemplateView):
    template_name = 'index.html'

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
        user = authenticate(username=self.request.POST['email'], password=self.request.POST['password1'])
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
            'owned_lists': List.objects.filter(owner=self.request.user) | List.objects.filter(guest__in=[self.request.user]),
        }
        return queryset


class ShoppingListDisplay(LoginRequiredMixin, UserOwnsShoppingListMixin, DetailView):
    template_name = 'detail.html'
    context_object_name = 'shopping_list'
    model = List

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(parent_list=self.object).order_by('date_created')
        context['new_item_form'] = NewItemForm()
        context['invite_user_form'] = InviteUserForm()
        return context



class FetchListView(LoginRequiredMixin, DetailView):

    model = List

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = {
            'items': Item.objects.filter(parent_list=self.object).order_by('date_created')
        }

        data = {
            'shopping_list': render_to_string('shopping_list_table.html', context, request)
        }
        return JsonResponse(data)

class ShoppingListAddItem(SingleObjectMixin, UserOwnsShoppingListMixin, FormView):
    template_name = 'detail.html'
    form_class = NewItemForm
    model = List

    def post(self, request, *args, **kwargs):
        new_item_data = json.loads(request.POST.get('selected'))
        item = new_item_data['itemName']
        quantity = new_item_data['quantity']
        i = Item.objects.create(
            name=item,
            quantity=quantity,
            parent_list=self.get_object(),
            found=False,
        )
        i.save()
        data = {
            'item': item,
            'quantity': quantity,
            'date_created': naturaltime(i.date_created),
            'timestamp': i.date_created.isoformat(),
        }
        return JsonResponse(data)


class ShoppingListRemoveItem(UserOwnsShoppingListMixin, DeleteView):
    template_name = 'detail.html'
    form_class = NewItemForm
    model = List

    def delete(self, request, *args, **kwargs):
        item_name = request.GET['itemName']
        quantity = request.GET['quantity']
        timestamp = request.GET['timestamp']
        i = Item.objects.get(
            name=item_name,
            quantity=quantity,
            parent_list=self.get_object(),
            date_created=timestamp,
        )
        i.delete()
        payload = {'delete': 'ok'}
        return JsonResponse(payload)


class ShoppingListFoundItem(UserOwnsShoppingListMixin, UpdateView):
    template_name = 'detail.html'
    model = List

    def post(self, request, *args, **kwargs):
        selected_item = json.loads(request.POST.get('selected'))
        item_name = selected_item['itemName']
        quantity = selected_item['quantity']
        timestamp = selected_item['timestamp']
        i = Item.objects.get(
            name=item_name,
            quantity=quantity,
            parent_list=self.get_object(),
            date_created=timestamp,
        )
        i.found = not i.found
        i.save()
        payload = {'update': 'ok'}
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

        email_address = request.POST.get('email_address')
        user_model = get_user_model()

        try:
            user = user_model.objects.get(email=email_address)
        except user_model.DoesNotExist:
            """
            User doesn't exist. Need to figure out some sort of
            invite/registration process from here. Gonna be complex.
            """
            
            messages.add_message(self.request, messages.ERROR,
                                 '{0} not registered on the website.'.format(email_address))
            
            # from invitations.utils import get_invitation_model
            # Invitation = get_invitation_model()
            # invite = Invitation.create(email_address, inviter=request.user)
            # invite.send_invitation(request)            
            return super().post(self, request, *args, **kwargs)

        current_list = self.get_object()
        if current_list.owner.email == email_address:
            messages.add_message(self.request, messages.ERROR,
                                 '{0} owns this list.'.format(email_address))
        else:
            current_list.guest.add(user)
            messages.add_message(self.request, messages.SUCCESS,
                                 '{0} successfully added to list.'.format(user))

        return super().post(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse('list_detail', kwargs=self.kwargs)
