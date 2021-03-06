from django.conf.urls import url

from . import views
from event.views import add_cash

app_name = "admission"
urlpatterns = [
    url(r'^(?P<event_id>[0-9]+)/$', views.admission_types, name="admission"),
    url(r'^(?P<event_id>[0-9]+)/addtickets/$', views.add_tickets, name="addtickets"),
    url(r'^(?P<event_id>[0-9]+)/deleteone/(?P<type_id>[0-9]+)/$', views.delete_one, name="deleteone"),
    url(r'^(?P<event_id>[0-9]+)/add_admission_type/$', views.add_type, name="add_type"),
    url(r'^(?P<event_id>[0-9]+)/addexpense/$', views.add_expense, name="add_expense"),
    url(r'^(?P<event_id>[0-9]+)/addincome/$', views.add_income, name="add_income"),
    url(r'^(?P<event_id>[0-9]+)/addincometype/$', views.add_income_type, name="add_income_type"),
    url(r'^expenses/edit/(?P<expense_id>[0-9]+)/$', views.edit_expense, name="edit_expense"),
    url(r'^types/edit/(?P<i_id>[0-9]+)/$', views.edit_type, name="edit_type"),
    url(r'^(?P<event_id>[0-9]+)/cash/$', add_cash, name="starting_cash"),
    url(r'^report/(?P<year>[0-9]{4})/$', views.report, name='year_report'),
    url(r'^report/past_events/$', views.past_events, name='past_events'),
    url(r'^(?P<event_id>[0-9]+)/check_as_paid/(?P<expense_id>[0-9]+)/$', views.mark_as_paid, name="mark_as_paid"),
]
