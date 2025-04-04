from django.urls import path
from product import views


urlpatterns = [
    #Product
    path('create', views.ProductCreateApiView.as_view()),
    path('update/<int:id>', views.ProductUpdateApiView.as_view()),
    path('delete', views.ProductDeleteApiView.as_view()),
    path('info/<int:id>', views.ProductDetailView.as_view()),
    path('list', views.ProductListApiView.as_view()),
    
    #Product Web
    path('web-product', views.WebProductUpdateApiView.as_view()),
    
    #Type
    path('type/create', views.TypeCreateApiView.as_view()),
    path('type/update/<int:id>', views.TypeUpdateApiView.as_view()),
    path('type/delete', views.TypeDeleteApiView.as_view()),
    path('type/info/<int:id>', views.TypeDetailApiView.as_view()),
    path('type/list', views.TypeListApiView.as_view()),
    
    #Brand
    path('brand/create', views.BrandCreateApiView.as_view()),
    path('brand/update/<int:id>', views.BrandUpdateApiView.as_view()),
    path('brand/delete', views.BrandDeleteApiView.as_view()),
    path('brand/info/<int:id>', views.BrandDetailApiView.as_view()),
    path('brand/list', views.BrandListApiView.as_view()),
    
    #Category
    path('category/list', views.CategoryListApiView.as_view()),
    path('category/children/<int:parent>', views.CategoryChildrenListApiView.as_view()),
    path('category/child/<slug:parent__slug>', views.CategoryChildrenListApiView.as_view()),
    path('category/create', views.CategoryCreateApiView.as_view()),
    path('category/update/<int:id>', views.CategoryUpdateApiView.as_view()),
    path('category/delete', views.CategoryDeleteApiView.as_view()),
    path('category/info/<int:id>', views.CategoryDetailApiView.as_view()),
    
    #Region
    path('region/list', views.RegionListApiView.as_view()),
    path('region/update/<int:id>', views.RegionUpdateApiView.as_view()),
    path('region/create', views.RegionCreateApiView.as_view()),
    path('region/delete', views.RegionDeleteApiView.as_view()),
    path('region/info/<int:id>', views.RegionDetailApiView.as_view()),
    
    #Color
    path('color/list', views.ColorListApiView.as_view()),
    path('color/update/<int:id>', views.ColorUpdateApiView.as_view()),
    path('color/create', views.ColorCreateApiView.as_view()),
    path('color/delete', views.ColorDeleteApiView.as_view()),
    path('color/info/<int:id>', views.ColorDetailApiView.as_view()),
    
        
]