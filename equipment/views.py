import io
import pandas as pd

from django.utils import timezone
from django.http import FileResponse, Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions

from reportlab.pdfgen import canvas

from .models import EquipmentDataset
from .serializers import EquipmentDatasetSerializer


# ----------------------------
# CSV UPLOAD + STATS GENERATION
# ----------------------------
class UploadCSVView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        file_obj = request.FILES.get("file")
        dataset_name = request.data.get("name", "")

        if not file_obj:
            return Response(
                {"detail": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Read CSV
            df = pd.read_csv(file_obj)

            # Validate required columns
            required_cols = [
                "Equipment Name",
                "Type",
                "Flowrate",
                "Pressure",
                "Temperature",
            ]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                return Response(
                    {"detail": f"Missing columns: {', '.join(missing)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Summary calculations
            total_count = int(len(df))
            avg_flowrate = float(df["Flowrate"].mean())
            avg_pressure = float(df["Pressure"].mean())
            avg_temperature = float(df["Temperature"].mean())
            type_distribution = df["Type"].value_counts().to_dict()

            # Reset file pointer so Django can save it
            file_obj.seek(0)

            if not dataset_name:
                dataset_name = f"Dataset {timezone.now().strftime('%Y-%m-%d %H:%M')}"

            # Save dataset
            dataset = EquipmentDataset.objects.create(
                name=dataset_name,
                original_filename=file_obj.name,
                csv_file=file_obj,
                total_count=total_count,
                avg_flowrate=avg_flowrate,
                avg_pressure=avg_pressure,
                avg_temperature=avg_temperature,
                type_distribution=type_distribution,
            )

            # Keep only last 5 datasets
            qs = EquipmentDataset.objects.all()
            if qs.count() > 5:
                for old in qs[5:]:
                    if old.csv_file:
                        old.csv_file.delete(save=False)
                    old.delete()

            serializer = EquipmentDatasetSerializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"Error processing CSV: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ----------------------------
# GET LATEST SUMMARY
# ----------------------------
class LatestSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        latest = EquipmentDataset.objects.first()
        if not latest:
            return Response(
                {"detail": "No datasets uploaded yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EquipmentDatasetSerializer(latest)
        return Response(serializer.data)


# ----------------------------
# HISTORY (LAST 5 DATASETS)
# ----------------------------
class HistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        datasets = EquipmentDataset.objects.all()[:5]
        serializer = EquipmentDatasetSerializer(datasets, many=True)
        return Response(serializer.data)


# ----------------------------
# PDF REPORT GENERATION
# ----------------------------
class PDFReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_dataset(self, pk=None):
        if pk:
            try:
                return EquipmentDataset.objects.get(pk=pk)
            except EquipmentDataset.DoesNotExist:
                raise Http404("Dataset not found")
        else:
            dataset = EquipmentDataset.objects.first()
            if not dataset:
                raise Http404("No datasets available")
            return dataset

    def get(self, request, pk=None, format=None):
        dataset = self.get_dataset(pk)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "Chemical Equipment Parameter Report")

        p.setFont("Helvetica", 12)
        y = 770
        p.drawString(50, y, f"Dataset Name: {dataset.name}")
        y -= 20
        p.drawString(50, y, f"Original File: {dataset.original_filename}")
        y -= 20
        p.drawString(
            50, y, f"Uploaded At: {dataset.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        y -= 40

        # Summary section
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Summary Statistics")
        y -= 25
        p.setFont("Helvetica", 12)
        p.drawString(60, y, f"Total Equipment Count: {dataset.total_count}")
        y -= 20
        p.drawString(60, y, f"Average Flowrate: {dataset.avg_flowrate:.2f}")
        y -= 20
        p.drawString(60, y, f"Average Pressure: {dataset.avg_pressure:.2f}")
        y -= 20
        p.drawString(60, y, f"Average Temperature: {dataset.avg_temperature:.2f}")
        y -= 40

        # Type distribution
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Equipment Type Distribution")
        y -= 25
        p.setFont("Helvetica", 12)
        for eq_type, count in dataset.type_distribution.items():
            p.drawString(60, y, f"{eq_type}: {count}")
            y -= 18
            if y < 50:  # create new PDF page if needed
                p.showPage()
                y = 800
                p.setFont("Helvetica", 12)

        p.showPage()
        p.save()

        buffer.seek(0)
        filename = f"equipment_report_{dataset.id}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)
