from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from .helper import analyzeImage, change12HourTo24HourFormat
from .models import History, Label
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    if request.method == 'GET':
        context = {'title': 'Dashboard | Kofee'}

        if request.session.get('last_history', False):
            context['last_history'] = request.session['last_history']

        template = 'dashboard/dashboard.html'
        histories = History.objects.filter(userid=request.user).order_by('-timestamp')

        for history in histories:
            history.image = settings.MEDIA_URL + str(history.image)
            history.timestamp = change12HourTo24HourFormat(history.timestamp.strftime("%I:%M %p")) + history.timestamp.strftime(", %d %B %Y")

        context['histories'] = histories
        context['last_history'] =  histories.first()

        return render(request,
                      template,
                      context)
    
    elif request.method == 'POST':
        new_history = History()
        new_history.userid = request.user
        new_history.image = request.FILES['image']
        new_history.label_id = 2 # for temporary only
        new_history.save()

        image = request.FILES['image']
        labeledImage, file_name = analyzeImage(image)

        labels = Label.objects.all()
        for label in labels:
            if label.name == labeledImage:
                new_history.label_id = label.id
                break
            
        new_history.filename = file_name
        new_history.save()

        return redirect('home')
