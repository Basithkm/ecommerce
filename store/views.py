from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser,DjangoModelPermissions
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin,ListModelMixin
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Product,Customer,Collection,OrderItem,Cart,CartItem,Order

from .serializers import ProductSerializers,CollectionSerializer,CartSerializer,CartItemSerializer,AddCartSerializer,UpdateCartItemSerializer,CustomerSerializer,OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer
from . filter import ProductFilter
from . pagination import DefaultPagination
from  . permissions import IsAdminOrReadOnly,FullDjangoModelPermissions,ViewCustomerHistoryPermissions

# Create your views here.


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    pagination_class = DefaultPagination
    permission_classes =[IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']

    def get_serializer_context(self):
        return {'request':self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error':'producty cannot be deleted because it is assoiciated with an order item .'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
  

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes =[IsAdminOrReadOnly]
   
    def delete(self,request,pk):
        collection = get_object_or_404(Collection,pk=pk)
        if collection.products.count()>0:
            return Response({'error':'Collection canot be deleted becase it includes one or more products'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# class ReviewViewSet(ModelViewSet):
#     queryset = Reviews.objects.all()
#     serializer_class = ReviewSerializer


class CartViewSet(CreateModelMixin,GenericViewSet,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin,ListModelMixin):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):

    http_method_names=['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method=='POST':
            return AddCartSerializer

        elif self.request.method=='PATCH':
            return UpdateCartItemSerializer

        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id =self.kwargs['cart_pk'])


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class =CustomerSerializer
    permission_classes=[IsAdminUser]


    # def get_permissions(self):
    #     if self.request.method=='GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    @action(detail=True,permission_classes=[ViewCustomerHistoryPermissions])
    def history(self,request,pk):
        return Response("okk")

 
    @action(detail=False ,methods=['GET','PUT'],permission_classes =[IsAuthenticated])
    def me(self,request):
        customer =Customer.objects.get(user_id=request.user.id)
        if request.method =='GET':
            serializer =CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method=='PUT':
            serializer=CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


# {
#     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3MjQ2MDg2MiwianRpIjoiNjY0YmFmMWEyYzQzNDU0M2JlODU4YzBjODA5MzQ3YjYiLCJ1c2VyX2lkIjo1fQ.mD2bB0JOprNxsvmJWRR_FpYjG7jgRaHMxYKyuUdLRe0",
#     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjcyNDYwODYyLCJqdGkiOiJjNjZhYzY4Yzk4MTQ0ZDUzYTk0MzRkMjVmZmU5MTU5ZiIsInVzZXJfaWQiOjV9.RKXXatEZj1UZthKG3WaEJ0Ywz3XGxIb1aTKAEhqNQcA"
# }


class OrderViewSet(ModelViewSet):
    http_method_names=['get','post','patch','delete','head','options']

    def get_permissions(self):
        if self.request.method in ['PUT','PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer =CreateOrderSerializer(data=request.data,context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer=OrderSerializer(order)
        return Response(serializer.data)


    def get_serializer_class(self):
        if self.request.method=='POST':
            return CreateOrderSerializer
        elif self.request.method=='PATCH':
            return UpdateOrderSerializer
        return OrderSerializer



    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only('id').get(user_id = user.id)
        return Order.objects.filter(customer_id=customer_id)

