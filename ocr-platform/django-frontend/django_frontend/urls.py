from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from documents import views as doc_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', doc_views.home, name='home'),
    path('login/', doc_views.login_view, name='login'),
    path('logout/', doc_views.logout_view, name='logout'),
    path('docs/', include('documents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)