from django.contrib import admin

from auction.models import Auction, Bid


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    exclude = ('object_id',)
    readonly_fields = ('content_type', 'content_object', 'price', 'winner')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AuctionAdmin(admin.ModelAdmin):
    list_display = ('target_user', 'created')
    inlines = (BidInline,)
    readonly_fields = ('target_user',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Auction, AuctionAdmin)
