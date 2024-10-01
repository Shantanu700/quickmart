from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.signin, name="sign"),
    path("logout/", views.signout, name="logout"),
    path("products/", views.show_prod, name="show_products"),
    path("qmart_admin/", views.magnage_pro, name="manage products"),
    path("info/", views.info, name="Info"),
    path("add_to_cart/", views.manage_cart, name="add_to_cart"),
    path("test/", views.test, name="test"),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)