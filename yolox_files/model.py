# Modifications copyright 2023 AI Singapore
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Original copyright 2021 Megvii, Base Detection
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""YOLOX model with its backbone (YOLOFAPN) and head (YOLOXHead).

Modifications include:
- YOLOX
    - Uses only YOLOPAFPN as backbone
    - Uses only YOLOHead as head
- YOLOPAFPN
    - Refactor arguments name
- YOLOXHead
    - Uses range based loop to iterate through in_channels
    - Removed training-related code and arguments
        - Code under the `if self.training` scope
        - get_output_and_grid() and initialize_biases() methods
"""

from typing import Any, List, Optional, Tuple, Union
import math

import torch
from torch import nn
import torch.nn.functional as F

from src.model.yoloxv1.yolox_files.darknet import CSPDarknet
from src.model.yoloxv1.yolox_files.network_blocks import (
    BaseConv,
    CSPLayer,
)
from src.model.yoloxv1.yolox_files.losses import IOUloss
from src.model.yoloxv1.yolox_files.compat import meshgrid
from src.model.yoloxv1.yolox_files.boxes import bboxes_iou

IN_CHANNELS = [256, 512, 1024]


class YOLOX(nn.Module):
    """YOLOX model module.

    The module list is defined by create_yolov3_modules function. The network
    returns loss values from three YOLO layers during training and detection
    results during test.
    """

    # pylint: disable=arguments-differ
    def __init__(
        self,
        num_classes: int,
        depth: float,
        width: float,
    ) -> None:
        super().__init__()
        self.backbone = YOLOPAFPN(depth, width)
        self.head = YOLOXHead(num_classes, width)
        self.apply(YOLOX.initialize_batch_norm)

    def forward(
        self, inputs: torch.Tensor, targets: Optional[torch.Tensor] = None
    ) -> Union[dict, torch.Tensor]:
        """Defines the computation performed at every call.

        Args:
            inputs (torch.Tensor): Input image.

        Returns:
            (torch.Tensor): The decoded output with the shape (B,D,85) where
            B is the batch size, D is the number of detections. The 85 columns
            consist of the following values:
            [x, y, w, h, conf, (cls_conf of the 80 COCO classes)].
        """
        # FPN output content features of [dark3, dark4, dark5]
        fpn_outs = self.backbone(inputs)
        if self.training:
            assert targets is not None
            loss, iou_loss, conf_loss, cls_loss, l1_loss, num_fg = self.head(
                fpn_outs, targets, inputs
            )
            outputs = {
                "total_loss": loss,
                "iou_loss": iou_loss,
                "l1_loss": l1_loss,
                "conf_loss": conf_loss,
                "cls_loss": cls_loss,
                "num_fg": num_fg,
            }
        else:
            outputs = self.head(fpn_outs)
        return outputs

    @staticmethod
    def initialize_batch_norm(module: nn.Module) -> None:
        """Initializes the BatchNorm2d layers."""
        for mod in module.modules():
            if isinstance(mod, nn.BatchNorm2d):
                mod.eps = 1e-3
                mod.momentum = 0.03


class YOLOPAFPN(nn.Module):  # pylint: disable=too-many-instance-attributes
    """YOLOv3 model. Darknet 53 is the default backbone of this model."""

    # pylint: disable=arguments-differ, dangerous-default-value, invalid-name
    def __init__(
        self,
        depth: float = 1.0,
        width: float = 1.0,
    ) -> None:
        super().__init__()
        n_bottleneck = round(3 * depth)
        self.in_features = ("dark3", "dark4", "dark5")
        self.backbone = CSPDarknet(depth, width, self.in_features)

        self.upsample = nn.Upsample(scale_factor=2, mode="nearest")
        N256, N512, N1024 = IN_CHANNELS
        self.lateral_conv0 = BaseConv(int(N1024 * width), int(N512 * width), 1, 1)
        self.C3_p4 = self.make_csp_layer(N512, N512, n_bottleneck, width)

        self.reduce_conv1 = BaseConv(int(N512 * width), int(N256 * width), 1, 1)
        self.C3_p3 = self.make_csp_layer(N256, N256, n_bottleneck, width)

        # bottom-up conv
        self.bu_conv2 = BaseConv(int(N256 * width), int(N256 * width), 3, 2)
        self.C3_n3 = self.make_csp_layer(N256, N512, n_bottleneck, width)

        # bottom-up conv
        self.bu_conv1 = BaseConv(int(N512 * width), int(N512 * width), 3, 2)
        self.C3_n4 = self.make_csp_layer(N512, N1024, n_bottleneck, width)

    @staticmethod
    def make_csp_layer(
        in_channel: int, out_channel: int, depth: int, width: float
    ) -> CSPLayer:
        """Returns a CSPLayer.

        Args:
            in_channel (int): Input channels.
            out_channel (int): Output channels.
            depth (int): Number of Bottlenecks.
            width (float): Multiplier to scale the number of input and output
                channels.

        Returns:
            (CSPLayer): A CSPLayer consisting of following blocks:
            Conv -> Bottlenecks -> Conv
                               /
                        Conv -
        """
        return CSPLayer(
            int(2 * in_channel * width), int(out_channel * width), depth, False
        )

    def forward(
        self, inputs: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Defines the computation performed at every call.

        Args:
            inputs: Input images.

        Returns:
            (Tuple[torch.Tensor, torch.Tensor, torch.Tensor]): FPN feature.
        """
        #  backbone
        out_features = self.backbone(inputs)
        [x2, x1, x0] = [out_features[f] for f in self.in_features]

        fpn_out0 = self.lateral_conv0(x0)  # 1024->512/32
        f_out0 = self.upsample(fpn_out0)  # 512/16
        f_out0 = torch.cat([f_out0, x1], 1)  # 512->1024/16
        f_out0 = self.C3_p4(f_out0)  # 1024->512/16

        fpn_out1 = self.reduce_conv1(f_out0)  # 512->256/16
        f_out1 = self.upsample(fpn_out1)  # 256/8
        f_out1 = torch.cat([f_out1, x2], 1)  # 256->512/8
        pan_out2 = self.C3_p3(f_out1)  # 512->256/8

        p_out1 = self.bu_conv2(pan_out2)  # 256->256/16
        p_out1 = torch.cat([p_out1, fpn_out1], 1)  # 256->512/16
        pan_out1 = self.C3_n3(p_out1)  # 512->512/16

        p_out0 = self.bu_conv1(pan_out1)  # 512->512/32
        p_out0 = torch.cat([p_out0, fpn_out0], 1)  # 512->1024/32
        pan_out0 = self.C3_n4(p_out0)  # 1024->1024/32

        return pan_out2, pan_out1, pan_out0


