from rest_framework import serializers

from apps.users.serializers import UserMiniSerializer

from .models import EvidenceFile


class EvidenceFileSerializer(serializers.ModelSerializer):
    uploaded_by_detail = UserMiniSerializer(source="uploaded_by", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = EvidenceFile
        fields = (
            "id", "task", "uploaded_by", "uploaded_by_detail",
            "file", "file_url", "original_filename",
            "content_type", "size_bytes", "checksum_sha256",
            "metadata", "created_at",
        )
        read_only_fields = (
            "uploaded_by", "checksum_sha256", "size_bytes", "created_at",
        )

    def get_file_url(self, obj) -> str:
        request = self.context.get("request")
        try:
            url = obj.file.url
        except Exception:
            return ""
        if request:
            return request.build_absolute_uri(url)
        return url
