from geolib.models.dstability.internal import Waternet
from geolib.models.dstability.internal import PersistablePoint, PersistableReferenceLine
from geolib.geometry import Point
from typing import List, Optional


class Waternet(Waternet):
    def add_reference_line(
        self,
        reference_line_id: str,
        label: str,
        notes: str,
        points: List[Point],
        bottom_head_line_id: Optional[str] = None,
        top_head_line_id: Optional[str] = None,
    ) -> PersistableReferenceLine:
        reference_line = PersistableReferenceLine(
            Id=reference_line_id, Label=label, Notes=notes
        )
        reference_line.Points = [PersistablePoint(X=p.x, Z=p.z) for p in points]

        if bottom_head_line_id is not None and not self.has_head_line_id(
            bottom_head_line_id
        ):
            raise ValueError(
                f"Unknown headline id {bottom_head_line_id} for bottom_head_line_id"
            )

        if top_head_line_id is not None and not self.has_head_line_id(top_head_line_id):
            raise ValueError(
                f"Unknown headline id {top_head_line_id} for top_head_line_id"
            )

        reference_line.BottomHeadLineId = bottom_head_line_id
        reference_line.TopHeadLineId = top_head_line_id

        self.ReferenceLines.append(reference_line)
        return reference_line
