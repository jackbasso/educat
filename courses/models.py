from django.db import models
from django.contrib.auth.models import User
from .fields import OrderField
# Polymorphic content
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title

class Course(models.Model):
    owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course']) # custom model fields from fields.py 531;ordering is calculated with respect to the course

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'

'''
Polymorphic content class
set up a generic relation to associate objects from different models that represent
different types of content
'''
class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,limit_choices_to={'model__in':('text','video','image','file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module']) # custom model fields from fields.py 531
    
    class Meta:
        ordering = ['order']
'''
we need three different fields to set up a generic relation. In the Content model, these are:
• content_type: A ForeignKey field to the ContentType model.
• object_id: A PositiveIntegerField to store the primary key of the related object.
• item: A GenericForeignKey field to the related object combining the two previous fields.
'''

'''
Abtract model
you define the fields you want to include in all child models
'''
class ItemBase(models.Model):
    '''
    Since this field is defined in an abstract class, you need a different related_name for each sub-model.
    Django allows you to specify a placeholder for the model class name in the related_name attribute as %(class)s.
    Since you are using '%(class)s_related' as the related_name, the reverse relationship for child models will be 
    text_related, file_related, image_related, and video_related, respectively.
    '''
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    url = models.URLField()