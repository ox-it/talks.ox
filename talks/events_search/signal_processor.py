# Custom signal processor for event changes
# If an event is saved, upate it in the default way.
# If a list is saved, update affected events

from __future__ import absolute_import
from __future__ import print_function
from talks.events.models import Event
from talks.users.models import Collection, CollectionItem
from django.db import models
from haystack import signals
from haystack.exceptions import NotHandled

class EventUpdateSignalProcessor(signals.BaseSignalProcessor):
	def setup(self):
		# connect event save/delete to default handler
		models.signals.post_save.connect(self.handle_save, sender=Event)
		models.signals.post_delete.connect(self.handle_delete, sender=Event)
		
		# connect list save to handler for collection
		models.signals.post_save.connect(self.handle_save_list, sender=Collection)
		# removing a list treated same as updating it - we just update the affected talks
		models.signals.post_delete.connect(self.handle_save_list, sender=Collection)
		
		# update when talk is added/removed from a collection
		models.signals.post_save.connect(self.handle_change_collectionItem, sender=CollectionItem)
		models.signals.post_delete.connect(self.handle_change_collectionItem, sender=CollectionItem)

	def teardown(self):
		# disconnect event/collection save/delete
		models.signals.post_save.disconnect(self.handle_save, sender=Event)
		models.signals.post_delete.disconnect(self.handle_delete, sender=Event)
		models.signals.post_save.disconnect(self.handle_save_list, sender=Collection)
		models.signals.post_delete.disconnect(self.handle_save_list, sender=Collection)
		models.signals.post_save.disconnect(self.handle_change_collectionItem, sender=CollectionItem)
		models.signals.post_delete.disconnect(self.handle_change_collectionItem, sender=CollectionItem)
		
	def handle_save_list(self, sender, instance, **kwargs):
		# update the each event from the list in each index
		events = instance.get_all_events()
		using_backends = self.connection_router.for_write(instance=instance)

		for event in events.all():
			for using in using_backends:
				try:
					index = self.connections[using].get_unified_index().get_index(event.__class__)
					index.update_object(event, using=using)
				except Exception:
					# TODO: Maybe log it or let the exception bubble?
					print("NOT HANDLED")
					pass
	
	def handle_change_collectionItem(self, sender, instance, **kwargs):
		#re-index the affected event
		item = instance.item
		
		using_backends = self.connection_router.for_write(instance=instance)


		for using in using_backends:
			try:
				index = self.connections[using].get_unified_index().get_index(item.__class__)
				index.update_object(item, using=using)
			except Exception:
				print("NOT HANDLED")
				pass
