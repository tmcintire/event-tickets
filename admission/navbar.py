from models import Event

def navbar(request):
    years = Event.objects.all().dates('date', 'year')

    return locals()
