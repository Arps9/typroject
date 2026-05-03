from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from apps.core.permissions import IsAuthenticatedAndActive
from apps.core.responses import envelope

from .models import EvidenceFile
from .serializers import EvidenceFileSerializer
from .storage import compute_sha256


class EvidenceFileViewSet(viewsets.ModelViewSet):
    queryset = EvidenceFile.objects.select_related("task", "uploaded_by")
    serializer_class = EvidenceFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticatedAndActive]
    filterset_fields = ("task",)

    ALLOWED = set(settings.ALLOWED_UPLOAD_EXTENSIONS)
    MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    def create(self, request, *args, **kwargs):
        upload = request.FILES.get("file")
        if not upload:
            return envelope(
                None, message="'file' is required",
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = upload.name.rsplit(".", 1)[-1].lower() if "." in upload.name else ""
        if ext not in self.ALLOWED:
            return envelope(
                None, message=f"Extension '.{ext}' not permitted",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if upload.size > self.MAX_BYTES:
            return envelope(
                None,
                message=f"File too large (>{settings.MAX_UPLOAD_SIZE_MB}MB)",
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(
            uploaded_by=request.user,
            original_filename=upload.name,
            content_type=upload.content_type or "",
            size_bytes=upload.size,
            checksum_sha256=compute_sha256(upload),
        )
        # TODO(phase-10): trigger AI extraction Celery task

        return envelope(
            EvidenceFileSerializer(instance, context={"request": request}).data,
            message="File uploaded",
            status=status.HTTP_201_CREATED,
        )
