from django.urls import path
from .views import UploadCSVView, LatestSummaryView, HistoryView, PDFReportView

urlpatterns = [
    path("upload/", UploadCSVView.as_view(), name="upload-csv"),
    path("summary/latest/", LatestSummaryView.as_view(), name="latest-summary"),
    path("history/", HistoryView.as_view(), name="history"),
    path("report/", PDFReportView.as_view(), name="latest-report"),  # /api/report/
    path(
        "report/<uuid:pk>/", PDFReportView.as_view(), name="report-by-id"
    ),  # /api/report/<id>/
]
