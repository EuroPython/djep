# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'JobOffer.reply_to'
        db.delete_column(u'sponsorship_joboffer', 'reply_to')

        # Deleting field 'JobOffer.subject'
        db.delete_column(u'sponsorship_joboffer', 'subject')

        # Adding field 'JobOffer.title'
        db.add_column(u'sponsorship_joboffer', 'title',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'JobOffer.link'
        db.add_column(u'sponsorship_joboffer', 'link',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'JobOffer.active'
        db.add_column(u'sponsorship_joboffer', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'JobOffer.added'
        db.add_column(u'sponsorship_joboffer', 'added',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime.now, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'JobOffer.reply_to'
        db.add_column(u'sponsorship_joboffer', 'reply_to',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=75),
                      keep_default=False)

        # Adding field 'JobOffer.subject'
        db.add_column(u'sponsorship_joboffer', 'subject',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Deleting field 'JobOffer.title'
        db.delete_column(u'sponsorship_joboffer', 'title')

        # Deleting field 'JobOffer.link'
        db.delete_column(u'sponsorship_joboffer', 'link')

        # Deleting field 'JobOffer.active'
        db.delete_column(u'sponsorship_joboffer', 'active')

        # Deleting field 'JobOffer.added'
        db.delete_column(u'sponsorship_joboffer', 'added')


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
        u'conference.conference': {
            'Meta': {'object_name': 'Conference'},
            'anonymize_proposal_author': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reviews_active': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'reviews_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'reviews_start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'tickets_editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tickets_editable_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sponsorship.joboffer': {
            'Meta': {'ordering': "['-added']", 'object_name': 'JobOffer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sponsorship.Sponsor']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'sponsorship.sponsor': {
            'Meta': {'ordering': "['name']", 'object_name': 'Sponsor'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'annotation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'custom_logo_size_listing': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sponsorship.SponsorLevel']"}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sponsorship.sponsorlevel': {
            'Meta': {'ordering': "['conference', 'order']", 'object_name': 'SponsorLevel'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'sponsorship.sponsorlistplugin': {
            'Meta': {'object_name': 'SponsorListPlugin', 'db_table': "u'cmsplugin_sponsorlistplugin'", '_ormbases': ['cms.CMSPlugin']},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'custom_css_classes': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sponsorship.SponsorLevel']", 'symmetrical': 'False'}),
            'split_list_length': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['sponsorship']
