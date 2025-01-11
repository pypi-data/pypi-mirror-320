import csv
import json
from itertools import chain

from django.contrib import admin
from django.http.response import HttpResponse
from django.utils.safestring import mark_safe

from daily_active_users.models import DailyActiveUser


@admin.register(DailyActiveUser)
class DailyActiveUserAdmin(admin.ModelAdmin):
    """Daily Active User admin"""

    date_hierarchy = "date"
    list_display = ("user", "date")
    list_select_Related = ("user",)
    readonly_fields = ("user", "date", "formatted_metadata")
    fields = ("user", "date", "formatted_metadata")
    actions = ["export_as_csv"]

    def formatted_metadata(self, obj):
        json_data = json.dumps(obj.metadata, indent=4)
        return mark_safe(f"<pre>{json_data}</pre>")

    formatted_metadata.short_description = "Metadata"

    def export_as_csv(self, request, queryset):
        """Export daily active users"""

        meta = self.model._meta
        fields = [
            ("user", lambda x: x.user.username),
            ("email", lambda x: x.user.email),
            ("date", lambda x: x.date),
        ]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        writer = csv.writer(response)

        writer.writerow(name for name, _ in fields)
        for obj in queryset:
            writer.writerow(
                [func(obj) for _, func in fields]
                + list(
                    chain(
                        *[[m["name"], m["plan"]] for m in obj.metadata["organizations"]]
                    )
                )
            )

        return response

    export_as_csv.short_description = "Export Selected"
