from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsAdminOrAuditor
from apps.core.responses import envelope
from apps.evidence.models import EvidenceFile

from .models import AIExtractionResult
from .services import verify_evidence


class AIExtractionResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIExtractionResult.objects.select_related("evidence")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from rest_framework import serializers

        class _Serializer(serializers.ModelSerializer):
            class Meta:
                model = AIExtractionResult
                fields = "__all__"

        return _Serializer

    @action(detail=False, methods=["post"], url_path="verify",
            permission_classes=[IsAdminOrAuditor])
    def verify(self, request):
        """POST {"evidence_id": "..."}  -> run pipeline synchronously.

        For high-throughput environments call ``verify_evidence_async`` via
        Celery instead.
        """
        eid = request.data.get("evidence_id")
        if not eid:
            return envelope(None, message="'evidence_id' is required",
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            evidence = EvidenceFile.objects.get(pk=eid)
        except EvidenceFile.DoesNotExist:
            return envelope(None, message="Evidence not found",
                            status=status.HTTP_404_NOT_FOUND)

        result = verify_evidence(evidence)
        return envelope({
            "id": str(result.id),
            "result": result.result,
            "confidence": str(result.confidence),
            "notes": result.notes,
            "fields": result.fields,
        }, message="AI verification complete (auditor must confirm)")
