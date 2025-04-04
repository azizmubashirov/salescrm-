from rest_framework import serializers
from .models import *
from typing import List

class StoreListSerializers(serializers.ModelSerializer):
    swope = serializers.SerializerMethodField()
    class Meta:
        model = Store
        fields = ('id', 'address', 'phone_number', 'swope', 'name', "type", 'sell_price')
        
    def get_swope(self, obj: Store) -> List[int]:
        swope_stores = SwopeStore.objects.filter(from_store=obj)
        to_store_ids = list(swope_stores.values_list('to_store_id', flat=True))
        return to_store_ids

class StoreSerializers(serializers.ModelSerializer):
    swope = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
        
    class Meta:
        model = Store
        fields = ('id', 'address', 'phone_number', 'swope', 'name', "type", 'sell_price')
        
    def create(self, validated_data):
        swope_data = validated_data.pop('swope', [])
        store = Store.objects.create(**validated_data)
        for swope_id in swope_data:
            SwopeStore.objects.create(from_store=store, to_store_id=swope_id)

        return store
    
    def update(self, instance, validated_data):
        swope_data = validated_data.pop('swope', None)
        if swope_data is not None:
            instance.from_store_swope.all().delete()
            for swope_id in swope_data:
                SwopeStore.objects.create(from_store=instance, to_store_id=swope_id)

        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.type = validated_data.get('type', instance.type)
        instance.sell_price = validated_data.get('sell_price', instance.sell_price)
        instance.save()

        return instance
        

class BalanceListSerializers(serializers.ModelSerializer):      
    
    class Meta:
        model = StoreBalance
        fields = "__all__"
    

class DeleteSerializers(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of ids",
        max_length=100
    )

    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError("Id is not provided")
        return value





