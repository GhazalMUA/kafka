"""enforce telemetry reference integrity

Revision ID: e09686e69ea7
Revises: 3cf41749aae3
Create Date: 2026-10-02 11:24:38.109991

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e09686e69ea7"
down_revision: str | Sequence[str] | None = "3cf41749aae3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    # Sensor IDs are equipment-local, not globally unique.
    op.drop_constraint(
        "sensors_pkey",
        "sensors",
        type_="primary",
    )

    op.create_primary_key(
        "sensors_pkey",
        "sensors",
        [
            "equipment_id",
            "id",
        ],
    )

    # Restore every distinct equipment/sensor pair from telemetry history.
    op.execute(
        """
        INSERT INTO sensors (
            id,
            equipment_id,
            measurement_type,
            unit
        )
        SELECT DISTINCT
            sensor_id,
            equipment_id,
            measurement_type,
            unit
        FROM telemetry_measurements
        ON CONFLICT (equipment_id, id) DO NOTHING
        """
    )

    op.create_unique_constraint(
        "uq_equipment_vessel_id_id",
        "equipment",
        [
            "vessel_id",
            "id",
        ],
    )

    op.create_foreign_key(
        "fk_telemetry_measurements_equipment",
        "telemetry_measurements",
        "equipment",
        [
            "vessel_id",
            "equipment_id",
        ],
        [
            "vessel_id",
            "id",
        ],
    )

    op.create_foreign_key(
        "fk_telemetry_measurements_sensor",
        "telemetry_measurements",
        "sensors",
        [
            "equipment_id",
            "sensor_id",
        ],
        [
            "equipment_id",
            "id",
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_telemetry_measurements_sensor",
        "telemetry_measurements",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_telemetry_measurements_equipment",
        "telemetry_measurements",
        type_="foreignkey",
    )

    op.drop_constraint(
        "uq_equipment_vessel_id_id",
        "equipment",
        type_="unique",
    )

    # Restore one row per sensor ID before returning to the old PK.
    op.execute(
        """
        DELETE FROM sensors s
        USING sensors duplicate
        WHERE s.id = duplicate.id
          AND s.equipment_id > duplicate.equipment_id
        """
    )

    op.drop_constraint(
        "sensors_pkey",
        "sensors",
        type_="primary",
    )

    op.create_primary_key(
        "sensors_pkey",
        "sensors",
        ["id"],
    )
