from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, render_to_response, RequestContext, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from rest_framework import viewsets
from django.utils import timezone
from datetime import datetime
from forms import *
from models import *
import json
from django.core.serializers.json import DjangoJSONEncoder


@login_required()
def admission_types(request, event_id):
    # Get all tickets that are related to the current event_id
    tickets = Tickets.objects.filter(event=event_id)

    # get all the event objects for this specific event
    event = Event.objects.get(pk=event_id)
    event_is_passed = False
    if event.date < datetime.today().date():
        event_is_passed = True

    # Get all types for the event in question using the admission_types() method
    types = event.admission_types().order_by('-price')

    # define expenses and call the expenses() method from the Event Model which gets a list of all the expenses
    expenses = event.expenses()

    income = event.income()
    total_income = event.total_income()

    # runs the tickets_total() method from the Event model which gets all the tickets sold for the event
    total_revenue = event.tickets_total()
    admin_expenses = event.admin_expenses()
    admin_fee = event.admin_fee

    if total_revenue is None:
        total_revenue = 0

    if total_income is None:
        all_income = total_revenue - admin_fee
    else:
        all_income = (total_income + total_revenue) - admin_fee

    cash = event.cash
    total_expenses = event.total_expenses()
    net = 0

    if total_expenses is None:
        total_expenses = 0

    if total_revenue is None or total_expenses is None:
        cash_remaining = cash + admin_fee
    else:
        cash_remaining = ((all_income + cash) - total_expenses) + admin_fee
        net = all_income - total_expenses

    # loops through the expenses list and modifies "cost" to the result of a percentage of total revenue
    if total_revenue is not None:
        for i in expenses:
            if i.percent > 0 and all_income > 0:
                i.cost = (total_revenue - admin_expenses - admin_fee) * i.percent/100
                i.save()

    return render(request, "admissions.html", locals())

@login_required()
def report(request, year):
    events = Event.objects.filter(date__year=year, date__lt=timezone.now()).order_by(('date'))
    header = "Yearly Event Summary"
    i = 0
    netSum = 0
    for i in events:
        netSum = netSum + i.net()
    return render(request, "report.html", locals())


@login_required()
def past_events(request):

    event = Event.objects.filter(date__lt=timezone.now()).order_by(('-date'))
    header = "Past Events"

    return render(request, "past_events.html", locals())


@login_required()
def add_tickets(request, event_id):
    if request.method == 'POST':
        # # Get post data from the form submit, along with the admission type clicked
        type_id = request.POST.get('type_id')

        new_ticket = Tickets(type_id=type_id, event_id=event_id)
        new_ticket.save()

        # Grab data from database to be passed back to the template
        event = Event.objects.get(pk=event_id)
        count = event.admission_type_count(type_id)
        type_total = event.admission_type_total(type_id)
        tickets_total = event.tickets_total()
        tickets = event.count()
        cash = event.cash
        total_income = event.total_income()
        total_revenue = event.tickets_total()
        admin_fee = event.admin_fee
        admin_expenses = event.admin_expenses()

        if total_income is None:
            all_income = total_revenue
        else:
            all_income = total_income + total_revenue

        for i in event.expenses():
            if i.percent != 0 and i.percent != None:
                cost = (total_revenue - admin_expenses - admin_fee) * i.percent/100
                if cost > 0:
                    i.cost = cost
                    i.save()
                else:
                    i.cost = 0
                    i.save()
            elif i.percent is None:
                i.save()

        total_expenses = event.total_expenses()

        if total_revenue is None or total_expenses is None:
            cash_remaining = cash
        else:
            cash_remaining = all_income + cash - total_expenses
        expenses_query = event.expenses().values('cost')

        expenses = json.dumps(list(expenses_query), cls=DjangoJSONEncoder)

        data = {
            "count": count,
            "total": type_total,
            "tickets_total": tickets_total,
            "tickets_sold": tickets,
            "cash": cash,
            "cash_remaining": cash_remaining,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "all_income": all_income,
            "expenses": expenses,
            "result": "Successful",
            "type_id": type_id,
            "event_id": event_id,
            "admin_fee": admin_fee


        }
        return JsonResponse(data)

    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@login_required()
