from rest_framework import serializers
from .models import Board

class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    data = serializers.CharField()
    board = serializers.CharField(required=True)
    width = serializers.IntegerField(required=True)
    height = serializers.IntegerField(required=True)
    state = serializers.CharField()
    mines = serializers.IntegerField()

    def create(self, validated_data):
        return Board.objects.create(**validated_data)