import logging
import os

from django.contrib import messages
from django.shortcuts import render, redirect
from PIL import UnidentifiedImageError

from .helper import ModelUnavailableError, analyzeImage, change12HourTo24HourFormat
from .models import History, Label
from django.conf import settings
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@login_required
def home(request):
    if request.method == 'GET':
        context = {'title': 'Dashboard | Kofee', 'judul_halaman': "Dashboard"}

        template = 'dashboard/dashboard.html'
        histories = History.objects.filter(userid=request.user).order_by('-timestamp')
        labels = Label.objects.all()

        for history in histories:
            history.image = settings.MEDIA_URL + str(history.image)
            history.timestamp = change12HourTo24HourFormat(history.timestamp.strftime("%I:%M %p")) + history.timestamp.strftime(", %d %B %Y")
            for label in labels:
                if history.label_id == label.id:
                    history.treatment = label.treatment
                    break

        context['histories'] = histories
        context['last_history'] =  histories.first() if histories.exists() else None

        return render(request,
                      template,
                      context)
    
    elif request.method == 'POST':
        image = request.FILES.get('image')
        if image is None:
            messages.error(request, "Please choose an image to diagnose.")
            return redirect('home')

        new_history = History()
        new_history.userid = request.user
        new_history.image = image
        new_history.label_id = 2 # for temporary only
        new_history.save()

        try:
            labeledImage = analyzeImage(new_history.image.path)
        except UnidentifiedImageError:
            new_history.image.delete(save=False)
            new_history.delete()
            messages.error(request, "The uploaded file is not a valid image.")
            return redirect('home')
        except ModelUnavailableError:
            logger.exception("Classification model unavailable")
            new_history.image.delete(save=False)
            new_history.delete()
            messages.error(request, "The diagnosis model is not available right now. Please try again later.")
            return redirect('home')

        label = Label.objects.filter(name=labeledImage).first()
        if label is not None:
            new_history.label_id = label.id

        new_history.filename = os.path.basename(new_history.image.name)
        new_history.save()

        return redirect('home')

@login_required
def petunjuk(request):
    template = 'dashboard/petunjuk.html'
    context = {'title': 'Petunjuk | Kofee', 'judul_halaman': "Petunjuk Penggunaan"}
    
    return render(request,
                      template,
                      context)

@login_required
def profile(request):
    if request.method == 'GET':
        template = 'dashboard/profile.html'
        context = {'title': 'Profil | Kofee', 'judul_halaman': "Profil"}
        context['user'] = request.user
        histories = History.objects.filter(userid=request.user).order_by('-timestamp')
        context['jumlah_history_user'] = len(histories)
        
        return render(request,
                    template,
                    context)
    elif request.method == 'POST':
        user = request.user
        user.username = request.POST['username']
        user.first_name = request.POST['name']
        user.email = request.POST['email']
        user.save()

        return redirect('profile')