from django.contrib import admin
from managebook.models import Book, Comment


class InlineAdmin(admin.StackedInline):
    model = Comment
    readonly_fields = ('cached_likes',)
    extra = 2


class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = "title", "publish_date", "cached_rate"
    search_fields = ("title", )
    list_filter = 'publish_date', "author", "genre"
    readonly_fields = ('cached_rate', )
    inlines = (InlineAdmin, )


admin.site.register(Book, BookAdmin)
