from drf_spectacular.utils import OpenApiParameter


play_schema = {
    "parameters": [
            OpenApiParameter(
                "title",
                type={"type": "string"},
                description="Filter by title (ex. ?title=something)"
            ),
            OpenApiParameter(
                "genres",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by genres ids (ex. ?genre=2,3)"
            ),
            OpenApiParameter(
                "actors",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by actors ids (ex. ?actors=2,3)"
            )
        ]
}

performance_schema = {"parameters": [
            OpenApiParameter(
                "date",
                type={"type": "string"},
                description="Filter by date (ex. ?date=2024-10-09)"
            ),
            OpenApiParameter(
                "play_id_str",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by plays ids (ex. ?plays=2,3)"
            )
        ]
}
