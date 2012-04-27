"""
This abstracts some of the functionality provided by django-taggit in order
to normalize the tags provided by the users.
"""

from taggit import managers as taggit_managers


def _normalize_tag(t):
    if isinstance(t, unicode):
        return t.lower()
    return t


class _TaggableManager(taggit_managers._TaggableManager):
    def add(self, *tags):
        return super(_TaggableManager, self).add(*[
            _normalize_tag(t) for t in tags])


class TaggableManager(taggit_managers.TaggableManager):
    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError("%s objects need to have a primary key value "
                "before you can access their tags." % model.__name__)
        manager = _TaggableManager(
            through=self.through, model=model, instance=instance
        )
        return manager
