from rest_framework import serializers
from product.models import Settings

class SettingsUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ('product_discount', 'first_payment_percentage')
    
    def create(self, validated_data):
        setting = Settings.objects.last()
        if setting:
            setting.product_discount = validated_data.get('product_discount')
            setting.first_payment_percentage = validated_data.get('first_payment_percentage')
            setting.save()
        else:
            setting = Settings.objects.create(product_discount=validated_data.get('product_discount'))
        return setting