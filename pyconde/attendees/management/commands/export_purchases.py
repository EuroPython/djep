from django.core.management.base import BaseCommand

from ... import models
from ... import exporters


class Command(BaseCommand):
    def handle(self, *args, **options):
        exporter = exporters.PurchaseEmailExporter()
        if args:
            for pk in args:
                purchase = models.Purchase.objects.get(pk=pk)
                exporter(purchase)
                print("Purchase {0} exported".format(pk))
        else:
            print("Exporting all not-exported purchases")
            for purchase in models.Purchase.objects.get_exportable_purchases():
                exporter(purchase)
                print("Purchase {0} exported".format(purchase.pk))