def delete_one(request, event_id, type_id):

    del_ticket = Tickets.objects.filter(type=type_id).latest('type')
    del_ticket.delete()

    event = Event.objects.get(pk=event_id)
    count = event.admission_type_count(type_id)
    type_total = event.admission_type_total(type_id)
    tickets_total = event.tickets_total()
    tickets = event.count()
    cash = event.cash
    admin_fee = event.admin_fee
    total_income = event.total_income()
    total_revenue = event.tickets_total()
    admin_expenses = event.admin_expenses()

    if total_income is None:
        total_income = 0
    if total_revenue is None:
        total_revenue = 0
    if admin_expenses is None:
        admin_expenses = 0

    if total_income is None:
        all_income = total_revenue
    else:
        all_income = total_income + total_revenue

    for i in event.expenses():
            if i.percent != 0 and i.percent != None:
                cost = (total_revenue - admin_expenses - admin_fee) * i.percent/100
                if cost > 0:
                    i.cost = cost
                    i.save()
                else:
                    i.cost = 0
                    i.save()
            elif i.percent is None:
                i.save()

    total_expenses = event.total_expenses()

    if total_revenue is None or total_expenses is None:
        cash_remaining = cash
    else:
        cash_remaining = all_income + cash - total_expenses
    expenses_query = event.expenses().values('cost')

    expenses = json.dumps(list(expenses_query), cls=DjangoJSONEncoder)

    data = {
        "count": count,
        "total": type_total,
        "tickets_total": tickets_total,
        "tickets_sold": tickets,
        "cash": cash,
        "cash_remaining": cash_remaining,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "all_income": all_income,
        "expenses": expenses,
        "result": "Successful",
        "type_id": type_id,
        "event_id": event_id,

    }

    return JsonResponse(data)


@login_required()
def mark_as_paid(request, event_id, expense_id):
    event = Event.objects.get(pk=event_id)
    expense = Expenses.objects.get(pk=expense_id)
    checked = request.POST.get('checked')
    print checked
    if checked == "true":
        checked = True
    else:
        checked = False

    expense.paid = checked
    expense.save()

    data = {
        "event_id": event_id,
    }

    return JsonResponse(data)

@login_required()
def add_type(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.POST:
            form = AdmissionForm(request.POST)
            if form.is_valid():
                form.save()
                url = reverse('admission:add_type', args=(event.id,))
                return HttpResponseRedirect(url)
    else:
        event_name = event.id
        data_dict = {'event': event_name}
        form = AdmissionForm(initial=data_dict)

    title = "Admission Types"
    data = AdmissionType.objects.filter(event=event_id).order_by('-price')

    return render(request, 'add.html', locals())


@login_required()
def add_expense(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.POST:
            form = ExpenseForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Expense added!')
                url = reverse('admission:add_expense', args=(event.id,))
                return HttpResponseRedirect(url)
    else:
        event_name = event.id
        data_dict = {'name': event_name, 'cost': '0'}
        form = ExpenseForm(initial=data_dict)

    title = "Expenses"
    data = Expenses.objects.filter(name=event_id)

    return render(request, 'add.html', locals())

@login_required()
def add_income(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.POST:
            form = IncomeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Income added!')
                url = reverse('admission:add_income', args=(event.id,))
                return HttpResponseRedirect(url)
    else:
        event_name = event.id
        data_dict = {'event': event_name}
        form = IncomeForm(initial=data_dict)

    title = "Income"
    data = Income.objects.filter(event=event_id)

    return render(request, 'add.html', locals())


@login_required()
def add_income_type(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.POST:
            form = IncomeTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Income type added!')
                url = reverse('admission:add_income_type', args=(event.id,))
                return HttpResponseRedirect(url)
    else:
        event_name = event.id
        data_dict = {'event': event_name}
        form = IncomeTypeForm(initial=data_dict)

    data = IncomeType.objects.filter(event=event_id)
    title = "Income Types"

    return render(request, 'add.html', locals())



@login_required()
def add_event_type(request):
    if request.POST:
            form = EventTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Event Type added!')
                return HttpResponseRedirect('/events/')
    else:
        form = EventTypeForm()


    return render(request, 'add.html', locals())


@login_required()
def edit_type(request, i_id):
    type = get_object_or_404(AdmissionType, pk=i_id)
    t = "Edit"

    if request.POST:
        form = AdmissionForm(request.POST, instance=type)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/events/')

    else:
        form = AdmissionForm(instance=type)

    return render_to_response("edit.html", {
        'form': form,
        'type': type,
    }, context_instance=RequestContext(request))


@login_required()
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expenses, pk=expense_id)
    t = "Edit"

    if request.POST:
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/events/')

    else:
        form = ExpenseForm(instance=expense)

    return render_to_response("edit.html", {
        'form': form,
        'expense': expense,
    }, context_instance=RequestContext(request))
