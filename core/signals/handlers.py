from store.signals import order_created
from django.dispatch import receiver


@receiver(order_created)
def on_orders_created(sender,**kwargs):
    print(kwargs['order'])
