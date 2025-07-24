from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from .models import Doc, UserToDoc, FileType, Cart
from .forms import DocUploadForm, LoginForm
import os
import requests
import base64


def home(request):
    # Get all documents for current user if authenticated
    if request.user.is_authenticated:
        user_docs = Doc.objects.filter(
            id__in=UserToDoc.objects.filter(user=request.user).values('doc')
        ).order_by('-created_at')
    else:
        user_docs = Doc.objects.none()

    # Pagination
    paginator = Paginator(user_docs, 12)  # 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'media_url': settings.MEDIA_URL
    }
    return render(request, 'home.html', context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save()

            # Create UserToDoc relationship
            UserToDoc.objects.create(user=request.user, doc=doc)

            # Add to cart (automatic price calculation)
            Cart.objects.create(user=request.user, doc=doc)

            return redirect('home')
    else:
        form = DocUploadForm()

    return render(request, 'upload.html', {'form': form})


@login_required
def analyze_document(request, doc_id):
    doc = get_object_or_404(Doc, id=doc_id)

    # Check if user owns this document
    if not UserToDoc.objects.filter(user=request.user, doc=doc).exists():
        return redirect('home')

    # Prepare FastAPI request
    fastapi_url = f"{settings.FASTAPI_URL}/upload_doc"
    file_path = doc.file_path.path

    # Read file and convert to base64
    with open(file_path, 'rb') as f:
        file_content = f.read()
    base64_content = base64.b64encode(file_content).decode('utf-8')

    # Send to FastAPI
    try:
        response = requests.post(
            fastapi_url,
            data={
                'file_content': f"data:image/jpeg;base64,{base64_content}",
                'filename': os.path.basename(file_path),
                'doc_date': '2023-01-01'  # Placeholder date
            },
            timeout=30
        )

        if response.status_code == 201:
            data = response.json()
            doc_id_fastapi = data['document_id']

            # Start analysis
            analyze_url = f"{settings.FASTAPI_URL}/doc_analyse/{doc_id_fastapi}"
            analyze_response = requests.post(analyze_url)

            if analyze_response.status_code == 202:
                # Success
                return render(request, 'analysis_started.html', {
                    'doc': doc,
                    'task_id': analyze_response.json()['task_id']
                })

    except requests.exceptions.RequestException as e:
        pass

    # If we get here, something went wrong
    return render(request, 'analysis_error.html', {'doc': doc})