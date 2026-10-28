from django.db import models


class Restaurant(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_id = models.BigIntegerField(unique=True)
    vendor_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    rate = models.DecimalField(max_digits=3, decimal_places=2)
    menu_url = models.URLField(max_length=500)
    is_open = models.BooleanField(default=False)
    establishment = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_alias = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=1000, blank=True)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="menu_items"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
       unique_together = ('source_alias', 'restaurant',)


    def __str__(self):
        return self.title
