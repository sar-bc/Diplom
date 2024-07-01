from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


from import_export.admin import ImportExportModelAdmin

User = get_user_model()

class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ["username"]
    list_editable = ('is_active',)
    list_display = ('username', 'is_active')

    class Meta:
        model = User
        fields = ('username', 'password')

    def __str__(self):
        return str(self.username)


admin.site.register(User, UserAdmin)



