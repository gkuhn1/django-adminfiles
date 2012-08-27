# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FileUpload.link'
        db.add_column('adminfiles_fileupload', 'link',
                      self.gf('django.db.models.fields.URLField')(max_length=500, null=True, blank=True),
                      keep_default=False)


        # Changing field 'FileUpload.upload'
        db.alter_column('adminfiles_fileupload', 'upload', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True))

    def backwards(self, orm):
        # Deleting field 'FileUpload.link'
        db.delete_column('adminfiles_fileupload', 'link')


        # Changing field 'FileUpload.upload'
        db.alter_column('adminfiles_fileupload', 'upload', self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100))

    models = {
        'adminfiles.fileupload': {
            'Meta': {'ordering': "['upload_date', 'title']", 'object_name': 'FileUpload'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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