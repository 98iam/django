from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'user__username')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'timestamp')
    list_filter = ('role', 'timestamp', 'session__user')
    search_fields = ('content', 'session__title')
    readonly_fields = ('timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
