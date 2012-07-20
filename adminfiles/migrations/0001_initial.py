# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileUpload'
        db.create_table('adminfiles_fileupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('upload_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('upload', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sub_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('adminfiles', ['FileUpload'])

        # Adding model 'FileUploadReference'
        db.create_table('adminfiles_fileuploadreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('upload', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['adminfiles.FileUpload'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('adminfiles', ['FileUploadReference'])

        # Adding unique constraint on 'FileUploadReference', fields ['upload', 'content_type', 'object_id']
        db.create_unique('adminfiles_fileuploadreference', ['upload_id', 'content_type_id', 'object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FileUploadReference', fields ['upload', 'content_type', 'object_id']
        db.delete_unique('adminfiles_fileuploadreference', ['upload_id', 'content_type_id', 'object_id'])

        # Deleting model 'FileUpload'
        db.delete_table('adminfiles_fileupload')

        # Deleting model 'FileUploadReference'
        db.delete_table('adminfiles_fileuploadreference')


    models = {
        'adminfiles.fileupload': {
            'Meta': {'ordering': "['upload_date', 'title']", 'object_name': 'FileUpload'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'adminfiles.fileuploadreference': {
            'Meta': {'unique_together': "(('upload', 'content_type', 'object_id'),)", 'object_name': 'FileUploadReference'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'upload': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['adminfiles.FileUpload']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['adminfiles']