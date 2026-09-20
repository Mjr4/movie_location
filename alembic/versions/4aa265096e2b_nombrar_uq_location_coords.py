"""nombrar uq_location_coords

Las bases creadas a mano antes de Alembic tienen UNIQUE (latitude, longitude) sin nombre;
el modelo la llama uq_location_coords. En bases nuevas ya viene nombrada y esto no hace nada.

Revision ID: 4aa265096e2b
Revises: a442bfbadc16
Create Date: 2026-09-20 11:14:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4aa265096e2b'
down_revision: Union[str, Sequence[str], None] = 'a442bfbadc16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COORD_COLUMNS = ["latitude", "longitude"]


def upgrade() -> None:
    uniques = sa.inspect(op.get_bind()).get_unique_constraints("locations")
    if not any(uq["column_names"] == COORD_COLUMNS and not uq["name"] for uq in uniques):
        return

    # naming_convention le da nombre a la constraint sin nombre al reflejarla, para poder dropearla
    with op.batch_alter_table(
        "locations",
        naming_convention={"uq": "uq_%(table_name)s_%(column_0_N_name)s"},
    ) as batch_op:
        batch_op.drop_constraint("uq_locations_latitude_longitude", type_="unique")
        batch_op.create_unique_constraint("uq_location_coords", COORD_COLUMNS)


def downgrade() -> None:
    # Solo cambia el nombre de la constraint: la unicidad de (latitude, longitude) se mantiene.
    pass
