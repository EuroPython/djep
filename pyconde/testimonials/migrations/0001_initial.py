# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TestimonialPlugin'
        db.create_table(u'cmsplugin_testimonialplugin', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('author_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('author_description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'testimonials', ['TestimonialPlugin'])

        # Adding model 'TestimonialCollectionPlugin'
        db.create_table(u'cmsplugin_testimonialcollectionplugin', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'testimonials', ['TestimonialCollectionPlugin'])


    def backwards(self, orm):
        # Deleting model 'TestimonialPlugin'
        db.delete_table(u'cmsplugin_testimonialplugin')

        # Deleting model 'TestimonialCollectionPlugin'
        db.delete_table(u'cmsplugin_testimonialcollectionplugin')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'testimonials.testimonialcollectionplugin': {
            'Meta': {'object_name': 'TestimonialCollectionPlugin', 'db_table': "u'cmsplugin_testimonialcollectionplugin'", '_ormbases': ['cms.CMSPlugin']},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'testimonials.testimonialplugin': {
            'Meta': {'object_name': 'TestimonialPlugin', 'db_table': "u'cmsplugin_testimonialplugin'", '_ormbases': ['cms.CMSPlugin']},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'author_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'author_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'author_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['testimonials']