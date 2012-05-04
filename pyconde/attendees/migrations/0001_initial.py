# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Voucher'
        db.create_table('attendees_voucher', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=254, blank=True)),
            ('date_valid', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_used', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('attendees', ['Voucher'])

        # Adding model 'TicketType'
        db.create_table('attendees_tickettype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product_number', self.gf('django.db.models.fields.IntegerField')(unique=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('fee', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('max_purchases', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_valid_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_valid_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('voucher_needed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tutorial_ticket', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('remarks', self.gf('django.db.models.fields.CharField')(max_length=254, blank=True)),
        ))
        db.send_create_signal('attendees', ['TicketType'])

        # Adding model 'Customer'
        db.create_table('attendees_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer_number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=250)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_exported', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('attendees', ['Customer'])

        # Adding model 'Purchase'
        db.create_table('attendees_purchase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attendees.Customer'])),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('vat_id', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='new', max_length=25)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('attendees', ['Purchase'])

        # Adding model 'Ticket'
        db.create_table('attendees_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('purchase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attendees.Purchase'])),
            ('ticket_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attendees.TicketType'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('voucher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attendees.Voucher'], null=True, blank=True)),
        ))
        db.send_create_signal('attendees', ['Ticket'])


    def backwards(self, orm):
        
        # Deleting model 'Voucher'
        db.delete_table('attendees_voucher')

        # Deleting model 'TicketType'
        db.delete_table('attendees_tickettype')

        # Deleting model 'Customer'
        db.delete_table('attendees_customer')

        # Deleting model 'Purchase'
        db.delete_table('attendees_purchase')

        # Deleting model 'Ticket'
        db.delete_table('attendees_ticket')


    models = {
        'attendees.customer': {
            'Meta': {'ordering': "('customer_number',)", 'object_name': 'Customer'},
            'customer_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'attendees.purchase': {
            'Meta': {'object_name': 'Purchase'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['attendees.Customer']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '25'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'vat_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'attendees.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['attendees.Purchase']"}),
            'ticket_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['attendees.TicketType']"}),
            'voucher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['attendees.Voucher']", 'null': 'True', 'blank': 'True'})
        },
        'attendees.tickettype': {
            'Meta': {'ordering': "('product_number', 'voucher_needed')", 'object_name': 'TicketType'},
            'date_valid_from': ('django.db.models.fields.DateTimeField', [], {}),
            'date_valid_to': ('django.db.models.fields.DateTimeField', [], {}),
            'fee': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_purchases': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'product_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'tutorial_ticket': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'voucher_needed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'attendees.voucher': {
            'Meta': {'object_name': 'Voucher'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'date_valid': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'})
        }
    }

    complete_apps = ['attendees']
