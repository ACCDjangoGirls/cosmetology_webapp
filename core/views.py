from django.shortcuts import render

# Create your views here.

class Home(View):
    def get(self, request):
        x = {}
        return render(request, 'home.html',x)

