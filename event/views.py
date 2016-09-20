from django.shortcuts import render, get_object_or_404, render_to_response, RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from admission.models import Event, Employee
from forms import *
# Create your views here.


def home(request):

    return render(request, 'home.html')

def get_organization(request):
    current_user = request.user
    user_id = current_user.id
    organization = Employee.objects.get(user=user_id).organization

    return organization


@login_required()
def events_view(request):
    
    organization = get_organization(request)
    event = Event.objects.filter(organization__name=organization, date__gte=timezone.now()).order_by(('date'))
    todays_event = Event.objects.filter(date=timezone.now())

    return render(request, 'event_list.html', locals())


@login_required()
def add_cash(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.POST:
            form = CashForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                messages.success(request, 'Modified!')
                return HttpResponseRedirect('/events/')
    else:
        form = CashForm(instance=event)

    header = "You must enter a starting cash box amount"

    return render_to_response("add.html", {
        'form': form,
        'event': event,
        'header': header,
    }, context_instance=RequestContext(request))


@login_required()
def add_event(request):
    organization = get_organization(request)
    data = {'organization': organization.id}
    if request.POST:
            form = EventForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Task added!')
                return HttpResponseRedirect('/events/')
    else:
        form = EventForm(initial=data)

    title = "New Event"

    return render(request, 'add.html', locals())


@login_required()
def delete_event(request, event_id):
    Event.objects.get(pk=event_id).delete()
    messages.success(request, 'Event Removed!')
    return HttpResponseRedirect('/events/')


@login_required()
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    t = "Edit"

    if request.POST:
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/events/')

    else:
        form = EditEventForm(instance=event)

    return render_to_response("edit.html", {
        'form': form,
        'event': event,
    }, context_instance=RequestContext(request))