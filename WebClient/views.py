from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from .helper import analyzeImage

# Create your views here.
def home(request):
    return render(request, 'home.html')

def input_image(request):
    if request.method == 'GET':
        context = {'title': 'Input Image Page'}
        if request.session.get('labeledImage', False):
            context['label'] = request.session['labeledImage']
        template = 'WebClient/image_upload.html'
        return render(request,
                      template,
                      context)
    
    elif request.method == 'POST':
        image = request.FILES['image']
        labeledImage = analyzeImage(image)
        request.session['labeledImage'] = labeledImage

        return redirect(reverse('WebClient:input_image'))