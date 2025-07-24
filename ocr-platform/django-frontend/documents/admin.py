from django.contrib import admin
from .models import Doc, UserToDoc, FileType, Cart


@admin.register(Doc)
class DocAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'size', 'created_at')
    search_fields = ('file_path',)

    def file_name(self, obj):
        return obj.file_path.name.split('/')[-1]


@admin.register(UserToDoc)
class UserToDocAdmin(admin.ModelAdmin):
    list_display = ('user', 'doc', 'created_at')
    list_filter = ('user', 'created_at')


@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('extension', 'price')
    list_editable = ('price',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'doc', 'order_price', 'payment', 'created_at')
    list_filter = ('user', 'payment')
    search_fields = ('user__username',)