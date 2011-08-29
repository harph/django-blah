from django.db import models
from django.contrib.contenttypes.models import ContentType

class ModelCommentManager(models.Manager):
	"""
    A manager that retrieves comments for a particular calling instance.
    """
	def get_query_set(self):
		ctype = ContentType.objects.get_for_model(self.model)
		return Comment.objects.filter(content_type__pk = ctype.pk).distinct()

	def add_comment(self, content, owner = None):
		"""
		Creates and associate a comment with the calling instance.
		If the owner is not null, it will be associated with the comment.
		
		:param content: A string that represents the content of the comment.
		:param owner: (default None) A django.db.models.Model which will be the owner of the comment.
		
		Returns:
		An instance of the created blah.Comment object.
		"""
		return Comment.objects.add_comment(self.instance, content, owner)

	def get_owned_by(self, owner):
		"""
		Creates a queryset that matches all the comments associated with calling instance and owned by the given owner.
		
		:param owner: django.db.models.Model instance for which you want to find the comments that belong to it.
		
		Returns:
		A queryset that matches the comments associated with the calling instance and owned by the given owner.
		"""
		return Comment.objects.get_for_object_and_owner(self.instance, owner)

	def delete_all_comments(self):
		"""
		Deletes all the comments associated with the calling instance.
		"""
		Comment.objects.delete_all_comments(self.instance)
		
		
class CommentManager(models.Manager):
	"""
	A manager that retrieves comments for a particular model.
	"""
	def add_comment(self, obj, content, owner = None):
		"""
		Creates and associate a comment with the given object instance.
		If the owner is not null, it will be associated with the comment.
		
		:param obj: django.db.models.Model instance which will be associated with the comment.
		:param content: A string that represents the content of the comment.
		:param owner: (default None) A django.db.models.Model which will be the owner of the comment.
		
		Returns:
		An instance of the created blah.Comment object.
		"""
		ctype = ContentType.objects.get_for_model(obj)
		owner_ctype = None
		owner_id = None
		if isinstance(owner, models.Model):
			owner_ctype = ContentType.objects.get_for_model(owner)
			owner_id = owner.pk
		elif owner != None:
			raise AttributeError ('The owner must be an instance of Django.db.model.Models')
		owner_id = None if owner == None else owner.pk
		return self.create(content_type = ctype, object_id = obj.pk, content = content, owner_content_type = owner_ctype, owner_id = owner_id)
	
	def delete_all_comments(self, obj):
		"""
		Deletes all the comments associated with the object instance.
		
		:params obj: django.models.Model instance from which you want to delete all the associated comments.
		"""
		
		ctype = ContentType.objects.get_for_model(obj)
		current_comments = list(self.filter(content_type__pk = ctype.pk, object_id = obj.pk))
		self.get_for_object(obj).delete()

	def get_for_object(self, obj):
		"""
		Creates a queryset that matches all the comments associated with the given object.
		
		:param obj: django.db.models.Model instance for which you want to find the associated comments.
		
		Returns:
		A queryset that matches the comments associated with the object.
		"""
		ctype = ContentType.objects.get_for_model(obj)
		return self.filter(content_type__pk = ctype.pk, object_id = obj.pk)

	def get_for_object_and_owner(self, obj,  owner):
		"""
		Creates a queryset that matches all the comments associated with object and owned by the given owner.
		
		:param obj: django.db.models.Model instance for which you want to find the associated comments.
		:param owner: django.db.models.Model instance for which you want to find the comments that belong to it.
		
		Returns:
		A queryset that matches the comments associated with the object and owned by the given owner.
		"""
		ctype = ContentType.objects.get_for_model(obj)
		owner_ctype = ContentType.objects.get_for_model(owner)
		return self.filter(content_type__pk = ctype.pk, object_id = obj.pk, owner_content_type__pk = owner_ctype.pk, owner_id = owner.pk)
	
	def get_owned_by(self, owner):
		"""
		Creates a queryset that matches all the comments owned by the given owner.
		
		:param owner: django.db.models.Model instance for which you want to find the comments that belong to it.

		Returns:
		A queryset that matches the comments owned by the given owner.
		"""
		owner_ctype = ContentType.objects.get_for_model(owner)
		return self.filter(owner_content_type__pk = owner_ctype.pk, owner_id = owner.pk)
		

class CommentDescriptor(object):
	"""
	A descriptor which provides access to a ``ModelCommentManager`` for model classes and simple retrieval, 
	updating and deletion of comments for model instances.
    """

	def __get__(self, instance, obj):
		model_comment_manager = ModelCommentManager()
		model_comment_manager.model = obj
		model_comment_manager.instance = instance
		return model_comment_manager

	def __delete__(self, instance):
		Comment.objects.delete_comments(instance)
	
class Comment(models.Model):
	"""
	Represents a generic comment.
	"""
	content_type = models.ForeignKey(ContentType, related_name = 'content_type')
	object_id = models.PositiveIntegerField('object id', db_index = True)
	owner_content_type = models.ForeignKey(ContentType, related_name = 'owner_content_type', null = True, blank = True)
	owner_id = models.PositiveIntegerField('owner_id', db_index = True, null = True, blank = True)
	content = models.TextField()	
	created_date = models.DateTimeField(auto_now_add = True)
	modified_date = models.DateTimeField(auto_now = True)
	
		
	objects = CommentManager()
	
	def __unicode__(self):
		return u"%s_%s\n%s" % (self.content_type.app_label, self.content_type.model, self.content)
		
	def _get_associated_object(self):
		if self.content_type != None and self.object_id != None:
			return self.content_type.get_object_for_this_type(pk = self.object_id)
		else:
			return None
	
	@property
	def associated_object(self):
		"""
		Returns an instance of the associated object.
		"""
		return self._get_associated_object()
			
	def _get_owner(self):
		if self.owner_content_type != None and self.owner_id != None:
			return self.owner_content_type.get_object_for_this_type(pk = self.owner_id)
		else:
			return None
	
	@property
	def owner(self):
		"""
		Returns an instance of the owner object.
		"""
		return self._get_owner()
		
	@owner.setter
	def owner(self, value):
		if isinstance(value, models.Model):
			self.owner_content_type = ContentType.objects.get_for_model(value)
			self.owner_id = value.pk
		elif value != None:
			raise AttributeError ('The owner must be an instance of Django.db.model.Models')
		else:
			self.owner_content_type = None
			self.owner_id = None
		self.save()
	
	@owner.deleter
	def owner(self):
		del self.owner_content_type
		del self.owner_id
		self.save()
			