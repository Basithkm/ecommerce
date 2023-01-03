from django.urls import path
from django.urls.conf import include    
from . import views
from rest_framework_nested import routers
# from rest_framework.routers import DefaultRouter

router = routers.DefaultRouter()
router.register('products',views.ProductViewSet,basename='products')
router.register('collection',views.CollectionViewSet)
router.register('carts',views.CartViewSet)
router.register('customer',views.CustomerViewSet)
router.register('order',views.OrderViewSet,basename='orders')


# URLConf

products_router = routers.NestedDefaultRouter(router,'products',lookup='product')
# products_router.register('reviews',views.ReviewViewSet,basename='product-reviews')

cart_router = routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_router.register('items',views.CartItemViewSet,basename='cart-items')


urlpatterns = router.urls + products_router.urls + cart_router.urls

