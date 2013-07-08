# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Type'
        db.create_table(u'utils_type', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'utils', ['Type'])

        # Adding model 'Scope'
        db.create_table(u'utils_scope', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scope', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['utils.Type'], null=True, blank=True)),
        ))
        db.send_create_signal(u'utils', ['Scope'])

        # Adding model 'AccessToken'
        db.create_table(u'utils_accesstoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('refresh_token', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'utils', ['AccessToken'])

        # Adding M2M table for field scope on 'AccessToken'
        m2m_table_name = db.shorten_name(u'utils_accesstoken_scope')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('accesstoken', models.ForeignKey(orm[u'utils.accesstoken'], null=False)),
            ('scope', models.ForeignKey(orm[u'utils.scope'], null=False))
        ))
        db.create_unique(m2m_table_name, ['accesstoken_id', 'scope_id'])

        # Adding model 'State'
        db.create_table(u'utils_state', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('nonce', self.gf('django.db.models.fields.CharField')(default='6f99ee35b075f3a', unique=True, max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'utils', ['State'])

        # Adding model 'Attribute'
        db.create_table(u'utils_attribute', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scope', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['utils.Scope'])),
            ('attribute', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'utils', ['Attribute'])

        # Adding model 'FirstLogin'
        db.create_table(u'utils_firstlogin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('firstLogin', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'utils', ['FirstLogin'])


    def backwards(self, orm):
        # Deleting model 'Type'
        db.delete_table(u'utils_type')

        # Deleting model 'Scope'
        db.delete_table(u'utils_scope')

        # Deleting model 'AccessToken'
        db.delete_table(u'utils_accesstoken')

        # Removing M2M table for field scope on 'AccessToken'
        db.delete_table(db.shorten_name(u'utils_accesstoken_scope'))

        # Deleting model 'State'
        db.delete_table(u'utils_state')

        # Deleting model 'Attribute'
        db.delete_table(u'utils_attribute')

        # Deleting model 'FirstLogin'
        db.delete_table(u'utils_firstlogin')


    models = {
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'utils.accesstoken': {
            'Meta': {'object_name': 'AccessToken'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'scope': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['utils.Scope']", 'symmetrical': 'False'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'utils.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'attribute': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scope': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['utils.Scope']"})
        },
        u'utils.firstlogin': {
            'Meta': {'object_name': 'FirstLogin'},
            'firstLogin': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'utils.scope': {
            'Meta': {'object_name': 'Scope'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scope': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['utils.Type']", 'null': 'True', 'blank': 'True'})
        },
        u'utils.state': {
            'Meta': {'object_name': 'State'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'default': "'cde01bd839d6405'", 'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'utils.type': {
            'Meta': {'object_name': 'Type'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        }
    }

    complete_apps = ['utils']