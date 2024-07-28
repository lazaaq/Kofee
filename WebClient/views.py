from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from .helper import analyzeImage
from .models import History
from django.conf import settings

# Create your views here.
def home(request):
    if request.method == 'GET':
        context = {'title': 'Dashboard | Kofee'}
        if request.session.get('labeledImage', False):
            context['label'] = request.session['labeledImage']
        if request.session.get('image', False):
            context['image'] = request.session['image']
        template = 'dashboard/dashboard.html'
        histories = History.objects.filter(userid=request.user).order_by('-timestamp')
        histories = list(histories)
        context['histories'] = histories
        for history in histories:
            history.image = settings.MEDIA_URL + str(history.image)
        return render(request,
                      template,
                      context)
    
    elif request.method == 'POST':
        new_history = History()
        image = request.FILES['image']
        print("checkpoint 1")
        labeledImage, file_name = analyzeImage(image)
        print("checkpoint 2")
        request.session['labeledImage'] = labeledImage
        request.session['image'] = image
        new_history.userid = request.user
        new_history.filename = file_name
        new_history.image = request.FILES['image']
        new_history.label = labeledImage
        print("checkpoint 3")
        new_history.save()

        return redirect('home')
