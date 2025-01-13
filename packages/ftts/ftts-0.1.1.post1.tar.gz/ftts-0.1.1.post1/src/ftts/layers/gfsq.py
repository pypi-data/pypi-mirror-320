import math
from typing import List

import torch
import torch.nn as nn
from vector_quantize_pytorch import GroupedResidualFSQ


class GFSQ(nn.Module):
    def __init__(self, dim: int, levels: List[int], G: int, R: int):
        # GFSQ Block modified from ChatTTS.
        super(GFSQ, self).__init__()
        self.quantizer = GroupedResidualFSQ(
            dim=dim, levels=list(levels), num_quantizers=R, groups=G
        )
        self.n_ind = math.prod(levels)
        self.G = G
        self.R = R

    def _embed(self, x: torch.Tensor):
        x = x.transpose(1, 2)
        x = x.view(x.size(0), x.size(1), self.G, self.R).permute(2, 0, 1, 3)
        feat = self.quantizer.get_output_from_indices(x)
        return feat.transpose_(1, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x.transpose_(1, 2)
        _, ind = self.quantizer(x)
        ind = ind.permute(1, 2, 0, 3).contiguous()
        ind = ind.view(ind.size(0), ind.size(1), -1)
        return ind.transpose_(1, 2)
