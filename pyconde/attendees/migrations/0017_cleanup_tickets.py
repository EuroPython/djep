# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Ticket.last_name'
        db.delete_column(u'attendees_ticket', 'last_name')

        # Deleting field 'Ticket.first_name'
        db.delete_column(u'attendees_ticket', 'first_name')

        # Deleting field 'Ticket.shirtsize'
        db.delete_column(u'attendees_ticket', 'shirtsize_id')

        # Deleting field 'Ticket.voucher'
        db.delete_column(u'attendees_ticket', 'voucher_id')

        db.rename_column(u'attendees_venueticket', 'first_name_tmp', 'first_name')
        db.rename_column(u'attendees_venueticket', 'last_name_tmp', 'last_name')
        db.rename_column(u'attendees_venueticket', 'shirtsize_tmp_id', 'shirtsize_id')
        db.rename_column(u'attendees_venueticket', 'voucher_tmp_id', 'voucher_id')

        db.rename_column(u'attendees_simcardticket', 'first_name_tmp', 'first_name')
        db.rename_column(u'attendees_simcardticket', 'last_name_tmp', 'last_name')

    def backwards(self, orm):
        db.rename_column(u'attendees_venueticket', 'first_name', 'first_name_tmp')
        db.rename_column(u'attendees_venueticket', 'last_name', 'last_name_tmp')
        db.rename_column(u'attendees_venueticket', 'shirtsize_id', 'shirtsize_tmp_id')
        db.rename_column(u'attendees_venueticket', 'voucher_id', 'voucher_tmp_id')

        db.rename_column(u'attendees_simcardticket', 'first_name', 'first_name_tmp')
        db.rename_column(u'attendees_simcardticket', 'last_name', 'last_name_tmp')

        # Adding field 'Ticket.last_name'
        db.add_column(u'attendees_ticket', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True),
                      keep_default=False)

        # Adding field 'Ticket.first_name'
        db.add_column(u'attendees_ticket', 'first_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True),
                      keep_default=False)

        # Adding field 'Ticket.shirtsize'
        db.add_column(u'attendees_ticket', 'shirtsize',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attendees.TShirtSize'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Ticket.voucher'
        db.add_column(u'attendees_ticket', 'voucher',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attendees.Voucher'], null=True, blank=True),
                      keep_default=False)

    models = {
        u'attendees.purchase': {
            'Meta': {'object_name': 'Purchase'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'exported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'invoice_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "'invoice'", 'max_length': '20'}),
            'payment_total': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'payment_transaction': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'incomplete'", 'max_length': '25'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'vat_id': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'attendees.simcardticket': {
            'Meta': {'ordering': "('ticket_type__tutorial_ticket', 'ticket_type__product_number')", 'object_name': 'SIMCardTicket', '_ormbases': [u'attendees.Ticket']},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'hotel_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sim_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'ticket_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['attendees.Ticket']", 'unique': 'True', 'primary_key': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'attendees.supportticket': {
            'Meta': {'ordering': "('ticket_type__tutorial_ticket', 'ticket_type__product_number')", 'object_name': 'SupportTicket', '_ormbases': [u'attendees.Ticket']},
            u'ticket_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['attendees.Ticket']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'attendees.ticket': {
            'Meta': {'ordering': "('ticket_type__tutorial_ticket', 'ticket_type__product_number')", 'object_name': 'Ticket'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.Purchase']"}),
            'ticket_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.TicketType']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'attendees_ticket_tickets'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'attendees.tickettype': {
            'Meta': {'ordering': "('tutorial_ticket', 'product_number', 'vouchertype_needed')", 'unique_together': "[('product_number', 'conference')]", 'object_name': 'TicketType'},
            'conference': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['conference.Conference']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
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
        u'attendees.venueticket': {
            'Meta': {'ordering': "('ticket_type__tutorial_ticket', 'ticket_type__product_number')", 'object_name': 'VenueTicket', '_ormbases': [u'attendees.Ticket']},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shirtsize': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.TShirtSize']", 'null': 'True', 'blank': 'True'}),
            u'ticket_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['attendees.Ticket']", 'unique': 'True', 'primary_key': 'True'}),
            'voucher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendees.Voucher']", 'null': 'True', 'blank': 'True'})
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
