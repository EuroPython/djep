# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Sponsor.description'
        db.add_column('sponsorship_sponsor', 'description', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Sponsor.description'
        db.delete_column('sponsorship_sponsor', 'description')


    models = {
        'conference.conference': {
            'Meta': {'object_name': 'Conference'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reviews_active': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'reviews_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'reviews_start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sponsorship.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'annotation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sponsorship.SponsorLevel']"}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sponsorship.sponsorlevel': {
            'Meta': {'ordering': "['conference', 'order']", 'object_name': 'SponsorLevel'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['conference.Conference']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['sponsorship']
