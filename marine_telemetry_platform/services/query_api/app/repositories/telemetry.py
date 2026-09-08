from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.database.models import TelemetryMeasurement


# ye equipment_id dari -> tamame measuremnethaye on equipmentha -> sorting az jadidtarin -> limit 1
def get_latest_measurement(
    session: Session,
    equipment_id: str,
) -> TelemetryMeasurement | None:
    statement = (
        select(TelemetryMeasurement)
        .where(
            TelemetryMeasurement.equipment_id
            == equipment_id
        )
        .order_by(
            TelemetryMeasurement.measured_at.desc()
        )
        .limit(1)
    )
    return session.scalar(statement)



# equipment_id -> measurmentha -> jadidtarinha bian aval -> maslan akharin 100 record 
def get_measurement_history(
    session: Session,
    equipment_id: str,
    limit: int,
) -> list[TelemetryMeasurement]:
    statement = (
        select(TelemetryMeasurement)
        .where(
            TelemetryMeasurement.equipment_id
            == equipment_id
        )
        .order_by(
            TelemetryMeasurement.measured_at.desc()
        )
        .limit(limit)
    )
    return list(
        session.scalars(statement)
    )