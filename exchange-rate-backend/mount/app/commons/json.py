import rapidjson

from app.commons import logger


def loads(str: str) -> object:
    try:
        return rapidjson.loads(str)
    except Exception:
        logger.error("Unable to str to object")
        raise


def dumps(data: object) -> str:
    try:
        return rapidjson.dumps(
            data,
            datetime_mode=rapidjson.DM_ISO8601 | rapidjson.DM_NAIVE_IS_UTC,
            number_mode=rapidjson.NM_DECIMAL,
            uuid_mode=rapidjson.UM_CANONICAL,
        )
    except Exception:
        logger.error("Unable to convert data to string")
        raise