class YOLOXHead(nn.Module):  # pylint: disable=too-many-instance-attributes
    """Decoupled head.

    The decoupled head contains two parallel branches for classification and
    regression tasks. An IoU branch is added to the regression branch after
    the conv layers.
    """

    # pylint: disable=arguments-differ, dangerous-default-value, invalid-name
    def __init__(
        self,
        num_classes: int,
        width: float = 1.0,
        strides: List[int] = [8, 16, 32],
    ) -> None:
        super().__init__()

        self.sizes: List[Tuple[Any, ...]]
        feat_channels = int(256 * width)
        self.n_anchors = 1
        self.num_classes = num_classes

        self.cls_convs = nn.ModuleList()
        self.reg_convs = nn.ModuleList()
        self.cls_preds = nn.ModuleList()
        self.reg_preds = nn.ModuleList()
        self.obj_preds = nn.ModuleList()
        self.stems = nn.ModuleList()

        for in_channel in IN_CHANNELS:
            self.stems.append(BaseConv(int(in_channel * width), feat_channels, 1, 1))
            self.cls_convs.append(nn.Sequential(*self.make_group_layer(feat_channels)))
            self.reg_convs.append(nn.Sequential(*self.make_group_layer(feat_channels)))
            self.cls_preds.append(
                nn.Conv2d(feat_channels, self.n_anchors * self.num_classes, 1, 1, 0)
            )
            self.reg_preds.append(nn.Conv2d(feat_channels, 4, 1, 1, 0))
            self.obj_preds.append(nn.Conv2d(feat_channels, self.n_anchors * 1, 1, 1, 0))

        self.use_l1 = False
        self.l1_loss = nn.L1Loss(reduction="none")
        self.bcewithlog_loss = nn.BCEWithLogitsLoss(reduction="none")
        self.iou_loss = IOUloss(reduction="none")
        self.strides = strides
        self.grids = [torch.zeros(1)] * len(IN_CHANNELS)

    @staticmethod
    def make_group_layer(in_channels: int) -> Tuple[BaseConv, BaseConv]:
        """2x BaseConv layer.

        Args:
            in_channels (int): The number of input and output channels for
                BaseConv.

        Returns:
            (Tuple[BaseConv, BaseConv]): A tuple containing 2 BaseConv blocks.
        """
        return (
            BaseConv(in_channels, in_channels, 3, 1),
            BaseConv(in_channels, in_channels, 3, 1),
        )

    def initialize_biases(self, prior_prob):
        for conv in self.cls_preds:
            b = conv.bias.view(1, -1)
            b.data.fill_(-math.log((1 - prior_prob) / prior_prob))
            conv.bias = torch.nn.Parameter(b.view(-1), requires_grad=True)

        for conv in self.obj_preds:
            b = conv.bias.view(1, -1)
            b.data.fill_(-math.log((1 - prior_prob) / prior_prob))
            conv.bias = torch.nn.Parameter(b.view(-1), requires_grad=True)

    def forward(
        self,
        xin: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
        labels: Optional[Any] = None,
        imgs: Optional[Any] = None,
    ) -> torch.Tensor:
        """Defines the computation performed at every call.

        Args:
            xin (Tuple[torch.Tensor, torch.Tensor, torch.Tensor]): Inputs from
                `YOLOPAFPN`, contains 3 levels of FPN features (256, 512,
                and 1024).

        Returns:
            (torch.Tensor): The decoded output with the shape (B,D,85) where
            B is the batch size, D is the number of detections. The 85 columns
            consist of the following values:
            [x, y, w, h, conf, (cls_conf of the 80 COCO classes)].
        """
        outputs = []
        origin_preds = []
        x_shifts = []
        y_shifts = []
        expanded_strides = []

        for k, (cls_conv, reg_conv, stride_this_level, x) in enumerate(
            zip(self.cls_convs, self.reg_convs, self.strides, xin)
        ):
            x = self.stems[k](x)

            cls_feat = cls_conv(x)
            cls_output = self.cls_preds[k](cls_feat)

            reg_feat = reg_conv(x)
            reg_output = self.reg_preds[k](reg_feat)
            obj_output = self.obj_preds[k](reg_feat)

            if self.training:
                output = torch.cat([reg_output, obj_output, cls_output], 1)
                output, grid = self.get_output_and_grid(
                    output, k, stride_this_level, xin[0].type()
                )
                x_shifts.append(grid[:, :, 0])
                y_shifts.append(grid[:, :, 1])
                expanded_strides.append(
                    torch.zeros(1, grid.shape[1])
                    .fill_(stride_this_level)
                    .type_as(xin[0])
                )
                if self.use_l1:
                    batch_size = reg_output.shape[0]
                    hsize, wsize = reg_output.shape[-2:]
                    reg_output = reg_output.view(batch_size, 1, 4, hsize, wsize)
                    reg_output = reg_output.permute(0, 1, 3, 4, 2).reshape(
                        batch_size, -1, 4
                    )
                    origin_preds.append(reg_output.clone())

            else:
                output = torch.cat(
                    [reg_output, obj_output.sigmoid(), cls_output.sigmoid()], 1
                )

            outputs.append(output)

        if self.training:
            return self.get_losses(
                imgs,
                x_shifts,
                y_shifts,
                expanded_strides,
                labels,
                torch.cat(outputs, 1),
                origin_preds,
                dtype=xin[0].dtype,
            )
        else:
            self.sizes = [x.shape[-2:] for x in outputs]
            # [batch, n_anchors_all, 85]
            outputs_tensor = torch.cat(
                [x.flatten(start_dim=2) for x in outputs], dim=2
            ).permute(0, 2, 1)
            # Always decode output for inference
            outputs_tensor = self.decode_outputs(
                outputs_tensor,
                xin[0].type(),
            )
            return outputs_tensor

    def get_output_and_grid(self, output, k, stride, dtype):
        """get_output_and_grid"""
        grid = self.grids[k]

        batch_size = output.shape[0]
        n_ch = 5 + self.num_classes
        hsize, wsize = output.shape[-2:]
        if grid.shape[2:4] != output.shape[2:4]:
            yv, xv = meshgrid([torch.arange(hsize), torch.arange(wsize)])
            if dtype.startswith("torch.mps"):
                grid = torch.stack((xv, yv), 2).view(1, 1, hsize, wsize, 2).to("cpu")
                self.grids[k] = grid.to("cpu")
                output = output.to("cpu")
            else:
                grid = torch.stack((xv, yv), 2).view(1, 1, hsize, wsize, 2).type(dtype)
                self.grids[k] = grid

        output = output.view(batch_size, 1, n_ch, hsize, wsize)
        output = output.permute(0, 1, 3, 4, 2).reshape(batch_size, hsize * wsize, -1)
        grid = grid.view(1, -1, 2)
        if dtype.startswith("torch.mps"):
            output = output.to("cpu")
        output[..., :2] = (output[..., :2] + grid) * stride
        output[..., 2:4] = torch.exp(output[..., 2:4]) * stride
        return output, grid

    def decode_outputs(self, outputs: torch.Tensor, dtype: str) -> torch.Tensor:
        """Converts raw output to [x, y, w, h] format.

        Args:
            outputs (torch.Tensor): Raw output tensor. The first 4 columns
                contain 2 offsets in terms of the top-left corner of the grid,
                and the height and width of the predicted box. The rest of the
                columns are not accessed in this method.
            dtype (str): Data type.

        Returns:
            (torch.Tensor): The decoded output with the shape (B,D,85) where
            B is the batch size, D is the number of detections. The 85 columns
            consist of the following values:
            [x, y, w, h, conf, (cls_conf of the 80 COCO classes)].
        """
        grids = []
        strides = []
        for (hsize, wsize), stride in zip(self.sizes, self.strides):
            yv, xv = torch.meshgrid([torch.arange(hsize), torch.arange(wsize)])
            grid = torch.stack((xv, yv), 2).view(1, -1, 2)
            grids.append(grid)
            shape = grid.shape[:2]
            strides.append(torch.full((*shape, 1), stride))
        if dtype.startswith("torch.mps"):
            grids_tensor = torch.cat(grids, dim=1).to("cpu")
            strides_tensor = torch.cat(strides, dim=1).to("cpu")
            outputs = outputs.to("cpu")
        else:
            grids_tensor = torch.cat(grids, dim=1).type(dtype)
            strides_tensor = torch.cat(strides, dim=1).type(dtype)

        outputs[..., :2] = (outputs[..., :2] + grids_tensor) * strides_tensor
        outputs[..., 2:4] = torch.exp(outputs[..., 2:4]) * strides_tensor
        return outputs

    def get_losses(
        self,
        imgs,
        x_shifts,
        y_shifts,
        expanded_strides,
        labels,
        outputs,
        origin_preds,
        dtype,
    ):
        bbox_preds = outputs[:, :, :4]  # [batch, n_anchors_all, 4]
        obj_preds = outputs[:, :, 4:5]  # [batch, n_anchors_all, 1]
        cls_preds = outputs[:, :, 5:]  # [batch, n_anchors_all, n_cls]

        # calculate targets
        nlabel = (labels.sum(dim=2) > 0).sum(dim=1)  # number of objects

        total_num_anchors = outputs.shape[1]
        x_shifts = torch.cat(x_shifts, 1)  # [1, n_anchors_all]
        y_shifts = torch.cat(y_shifts, 1)  # [1, n_anchors_all]
        expanded_strides = torch.cat(expanded_strides, 1)
        if self.use_l1:
            origin_preds = torch.cat(origin_preds, 1)

        cls_targets = []
        reg_targets = []
        l1_targets = []
        obj_targets = []
        fg_masks = []

        num_fg = 0.0
        num_gts = 0.0

        for batch_idx in range(outputs.shape[0]):
            num_gt = int(nlabel[batch_idx])
            num_gts += num_gt
            if num_gt == 0:
                cls_target = outputs.new_zeros((0, self.num_classes))
                reg_target = outputs.new_zeros((0, 4))
                l1_target = outputs.new_zeros((0, 4))
                obj_target = outputs.new_zeros((total_num_anchors, 1))
                fg_mask = outputs.new_zeros(total_num_anchors).bool()
            else:
                gt_bboxes_per_image = labels[batch_idx, :num_gt, 1:5]
                gt_classes = labels[batch_idx, :num_gt, 0]
                bboxes_preds_per_image = bbox_preds[batch_idx]

                try:
                    (
                        gt_matched_classes,
                        fg_mask,
                        pred_ious_this_matching,
                        matched_gt_inds,
                        num_fg_img,
                    ) = self.get_assignments(  # noqa
                        batch_idx,
                        num_gt,
                        gt_bboxes_per_image,
                        gt_classes,
                        bboxes_preds_per_image,
                        expanded_strides,
                        x_shifts,
                        y_shifts,
                        cls_preds,
                        obj_preds,
                    )
                except RuntimeError as e:
                    # TODO: the string might change, consider a better way
                    if "CUDA out of memory. " not in str(e):
                        raise  # RuntimeError might not caused by CUDA OOM

                    logger.error(
                        "OOM RuntimeError is raised due to the huge memory cost during label assignment. \
                           CPU mode is applied in this batch. If you want to avoid this issue, \
                           try to reduce the batch size or image size."
                    )
                    torch.cuda.empty_cache()
                    (
                        gt_matched_classes,
                        fg_mask,
                        pred_ious_this_matching,
                        matched_gt_inds,
                        num_fg_img,
                    ) = self.get_assignments(  # noqa
                        batch_idx,
                        num_gt,
                        gt_bboxes_per_image,
                        gt_classes,
                        bboxes_preds_per_image,
                        expanded_strides,
                        x_shifts,
                        y_shifts,
                        cls_preds,
                        obj_preds,
                        "cpu",
                    )

                torch.cuda.empty_cache()
                num_fg += num_fg_img

                cls_target = F.one_hot(
                    gt_matched_classes.to(torch.int64), self.num_classes
                ) * pred_ious_this_matching.unsqueeze(-1)
                obj_target = fg_mask.unsqueeze(-1)
                reg_target = gt_bboxes_per_image[matched_gt_inds]
                if self.use_l1:
                    l1_target = self.get_l1_target(
                        outputs.new_zeros((num_fg_img, 4)),
                        gt_bboxes_per_image[matched_gt_inds],
                        expanded_strides[0][fg_mask],
                        x_shifts=x_shifts[0][fg_mask],
                        y_shifts=y_shifts[0][fg_mask],
                    )

            cls_targets.append(cls_target)
            reg_targets.append(reg_target)
            obj_targets.append(obj_target.to(dtype))
            fg_masks.append(fg_mask)
            if self.use_l1:
                l1_targets.append(l1_target)

        cls_targets = torch.cat(cls_targets, 0)
        reg_targets = torch.cat(reg_targets, 0)
        obj_targets = torch.cat(obj_targets, 0)
        fg_masks = torch.cat(fg_masks, 0)
        if self.use_l1:
            l1_targets = torch.cat(l1_targets, 0)

        num_fg = max(num_fg, 1)
        loss_iou = (
            self.iou_loss(bbox_preds.view(-1, 4)[fg_masks], reg_targets)
        ).sum() / num_fg
        loss_obj = (
            self.bcewithlog_loss(obj_preds.view(-1, 1), obj_targets)
        ).sum() / num_fg
        loss_cls = (
            self.bcewithlog_loss(
                cls_preds.view(-1, self.num_classes)[fg_masks], cls_targets
            )
        ).sum() / num_fg
        if self.use_l1:
            loss_l1 = (
                self.l1_loss(origin_preds.view(-1, 4)[fg_masks], l1_targets)
            ).sum() / num_fg
        else:
            loss_l1 = 0.0

        reg_weight = 5.0
        loss = reg_weight * loss_iou + loss_obj + loss_cls + loss_l1

        return (
            loss,
            reg_weight * loss_iou,
            loss_obj,
            loss_cls,
            loss_l1,
            num_fg / max(num_gts, 1),
        )

    def get_l1_target(self, l1_target, gt, stride, x_shifts, y_shifts, eps=1e-8):
        l1_target[:, 0] = gt[:, 0] / stride - x_shifts
        l1_target[:, 1] = gt[:, 1] / stride - y_shifts
        l1_target[:, 2] = torch.log(gt[:, 2] / stride + eps)
        l1_target[:, 3] = torch.log(gt[:, 3] / stride + eps)
        return l1_target

    @torch.no_grad()
    def get_assignments(
        self,
        batch_idx,
        num_gt,
        gt_bboxes_per_image,
        gt_classes,
        bboxes_preds_per_image,
        expanded_strides,
        x_shifts,
        y_shifts,
        cls_preds,
        obj_preds,
        mode="cpu",
    ):
        if mode == "cpu":
            # print("-----------Using CPU for the Current Batch-------------")
            gt_bboxes_per_image = gt_bboxes_per_image.cpu().float()
            bboxes_preds_per_image = bboxes_preds_per_image.cpu().float()
            gt_classes = gt_classes.cpu().float()
            expanded_strides = expanded_strides.cpu().float()
            x_shifts = x_shifts.cpu()
            y_shifts = y_shifts.cpu()

        fg_mask, geometry_relation = self.get_geometry_constraint(
            gt_bboxes_per_image,
            expanded_strides,
            x_shifts,
            y_shifts,
        )

        bboxes_preds_per_image = bboxes_preds_per_image[fg_mask]
        cls_preds_ = cls_preds[batch_idx][fg_mask]
        obj_preds_ = obj_preds[batch_idx][fg_mask]
        num_in_boxes_anchor = bboxes_preds_per_image.shape[0]

        if mode == "cpu":
            gt_bboxes_per_image = gt_bboxes_per_image.cpu()
            bboxes_preds_per_image = bboxes_preds_per_image.cpu()

        pair_wise_ious = bboxes_iou(gt_bboxes_per_image, bboxes_preds_per_image, False)

        gt_cls_per_image = F.one_hot(
            gt_classes.to(torch.int64), self.num_classes
        ).float()
        pair_wise_ious_loss = -torch.log(pair_wise_ious + 1e-8)

        if mode == "cpu":
            cls_preds_, obj_preds_ = cls_preds_.cpu(), obj_preds_.cpu()

        with torch.cuda.amp.autocast(enabled=False):
            cls_preds_ = (
                cls_preds_.float().sigmoid_() * obj_preds_.float().sigmoid_()
            ).sqrt()
            pair_wise_cls_loss = F.binary_cross_entropy(
                cls_preds_.unsqueeze(0).repeat(num_gt, 1, 1),
                gt_cls_per_image.unsqueeze(1).repeat(1, num_in_boxes_anchor, 1),
                reduction="none",
            ).sum(-1)
        del cls_preds_

        cost = (
            pair_wise_cls_loss
            + 3.0 * pair_wise_ious_loss
            + float(1e6) * (~geometry_relation)
        )

        (
            num_fg,
            gt_matched_classes,
            pred_ious_this_matching,
            matched_gt_inds,
        ) = self.simota_matching(cost, pair_wise_ious, gt_classes, num_gt, fg_mask)
        del pair_wise_cls_loss, cost, pair_wise_ious, pair_wise_ious_loss

        # if mode == "cpu":
        #     gt_matched_classes = gt_matched_classes.cuda()
        #     fg_mask = fg_mask.cuda()
        #     pred_ious_this_matching = pred_ious_this_matching.cuda()
        #     matched_gt_inds = matched_gt_inds.cuda()

        return (
            gt_matched_classes,
            fg_mask,
            pred_ious_this_matching,
            matched_gt_inds,
            num_fg,
        )

    def get_geometry_constraint(
        self,
        gt_bboxes_per_image,
        expanded_strides,
        x_shifts,
        y_shifts,
    ):
        """
        Calculate whether the center of an object is located in a fixed range of
        an anchor. This is used to avert inappropriate matching. It can also reduce
        the number of candidate anchors so that the GPU memory is saved.
        """
        expanded_strides_per_image = expanded_strides[0]
        x_centers_per_image = (
            (x_shifts[0] + 0.5) * expanded_strides_per_image
        ).unsqueeze(0)
        y_centers_per_image = (
            (y_shifts[0] + 0.5) * expanded_strides_per_image
        ).unsqueeze(0)

        # in fixed center
        center_radius = 1.5
        center_dist = expanded_strides_per_image.unsqueeze(0) * center_radius
        gt_bboxes_per_image_l = (gt_bboxes_per_image[:, 0:1]) - center_dist
        gt_bboxes_per_image_r = (gt_bboxes_per_image[:, 0:1]) + center_dist
        gt_bboxes_per_image_t = (gt_bboxes_per_image[:, 1:2]) - center_dist
        gt_bboxes_per_image_b = (gt_bboxes_per_image[:, 1:2]) + center_dist

        c_l = x_centers_per_image - gt_bboxes_per_image_l
        c_r = gt_bboxes_per_image_r - x_centers_per_image
        c_t = y_centers_per_image - gt_bboxes_per_image_t
        c_b = gt_bboxes_per_image_b - y_centers_per_image
        center_deltas = torch.stack([c_l, c_t, c_r, c_b], 2)
        is_in_centers = center_deltas.min(dim=-1).values > 0.0
        anchor_filter = is_in_centers.sum(dim=0) > 0
        geometry_relation = is_in_centers[:, anchor_filter]

        return anchor_filter, geometry_relation

    def simota_matching(self, cost, pair_wise_ious, gt_classes, num_gt, fg_mask):
        # Dynamic K
        # ---------------------------------------------------------------
        matching_matrix = torch.zeros_like(cost, dtype=torch.uint8)

        n_candidate_k = min(10, pair_wise_ious.size(1))
        topk_ious, _ = torch.topk(pair_wise_ious, n_candidate_k, dim=1)
        dynamic_ks = torch.clamp(topk_ious.sum(1).int(), min=1)
        for gt_idx in range(num_gt):
            _, pos_idx = torch.topk(cost[gt_idx], k=dynamic_ks[gt_idx], largest=False)
            matching_matrix[gt_idx][pos_idx] = 1

        del topk_ious, dynamic_ks, pos_idx

        anchor_matching_gt = matching_matrix.sum(0)
        # deal with the case that one anchor matches multiple ground-truths
        if anchor_matching_gt.max() > 1:
            multiple_match_mask = anchor_matching_gt > 1
            _, cost_argmin = torch.min(cost[:, multiple_match_mask], dim=0)
            matching_matrix[:, multiple_match_mask] *= 0
            matching_matrix[cost_argmin, multiple_match_mask] = 1
        fg_mask_inboxes = anchor_matching_gt > 0
        num_fg = fg_mask_inboxes.sum().item()

        fg_mask[fg_mask.clone()] = fg_mask_inboxes

        matched_gt_inds = matching_matrix[:, fg_mask_inboxes].argmax(0)
        gt_matched_classes = gt_classes[matched_gt_inds]

        pred_ious_this_matching = (matching_matrix * pair_wise_ious).sum(0)[
            fg_mask_inboxes
        ]
        return num_fg, gt_matched_classes, pred_ious_this_matching, matched_gt_inds
