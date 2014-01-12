# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'TicketType', fields ['product_number']
        db.delete_unique(u'attendees_tickettype', ['product_number'])

        # Removing unique constraint on 'Customer', fields ['customer_number']
        db.delete_unique(u'attendees_customer', ['customer_number'])

        # Adding field 'Purchase.conference'
        db.add_column(u'attendees_purchase', 'conference',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conference.Conference'], null=True, on_delete=models.PROTECT),
                      keep_default=False)

        # Adding field 'Customer.conference'
        db.add_column(u'attendees_customer', 'conference',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conference.Conference'], null=True, on_delete=models.PROTECT),
                      keep_default=False)

        # Adding unique constraint on 'Customer', fields ['customer_number', 'conference']
        db.create_unique(u'attendees_customer', ['customer_number', 'conference_id'])

        # Adding field 'TicketType.conference'
        db.add_column(u'attendees_tickettype', 'conference',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conference.Conference'], null=True, on_delete=models.PROTECT),
                      keep_default=False)

        # Adding unique constraint on 'TicketType', fields ['product_number', 'conference']
        db.create_unique(u'attendees_tickettype', ['product_number', 'conference_id'])

        # Adding field 'VoucherType.conference'
        db.add_column(u'attendees_vouchertype', 'conference',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conference.Conference'], null=True, on_delete=models.PROTECT),
                      keep_default=False)

        # Adding field 'TShirtSize.conference'
        db.add_column(u'attendees_tshirtsize', 'conference',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['conference.Conference'], null=True, on_delete=models.PROTECT),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'TicketType', fields ['product_number', 'conference']
        db.delete_unique(u'attendees_tickettype', ['product_number', 'conference_id'])

        # Removing unique constraint on 'Customer', fields ['customer_number', 'conference']
        db.delete_unique(u'attendees_customer', ['customer_number', 'conference_id'])

        # Deleting field 'Purchase.conference'
        db.delete_column(u'attendees_purchase', 'conference_id')

        # Deleting field 'Customer.conference'
        db.delete_column(u'attendees_customer', 'conference_id')

        # Adding unique constraint on 'Customer', fields ['customer_number']
        db.create_unique(u'attendees_customer', ['customer_number'])

        # Deleting field 'TicketType.conference'
        db.delete_column(u'attendees_tickettype', 'conference_id')

        # Adding unique constraint on 'TicketType', fields ['product_number']
        db.create_unique(u'attendees_tickettype', ['product_number'])

        # Deleting field 'VoucherType.conference'
        db.delete_column(u'attendees_vouchertype', 'conference_id')

        # Deleting field 'TShirtSize.conference'
        db.delete_column(u'attendees_tshirtsize', 'conference_id')


    models = {
        u'attendees.customer': {
            'Meta': {'ordering': "('customer_number', 'email')", 'unique_together': "[('customer_number', 'conference')]", 'object_name': 'Customer'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'customer_number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'attendees.purchase': {
            'Meta': {'object_name': 'Purchase'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.Customer']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "'invoice'", 'max_length': '20'}),
            'payment_total': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'payment_transaction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'incomplete'", 'max_length': '25'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'vat_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'attendees.ticket': {
            'Meta': {'ordering': "('ticket_type__tutorial_ticket', 'ticket_type__product_number')", 'object_name': 'Ticket'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.Purchase']"}),
            'shirtsize': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.TShirtSize']", 'null': 'True', 'blank': 'True'}),
            'ticket_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.TicketType']"}),
            'voucher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.Voucher']", 'null': 'True', 'blank': 'True'})
        },
        u'attendees.tickettype': {
            'Meta': {'ordering': "('tutorial_ticket', 'product_number', 'vouchertype_needed')", 'unique_together': "[('product_number', 'conference')]", 'object_name': 'TicketType'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'date_valid_from': ('django.db.models.fields.DateTimeField', [], {}),
            'date_valid_to': ('django.db.models.fields.DateTimeField', [], {}),
            'fee': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_purchases': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'product_number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tutorial_ticket': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vouchertype_needed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.VoucherType']", 'null': 'True', 'blank': 'True'})
        },
        u'attendees.tshirtsize': {
            'Meta': {'ordering': "('sort',)", 'object_name': 'TShirtSize'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '999'})
        },
        u'attendees.voucher': {
            'Meta': {'object_name': 'Voucher'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'date_valid': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'remarks': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.VoucherType']", 'null': 'True'})
        },
        u'attendees.vouchertype': {
            'Meta': {'object_name': 'VoucherType'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            'timezone': ('timezones.fields.TimeZoneField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['attendees']