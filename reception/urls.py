from django.urls import path
from reception.views import *

urlpatterns = [
    path('list', ReceptionListApiView.as_view()),
    path('import-exel-reception', ExportReceptionToExcel.as_view()),
    path('seller-list', SellerListApiView.as_view()),
    path('create', ReceptionCreateApiView.as_view()),
    path('status-change/<int:id>', ReceptionUpdateApiView.as_view()),
    path('info/<int:id>', ReceptionDetailApiView.as_view()),
    path('update/<int:id>', ReceptionEditApiView.as_view()),
    path('update-return/<int:id>', ReceptionReturnApiView.as_view()),
    path('delete', ReceptionDeleteApiView.as_view()),
    
    #Price
    path('price-list', PriceListApiView.as_view()),
    path('price-create', PriceCreateApiView.as_view()),
    path('price-edit/<int:id>', PriceUpdateApiView.as_view()),
    path('price-info/<int:id>', PriceDetailApiView.as_view()),
    path('price-delete', PriceListDeleteApiView.as_view()),
    
    #StoreProduct
    path('store-product', StoreProductListApiView.as_view()),
    path('store-product-web', StoreProductWebListAPiView.as_view()),
    path('import-exel-store-product', ExportProductToExcel.as_view()),
    path('store-product-bot', StoreProductBotListApiView.as_view()),
    path('store-product-edit/<int:id>', StoreProductEditApiView.as_view()),
    path('store-product/info/<int:id>', StoreProductDetailApiView.as_view()),
    path('store-product/info-slug/<slug:slug>', StoreProductDetailSlugApiView.as_view()),
    path('store-product-bot/info/<int:id>', StoreProductBotDetailApiView.as_view()),
    
    #BarCODE
    path('create-barcode', BarCodeCreateApiView.as_view()),
    
    #Swope
    path('swope-create', SwopeCreateApiView.as_view()),
    path('swope-list/<int:to_store>', SwopeListApiView.as_view()),
    path('swope-list-all', SwopeListAllApiView.as_view()),
    # path('swope-accept/<int:id>', SwopeUpdateApiView.as_view()),
    path('swope-info/<int:id>', SwopeDetailApiView.as_view()),
    
    #Code
    path('code/<int:reception_id>/<int:store_id>', CodeApiView.as_view()),
    
    
    path('daily-sales/', DailySalesView.as_view()),
    path('store-product-count/', StoreProductSummaryView.as_view()),
    
]