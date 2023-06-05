from django.shortcuts import render

# Create your views here.
def render_weather_blox(request):
    return render(request, "aeris_weather/aeris_weather_blox.html")
