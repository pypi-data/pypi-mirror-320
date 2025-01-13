from bloomerp.models import BloomerpModel
from bloomerp.models.fields import StatusField
from django.db import models
import random

# Create your models here.

def generate_random_date():
    return f'{random.randint(1, 12)}/{random.randint(1, 28)}/{random.randint(2000, 2020)}'

class Parent(BloomerpModel):
    class Meta:
        db_table = 'bloomerp_tests_parent'

    name = models.CharField(max_length=255)
    age = models.IntegerField()
    is_active = models.BooleanField(default=True)
    status = StatusField(
        default='active',
        colored_choices=[
            ('active', 'Active', StatusField.GREEN),
            ('inactive', 'Inactive', StatusField.RED),
            ('pending', 'Pending', StatusField.YELLOW),
        ],
        max_length=255
    )
    date = models.DateField(default=generate_random_date)

class Many(BloomerpModel):
    class Meta:
        db_table = 'bloomerp_tests_many'

    name = models.CharField(max_length=255)
    age = models.IntegerField(default=random.randint(1, 100))
    is_active = models.BooleanField(default=True)
    date = models.DateField(default=generate_random_date)


    

class Child(BloomerpModel):
    class Meta:
        db_table = 'bloomerp_tests_child'

    name = models.CharField(max_length=255)
    age = models.IntegerField()
    is_active = models.BooleanField(default=True)
    date = models.DateField()
    parent_without_related_name = models.ForeignKey(Parent, on_delete=models.CASCADE)
    parent_with_related_name = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
    many_to_many_without_related_name = models.ManyToManyField('Many')
    many_to_many_with_related_name = models.ManyToManyField('Many', related_name='children')
    status = StatusField(
        default='active',
        colored_choices=[
            ('active', 'Active', StatusField.GREEN),
            ('inactive', 'Inactive', StatusField.RED),
            ('pending', 'Pending', StatusField.YELLOW),
        ],
        max_length=255
    )
    
