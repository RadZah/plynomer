from django.views.generic import ListView
from .models import Gassmeter

# Create your views here.
class GassmeterListView(ListView):
    model = Gassmeter
    template_name = 'gassmeter_list.html'
    context_object_name = 'gassmeter_list'
    ordering = ['-timestamp']
    paginate_by = 1000


