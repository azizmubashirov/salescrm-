from rest_framework import serializers
from currency.models import *


class CurrencySerializers(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = [
            'id', 'name', 'symbol', 'exchange_rate', 'is_main', 'created_at'
        ]
        
class CurrencyShortSerializers(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'symbol', 'is_main']

class CurrencyHistorySerializer(serializers.ModelSerializer):
    currency  = CurrencyShortSerializers()
    class Meta:
        model = CurrencyHistory
        fields = ['id', 'currency', 'exchange_rate', 'timestamp']

class CurrencyHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyHistory
        fields = ['currency', 'exchange_rate']
        
        
        
class CurrencyDeleteSerializers(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of ids",
        max_length=100
    )

    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError("Id is not provided")
        return value