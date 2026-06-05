# LATS P3
# Global Error Registry V1
#
# Purpose:
# - Central error code registry for all LATS brains/modules
# - Standard code format:
#   SYS-001, MEM-001, MKT-001, TRD-001, RSK-001, MON-001
#
# Scope:
# - TEST only
# - Registry only
# - No runtime side effects

ERROR_REGISTRY = {
    # System Core
    "SYS-001": {
        "group": "SYS",
        "name": "CONFIG_LOAD_FAIL",
        "level": "ERROR",
        "description": "System config load failed",
    },
    "SYS-002": {
        "group": "SYS",
        "name": "STARTUP_FAIL",
        "level": "ERROR",
        "description": "System startup failed",
    },
    "SYS-003": {
        "group": "SYS",
        "name": "SHUTDOWN_FAIL",
        "level": "ERROR",
        "description": "System shutdown failed",
    },
    "SYS-004": {
        "group": "SYS",
        "name": "RECOVERY_FAIL",
        "level": "ERROR",
        "description": "System recovery failed",
    },

    # Memory Brain Core
    "MEM-001": {
        "group": "MEM",
        "name": "JSON_LOAD_FAIL",
        "level": "ERROR",
        "description": "Memory JSON load failed",
    },
    "MEM-002": {
        "group": "MEM",
        "name": "JSON_SAVE_FAIL",
        "level": "ERROR",
        "description": "Memory JSON save failed",
    },
    "MEM-003": {
        "group": "MEM",
        "name": "MEMORY_NOT_FOUND",
        "level": "WARN",
        "description": "Requested memory was not found",
    },
    "MEM-004": {
        "group": "MEM",
        "name": "DUPLICATE_MEMORY",
        "level": "WARN",
        "description": "Duplicate memory id detected",
    },
    "MEM-005": {
        "group": "MEM",
        "name": "UPSERT_FAIL",
        "level": "ERROR",
        "description": "Memory upsert failed",
    },

    # Memory Candidate
    "MEM-101": {
        "group": "MEM",
        "name": "CANDIDATE_SAVE_FAIL",
        "level": "ERROR",
        "description": "Candidate save failed",
    },
    "MEM-102": {
        "group": "MEM",
        "name": "CANDIDATE_CONFIRM_FAIL",
        "level": "ERROR",
        "description": "Candidate confirm failed",
    },
    "MEM-103": {
        "group": "MEM",
        "name": "CANDIDATE_REJECT_FAIL",
        "level": "ERROR",
        "description": "Candidate reject failed",
    },
    "MEM-104": {
        "group": "MEM",
        "name": "CANDIDATE_NOT_FOUND",
        "level": "WARN",
        "description": "Candidate was not found",
    },

    # Memory API / Runtime
    "MEM-201": {
        "group": "MEM",
        "name": "API_QUERY_FAIL",
        "level": "ERROR",
        "description": "Memory API query failed",
    },
    "MEM-202": {
        "group": "MEM",
        "name": "API_HEALTH_FAIL",
        "level": "ERROR",
        "description": "Memory API health check failed",
    },
    "MEM-301": {
        "group": "MEM",
        "name": "RUNTIME_LOOP_FAIL",
        "level": "ERROR",
        "description": "Memory runtime loop failed",
    },
    "MEM-302": {
        "group": "MEM",
        "name": "RUNTIME_IMPORT_FAIL",
        "level": "ERROR",
        "description": "Memory runtime import failed",
    },

    # Market Brain
    "MKT-001": {
        "group": "MKT",
        "name": "CONTEXT_BUILD_FAIL",
        "level": "ERROR",
        "description": "Market context build failed",
    },
    "MKT-002": {
        "group": "MKT",
        "name": "TREND_BUILD_FAIL",
        "level": "ERROR",
        "description": "Market trend build failed",
    },

    # Trading Brain
    "TRD-001": {
        "group": "TRD",
        "name": "ORDER_CREATE_FAIL",
        "level": "ERROR",
        "description": "Order create failed",
    },
    "TRD-002": {
        "group": "TRD",
        "name": "ORDER_CLOSE_FAIL",
        "level": "ERROR",
        "description": "Order close failed",
    },

    # Risk Brain
    "RSK-001": {
        "group": "RSK",
        "name": "POSITION_SIZE_FAIL",
        "level": "ERROR",
        "description": "Position size calculation failed",
    },
    "RSK-002": {
        "group": "RSK",
        "name": "MAX_DRAWDOWN",
        "level": "WARN",
        "description": "Maximum drawdown threshold hit",
    },

    # Monitor / NOC
    "MON-001": {
        "group": "MON",
        "name": "MONITOR_START_FAIL",
        "level": "ERROR",
        "description": "Monitor start failed",
    },
    "MON-002": {
        "group": "MON",
        "name": "MONITOR_UPDATE_FAIL",
        "level": "ERROR",
        "description": "Monitor update failed",
    },

    # Resource Brain
    "RES-001": {
        "group": "RES",
        "name": "CPU_HIGH",
        "level": "WARN",
        "description": "CPU usage is high",
    },
    "RES-002": {
        "group": "RES",
        "name": "RAM_HIGH",
        "level": "WARN",
        "description": "RAM usage is high",
    },
    "RES-003": {
        "group": "RES",
        "name": "DISK_HIGH",
        "level": "WARN",
        "description": "Disk usage is high",
    },

    # Unknown
    "SYS-999": {
        "group": "SYS",
        "name": "UNKNOWN_ERROR",
        "level": "ERROR",
        "description": "Unknown error",
    },
}


def get_error(code):
    return ERROR_REGISTRY.get(
        code,
        ERROR_REGISTRY["SYS-999"],
    )


def get_error_name(code):
    return get_error(code).get("name")


def get_error_level(code):
    return get_error(code).get("level")


def list_errors(group=None):
    if group is None:
        return ERROR_REGISTRY

    return {
        code: data
        for code, data in ERROR_REGISTRY.items()
        if data.get("group") == group
    }


def validate_registry():
    duplicate_names = {}
    seen_names = {}

    for code, data in ERROR_REGISTRY.items():
        name = data.get("name")

        if name in seen_names:
            duplicate_names[name] = [
                seen_names[name],
                code,
            ]
        else:
            seen_names[name] = code

    return {
        "status": "OK" if not duplicate_names else "WARN",
        "total_codes": len(ERROR_REGISTRY),
        "duplicate_names": duplicate_names,
        "groups": sorted(
            set(
                item.get("group")
                for item in ERROR_REGISTRY.values()
            )
        ),
    }


if __name__ == "__main__":
    print(validate_registry())
    print(get_error("MEM-001"))
    print(get_error("MEM-999"))
