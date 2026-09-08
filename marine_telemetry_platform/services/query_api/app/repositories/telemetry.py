from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

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
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    measurment_type: MeasurementType | None = None,
) -> list[TelemetryMeasurement]:
    statement = select(TelemetryMeasurement).where(
        TelemetryMeasurement.equipment_id == equipment_id
    )
    if from_time is not None:
        statement = statement.where(TelemetryMeasurement.measured_at >= from_time)
    if to_time is not None:
        statement = statement.where(TelemetryMeasurement.measured_at <= to_time)
    if measurment_type is not None:
        statement = statement.where(TelemetryMeasurement.measurement_type == measurment_type.value)
    statement = statement.order_by(TelemetryMeasurement.measured_at.desc()).limit(limit)

    return list(session.scalars(statement))


def get_measurement_aggregates(
    session: Session,
    equipment_id: str,
    measurement_type: MeasurementType,
    bucket: str,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> list[dict[str, object]]:
    bucket_interval = BUCKET_INTERVALS[bucket]

    statement = text(
        """
        SELECT
            time_bucket(
                CAST(:bucket_interval AS interval),
                measured_at
            ) AS bucket_start,
            AVG(value) AS avg_value,
            MIN(value) AS min_value,
            MAX(value) AS max_value,
            COUNT(*) AS sample_count
        FROM telemetry_measurements
        WHERE equipment_id = :equipment_id
          AND measurement_type = :measurement_type
          AND (
              CAST(:from_time AS timestamptz) IS NULL
              OR measured_at >= CAST(:from_time AS timestamptz)
          )
          AND (
              CAST(:to_time AS timestamptz) IS NULL
              OR measured_at <= CAST(:to_time AS timestamptz)
          )
        GROUP BY bucket_start
        ORDER BY bucket_start ASC
        """
    )

    result = session.execute(
        statement,
        {
            "bucket_interval": bucket_interval,
            "equipment_id": equipment_id,
            "measurement_type": measurement_type.value,
            "from_time": from_time,
            "to_time": to_time,
        },
    )

    return [dict(row) for row in result.mappings()]


BUCKET_INTERVALS = {
    "1m": "1 minute",
    "5m": "5 minutes",
    "15m": "15 minutes",
    "1h": "1 hour",
    "1d": "1 day",
}
