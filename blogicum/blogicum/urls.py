from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from blog.views import CustomLoginView
urlpatterns = [
    path('', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('auth/login/', CustomLoginView.as_view(), name='login'),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=UserCreationForm, success_url=reverse_lazy(
            'pages:about'),), name='registration',),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.page_not_found_500'
handler403 = 'pages.views.csrf_failure'
