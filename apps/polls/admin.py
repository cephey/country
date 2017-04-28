from django.contrib import admin

from apps.polls.models import Poll, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'sum_votes')
    list_filter = ('is_active',)
    readonly_fields = ('sum_votes', 'created_at')
    inlines = (ChoiceInline,)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'poll', 'vote_count')
    list_select_related = ('poll',)
    readonly_fields = ('vote_count',)
