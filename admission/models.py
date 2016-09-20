from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum, F, Count
from django.contrib.auth.models import User


class EventTypeChoices(models.Model):
    type = models.CharField(max_length=100)

    def __unicode__(self):
        return self.type


class Organization(models.Model):
    name = models.CharField(max_length=100)
    event_types = models.ForeignKey(EventTypeChoices)

    def __unicode__(self):
        return self.name


class Event(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(EventTypeChoices)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    cash = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, verbose_name="Cash in Cashbox")
    admin_fee = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, default=0)

    def tickets(self):
        return self.tickets_set.all()

    # returns the count for all tickets sold of any type
    def count(self):
        return self.tickets_set.all().aggregate(Count('type__type')).values()[0]

    # returns the count for the specified type of admission
    def admission_type_count(self, type_id):
        return self.tickets_set.all().filter(type=type_id).aggregate(Count('type__type')).values()[0]

    # returns the total dollar amount of the specified type of admission
    def admission_type_total(self, type_id):
        return self.tickets_set.all().filter(type=type_id).aggregate(Sum(F('type__price'))).values()[0]

    def tickets_total(self):
        return self.tickets_set.all().aggregate(Sum(F('type__price'))).values()[0]

    def admission_types(self):
        return self.admissiontype_set.all()

    def admission_types_tickets(self, typeid):
        return self.tickets().filter(type=typeid)

    def expenses(self):
        return self.expenses_set.all()

    def expense_cost(self):
        return self.expenses().values("cost")

    def admin_expenses(self):
        return self.expenses().filter(category="Administrative").aggregate(Sum(F('cost'))).values()[0]

    def main_expenses(self):
        return self.expenses().filter(category="Main").aggregate(Sum(F('cost'))).values()[0]

    def total_expenses(self):
        admin_expenses = self.admin_expenses()
        main_expenses = self.main_expenses()
        if admin_expenses == None:
            admin_expenses = 0
        if main_expenses == None:
            main_expenses = 0
        return admin_expenses + main_expenses

    def income(self):
        return self.income_set.all()

    def total_income(self):
        return self.income().aggregate(Sum(F('amount'))).values()[0]

    def net(self):
        admin_expenses = self.admin_expenses()
        main_expenses = self.main_expenses()
        tickets = self.tickets_total()
        if admin_expenses is None:
            admin_expenses = 0
        if main_expenses is None:
            main_expenses = 0
        if tickets is None:
            tickets = 0
        expenses = admin_expenses + main_expenses
        return tickets - expenses

    def cash_remaining(self):
        expenses = self.total_expenses()
        if expenses is None:
            expenses = 0
        income = self.tickets_total()
        if income is None:
            income = 0;
        cash = self.cash
        if cash is None:
            cash = 0
        left = cash + income - expenses
        if left > 0:
            return left
        else:
            return 0

    def __unicode__(self):
        return self.name


class AdmissionType(models.Model):
    ADMISSION_CHOICES = (
        ('General', 'GENERAL'),
        ('Student', 'STUDENT'),
        ('Military', 'MILITARY'),
    )
    event = models.ForeignKey(Event)
    type = models.CharField(max_length=100, choices=ADMISSION_CHOICES)
    price = models.DecimalField(decimal_places=2, max_digits=10)

    def admission_type(self):
        return self.tickets_set.all()

    def admission_type_count(self):
        return self.admission_type().aggregate(Count('type')).values()[0]

    def admission_type_total_price(self):
        return self.admission_type().aggregate(Sum(F('type__price'))).values()[0]

    def __unicode__(self):
        return '%s %s' % (self.type, self.price)


class Tickets(models.Model):
    type = models.ForeignKey(AdmissionType)
    event = models.ForeignKey(Event)

    def __unicode__(self):
        return '%s %s' % (self.type, self.event)

class Expenses(models.Model):
    EXPENSE_TYPE_CHOICES = (
        ('Band', 'Band'),
        ('Venue', 'Venue'),
        ('DJ', 'DJ'),
        ('Teacher', 'Teacher'),
        ('Other', 'Other'),
    )
    EXPENSE_CATEGORY = (
        ('Main', 'Main'),
        ('Administrative', 'Administrative'),
    )
    name = models.ForeignKey(Event)
    type = models.CharField(max_length=100, choices=EXPENSE_TYPE_CHOICES, verbose_name="Expense Type")
    category = models.CharField(max_length=100, choices=EXPENSE_CATEGORY, verbose_name="Expense Category")
    notes = models.CharField(max_length=100)
    cost = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)
    percent = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return '%s %s' % (self.name, self.type)

class Income(models.Model):
    INCOME_TYPE_CHOICES = (
        ('Donation', 'Donation'),
        ('Other', 'Other'),
    )
    event = models.ForeignKey(Event)
    type = models.CharField(max_length=100, choices=INCOME_TYPE_CHOICES, verbose_name="Income Type")
    notes = models.CharField(max_length=100)
    amount = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)

    def __unicode__(self):
        return '%s %s' % (self.type, self.notes)
