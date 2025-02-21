
from django.db import models
from django.conf import settings
# from tag.models import Tag

from imagekit.models import ProcessedImageField # type: ignore
from imagekit.processors import ResizeToFill # type: ignore


# Create your models here.
from django.template.defaultfilters import slugify

from products.models import Category
from estores.models import EStore

from cloudinary.models import CloudinaryField

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=100)
    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, null=True, blank=True, related_name="estore_tags")
    slug = models.SlugField(max_length=255,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'



# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=255)
    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, null=True, blank=True, related_name="estore_blogs")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="category_blogs")
    seo_title = models.TextField(null=True, blank=True, max_length=100)
    seo_description = models.TextField(null=True, blank=True, max_length=255)
    content = models.TextField()
    slug = models.SlugField(max_length=255,null=True, blank=True)
    is_published = models.BooleanField(default=False)

    img = CloudinaryField(
        "image",
        folder="kb/blog/",
        transformation={"width": 1280, "height": 720, "crop": "fill", "quality": "auto:good"},
        blank=True,
        null=True,
    )


    # img = ProcessedImageField(upload_to='kb/blog/', processors=[ResizeToFill(1280, 720)], format='JPEG',options={'quality': 70 }, null=True,  blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    
    views = models.IntegerField(default=0)
    read_time = models.IntegerField(default=0) # in minutes
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Blog, self).save(*args, **kwargs)


    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'
    