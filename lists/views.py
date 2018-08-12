from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()
from lists.forms import ExistingListItemForm, ItemForm, NewListForm
from lists.models import Item, List


NOT_LOGGED_ERROR = 'You must log-in to see this list.'
NOT_OWNER_OR_SHAREE_ERROR = 'Only list owner and users owner shared this list with can see it.'


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})

    
def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    if list_.owner and request.user != list_.owner and not list_.shared_with.filter(pk=request.user.pk).exists():
        if request.user.is_authenticated:
            messages.error(request, NOT_OWNER_OR_SHAREE_ERROR)
        else:
            messages.error(request, NOT_LOGGED_ERROR)
        return redirect('/')
    form = ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(request, 'list.html', {'list': list_, "form": form})
        
        
def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, 'home.html', {'form': form})
        
        
def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, 'my_lists.html', {'owner': owner})

    
def share_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    list_.shared_with.add(request.POST['sharee'])
    return redirect(list_)
