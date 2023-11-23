# Feature state types
FEATURE_SEGMENT = "FEATURE_SEGMENT"
IDENTITY = "IDENTITY"
ENVIRONMENT = "ENVIRONMENT"

# Feature state statuses
COMMITTED = "COMMITTED"
DRAFT = "DRAFT"

# Feature import strategies
SKIP = "SKIP"
OVERWRITE = "OVERWRITE"
FEATURE_IMPORT_STRATEGIES = (
    (SKIP, "Skip"),
    (OVERWRITE, "Overwrite"),
)

MAX_FEATURE_EXPORT_SIZE = 1000_000
MAX_FEATURE_IMPORT_SIZE = MAX_FEATURE_EXPORT_SIZE
