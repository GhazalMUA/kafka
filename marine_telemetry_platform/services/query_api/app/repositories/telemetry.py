from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime

from shared.contracts.telemetry import MeasurementType
from shared.database.models import TelemetryMeasurement


# ye equipment_id dari -> tamame measuremnethaye on equipmentha -> sorting az jadidtarin -> limit 1
def get_latest_measurement(
    session: Session,
    equipment_id: str,
) -> TelemetryMeasurement | None:
    statement = (
        select(TelemetryMeasurement)
        .where(TelemetryMeasurement.equipment_id == equipment_id)
        .order_by(TelemetryMeasurement.measured_at.desc())
        .limit(1)
    )
    return session.scalar(statement)



# equipment ro peyda kon -> agar from dasht, ghadimitarharo hazf kon -> 
# agar to dasht jadidtarinharo hazf kon -> age measurment dasht faghat hamon type ro begir
# -> moratab kon -> limit kon

def get_measurement_history(
    session: Session,
    equipment_id: str,
    limit: int,
    from_time: datetime | None=None,
    to_time: datetime | None=None,
    measurment_type: MeasurementType | None=None
) -> list[TelemetryMeasurement]:
    statement = select(TelemetryMeasurement).where(
        TelemetryMeasurement.equipment_id == equipment_id
    )
    if from_time is not None:
        statement = statement.where(
            TelemetryMeasurement.measured_at >= from_time
        )
    if to_time is not None:
        statement = statement.where(
            TelemetryMeasurement.measured_at <= to_time
        )
    if measurment_type is not None:
        statement = statement.where(
            TelemetryMeasurement.measurement_type == measurment_type.value
        ) 
    statement = statement.order_by(TelemetryMeasurement.measured_at.desc()).limit(limit)
    
    return list(session.scalars(statement))
