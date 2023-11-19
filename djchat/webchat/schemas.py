from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from .serializers import MessageSerializer,ConversationSerializer



list_message_docs = extend_schema(
    responses=MessageSerializer(many=True),
    parameters=[
        OpenApiParameter(
            name="channel_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="ID of the channel",
        ),
         OpenApiParameter(
            name="content",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="search the channel",
        ),
    ],
)
list_conversation_docs = extend_schema(
    responses=ConversationSerializer(many=True),
    parameters=[
        OpenApiParameter(
            name="channel_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="ID of the channel",
        )
    ],
)
