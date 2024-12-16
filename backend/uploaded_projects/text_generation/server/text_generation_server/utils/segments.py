# Origin:   https://github.com/predibase/lorax
# Path:     lorax/server/lorax_server/utils/segments.py
# License:  Apache License Version 2.0, January 2004

from typing import List, Tuple, Union

import torch
import numpy as np


def find_segments(
    adapter_indices: Union[torch.Tensor, List[int]]
) -> Tuple[List[int], List[int]]:
    if isinstance(adapter_indices, torch.Tensor):
        adapter_indices = adapter_indices.cpu().numpy()
    elif isinstance(adapter_indices, list):
        adapter_indices = np.array(adapter_indices)

    change_mask = np.diff(adapter_indices, prepend=adapter_indices[0] - 1)
    change_indices = np.nonzero(change_mask)[0]

    segments = [0]
    segments.extend(change_indices[1:].tolist())
    segments.append(len(adapter_indices))

    segment_indices = adapter_indices[change_indices].tolist()

    return segments, segment_indices


class SegmentConcatBuilder:
    def __init__(self):
        self.adapter_segment_indices = []
        self.adapter_segment_tensors = []

    def concat(self, adapter_segments: torch.Tensor, segment_indices: List[int]):
        # Update adapter segments
        if self.adapter_segment_tensors:
            # Because we have already processed at least one batch, remove the 0 start index
            # from this batch denoting the beginning of the segment, then offset all segment
            # positions by the value of the last segment in the previous batch to account for
            # the concatenation.
            adapter_segments = (
                adapter_segments[1:] + self.adapter_segment_tensors[-1][-1]
            )

        if (
            self.adapter_segment_indices
            and self.adapter_segment_indices[-1] == segment_indices[0]
        ):
            # If the last segment in the previous batch is the same as the first segment in this batch,
            # then we merge them together into a single segment. In effect, this means removing it from
            # the segment indices of this batch, and extending the segment span by removing the segment
            # end index from the previous batch.
            segment_indices = segment_indices[1:]
            self.adapter_segment_tensors[-1] = self.adapter_segment_tensors[-1][:-1]

        self.adapter_segment_indices.extend(segment_indices)
        self.adapter_segment_tensors.append(adapter_segments)

    def build(self) -> Tuple[torch.Tensor, List[int]]:
        return torch.concat(self.adapter_segment_tensors), self.adapter_segment_indices
