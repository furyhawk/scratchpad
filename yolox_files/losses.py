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

import torch
import torch.nn as nn


class IOUloss(nn.Module):
    def __init__(self, reduction="none", loss_type="iou"):
        super().__init__()
        self.reduction = reduction
        self.loss_type = loss_type

    def forward(self, pred, target):
        assert pred.shape[0] == target.shape[0]

        if pred.type().startswith("torch.mps") or target.type().startswith("torch.mps"):
            pred = pred.view(-1, 4).to("cpu")
            target = target.view(-1, 4).to("cpu")
        else:
            pred = pred.view(-1, 4)
            target = target.view(-1, 4)

        tl = torch.max(
            (pred[:, :2] - pred[:, 2:] / 2), (target[:, :2] - target[:, 2:] / 2)
        )
        br = torch.min(
            (pred[:, :2] + pred[:, 2:] / 2), (target[:, :2] + target[:, 2:] / 2)
        )

        area_p = torch.prod(pred[:, 2:], 1)
        area_g = torch.prod(target[:, 2:], 1)

        if tl.type().startswith("torch.mps"):
            en = (tl < br).type("torch.FloatTensor").prod(dim=1).to("cpu")
        else:
            en = (tl < br).type(tl.type()).prod(dim=1)

        area_i = torch.prod(br - tl, 1) * en
        area_u = area_p + area_g - area_i
        iou = (area_i) / (area_u + 1e-16)

        if self.loss_type == "iou":
            loss = 1 - iou**2
        elif self.loss_type == "giou":
            c_tl = torch.min(
                (pred[:, :2] - pred[:, 2:] / 2), (target[:, :2] - target[:, 2:] / 2)
            )
            c_br = torch.max(
                (pred[:, :2] + pred[:, 2:] / 2), (target[:, :2] + target[:, 2:] / 2)
            )
            area_c = torch.prod(c_br - c_tl, 1)
            giou = iou - (area_c - area_u) / area_c.clamp(1e-16)
            loss = 1 - giou.clamp(min=-1.0, max=1.0)

        if self.reduction == "mean":
            loss = loss.mean()
        elif self.reduction == "sum":
            loss = loss.sum()

        return loss


# def get_losses(
#     imgs,
#     x_shifts,
#     y_shifts,
#     expanded_strides,
#     labels,
#     outputs,
#     origin_preds,
#     dtype,
#     num_classes,
# ):
#     use_l1 = False

#     bbox_preds = outputs[:, :, :4]  # [batch, n_anchors_all, 4]
#     obj_preds = outputs[:, :, 4:5]  # [batch, n_anchors_all, 1]
#     cls_preds = outputs[:, :, 5:]  # [batch, n_anchors_all, n_cls]

#     # calculate targets
#     nlabel = (labels.sum(dim=2) > 0).sum(dim=1)  # number of objects

#     total_num_anchors = outputs.shape[1]
#     x_shifts = torch.cat(x_shifts, 1)  # [1, n_anchors_all]
#     y_shifts = torch.cat(y_shifts, 1)  # [1, n_anchors_all]
#     expanded_strides = torch.cat(expanded_strides, 1)
#     if use_l1:
#         origin_preds = torch.cat(origin_preds, 1)

#     cls_targets = []
#     reg_targets = []
#     l1_targets = []
#     obj_targets = []
#     fg_masks = []

#     num_fg = 0.0
#     num_gts = 0.0

#     for batch_idx in range(outputs.shape[0]):
#         num_gt = int(nlabel[batch_idx])
#         num_gts += num_gt
#         if num_gt == 0:
#             cls_target = outputs.new_zeros((0, num_classes))
#             reg_target = outputs.new_zeros((0, 4))
#             l1_target = outputs.new_zeros((0, 4))
#             obj_target = outputs.new_zeros((total_num_anchors, 1))
#             fg_mask = outputs.new_zeros(total_num_anchors).bool()
#         else:
#             gt_bboxes_per_image = labels[batch_idx, :num_gt, 1:5]
#             gt_classes = labels[batch_idx, :num_gt, 0]
#             bboxes_preds_per_image = bbox_preds[batch_idx]

#             try:
#                 (
#                     gt_matched_classes,
#                     fg_mask,
#                     pred_ious_this_matching,
#                     matched_gt_inds,
#                     num_fg_img,
#                 ) = get_assignments(  # noqa
#                     batch_idx,
#                     num_gt,
#                     gt_bboxes_per_image,
#                     gt_classes,
#                     bboxes_preds_per_image,
#                     expanded_strides,
#                     x_shifts,
#                     y_shifts,
#                     cls_preds,
#                     obj_preds,
#                 )
#             except RuntimeError as e:
#                 # TODO: the string might change, consider a better way
#                 if "CUDA out of memory. " not in str(e):
#                     raise  # RuntimeError might not caused by CUDA OOM

#                 logger.error(
#                     "OOM RuntimeError is raised due to the huge memory cost during label assignment. \
#                         CPU mode is applied in this batch. If you want to avoid this issue, \
#                         try to reduce the batch size or image size."
#                 )
#                 torch.cuda.empty_cache()
#                 (
#                     gt_matched_classes,
#                     fg_mask,
#                     pred_ious_this_matching,
#                     matched_gt_inds,
#                     num_fg_img,
#                 ) = get_assignments(  # noqa
#                     batch_idx,
#                     num_gt,
#                     gt_bboxes_per_image,
#                     gt_classes,
#                     bboxes_preds_per_image,
#                     expanded_strides,
#                     x_shifts,
#                     y_shifts,
#                     cls_preds,
#                     obj_preds,
#                     "cpu",
#                 )

#             torch.cuda.empty_cache()
#             num_fg += num_fg_img

#             cls_target = F.one_hot(
#                 gt_matched_classes.to(torch.int64), num_classes
#             ) * pred_ious_this_matching.unsqueeze(-1)
#             obj_target = fg_mask.unsqueeze(-1)
#             reg_target = gt_bboxes_per_image[matched_gt_inds]
#             # if self.use_l1:
#             #     l1_target = self.get_l1_target(
#             #         outputs.new_zeros((num_fg_img, 4)),
#             #         gt_bboxes_per_image[matched_gt_inds],
#             #         expanded_strides[0][fg_mask],
#             #         x_shifts=x_shifts[0][fg_mask],
#             #         y_shifts=y_shifts[0][fg_mask],
#             #     )

#         cls_targets.append(cls_target)
#         reg_targets.append(reg_target)
#         obj_targets.append(obj_target.to(dtype))
#         fg_masks.append(fg_mask)
#         if use_l1:
#             l1_targets.append(l1_target)

#     cls_targets = torch.cat(cls_targets, 0)
#     reg_targets = torch.cat(reg_targets, 0)
#     obj_targets = torch.cat(obj_targets, 0)
#     fg_masks = torch.cat(fg_masks, 0)
#     if use_l1:
#         l1_targets = torch.cat(l1_targets, 0)

#     num_fg = max(num_fg, 1)
#     loss_iou = (
#         self.iou_loss(bbox_preds.view(-1, 4)[fg_masks], reg_targets)
#     ).sum() / num_fg
#     loss_obj = (self.bcewithlog_loss(obj_preds.view(-1, 1), obj_targets)).sum() / num_fg
#     loss_cls = (
#         self.bcewithlog_loss(
#             cls_preds.view(-1, self.num_classes)[fg_masks], cls_targets
#         )
#     ).sum() / num_fg
#     if self.use_l1:
#         loss_l1 = (
#             self.l1_loss(origin_preds.view(-1, 4)[fg_masks], l1_targets)
#         ).sum() / num_fg
#     else:
#         loss_l1 = 0.0

#     reg_weight = 5.0
#     loss = reg_weight * loss_iou + loss_obj + loss_cls + loss_l1

#     return (
#         loss,
#         reg_weight * loss_iou,
#         loss_obj,
#         loss_cls,
#         loss_l1,
#         num_fg / max(num_gts, 1),
#     )


# def get_l1_target(l1_target, gt, stride, x_shifts, y_shifts, eps=1e-8):
#     l1_target[:, 0] = gt[:, 0] / stride - x_shifts
#     l1_target[:, 1] = gt[:, 1] / stride - y_shifts
#     l1_target[:, 2] = torch.log(gt[:, 2] / stride + eps)
#     l1_target[:, 3] = torch.log(gt[:, 3] / stride + eps)
#     return l1_target


# @torch.no_grad()
# def get_assignments(
#     batch_idx,
#     num_gt,
#     gt_bboxes_per_image,
#     gt_classes,
#     bboxes_preds_per_image,
#     expanded_strides,
#     x_shifts,
#     y_shifts,
#     cls_preds,
#     obj_preds,
#     mode="gpu",
# ):
#     if mode == "cpu":
#         print("-----------Using CPU for the Current Batch-------------")
#         gt_bboxes_per_image = gt_bboxes_per_image.cpu().float()
#         bboxes_preds_per_image = bboxes_preds_per_image.cpu().float()
#         gt_classes = gt_classes.cpu().float()
#         expanded_strides = expanded_strides.cpu().float()
#         x_shifts = x_shifts.cpu()
#         y_shifts = y_shifts.cpu()

#     fg_mask, geometry_relation = get_geometry_constraint(
#         gt_bboxes_per_image,
#         expanded_strides,
#         x_shifts,
#         y_shifts,
#     )

#     bboxes_preds_per_image = bboxes_preds_per_image[fg_mask]
#     cls_preds_ = cls_preds[batch_idx][fg_mask]
#     obj_preds_ = obj_preds[batch_idx][fg_mask]
#     num_in_boxes_anchor = bboxes_preds_per_image.shape[0]

#     if mode == "cpu":
#         gt_bboxes_per_image = gt_bboxes_per_image.cpu()
#         bboxes_preds_per_image = bboxes_preds_per_image.cpu()

#     pair_wise_ious = bboxes_iou(gt_bboxes_per_image, bboxes_preds_per_image, False)

#     gt_cls_per_image = F.one_hot(gt_classes.to(torch.int64), self.num_classes).float()
#     pair_wise_ious_loss = -torch.log(pair_wise_ious + 1e-8)

#     if mode == "cpu":
#         cls_preds_, obj_preds_ = cls_preds_.cpu(), obj_preds_.cpu()

#     with torch.cuda.amp.autocast(enabled=False):
#         cls_preds_ = (
#             cls_preds_.float().sigmoid_() * obj_preds_.float().sigmoid_()
#         ).sqrt()
#         pair_wise_cls_loss = F.binary_cross_entropy(
#             cls_preds_.unsqueeze(0).repeat(num_gt, 1, 1),
#             gt_cls_per_image.unsqueeze(1).repeat(1, num_in_boxes_anchor, 1),
#             reduction="none",
#         ).sum(-1)
#     del cls_preds_

#     cost = (
#         pair_wise_cls_loss
#         + 3.0 * pair_wise_ious_loss
#         + float(1e6) * (~geometry_relation)
#     )

#     (
#         num_fg,
#         gt_matched_classes,
#         pred_ious_this_matching,
#         matched_gt_inds,
#     ) = simota_matching(cost, pair_wise_ious, gt_classes, num_gt, fg_mask)
#     del pair_wise_cls_loss, cost, pair_wise_ious, pair_wise_ious_loss

#     if mode == "cpu":
#         gt_matched_classes = gt_matched_classes.cuda()
#         fg_mask = fg_mask.cuda()
#         pred_ious_this_matching = pred_ious_this_matching.cuda()
#         matched_gt_inds = matched_gt_inds.cuda()

#     return (
#         gt_matched_classes,
#         fg_mask,
#         pred_ious_this_matching,
#         matched_gt_inds,
#         num_fg,
#     )


# def get_geometry_constraint(
#     gt_bboxes_per_image,
#     expanded_strides,
#     x_shifts,
#     y_shifts,
# ):
#     """
#     Calculate whether the center of an object is located in a fixed range of
#     an anchor. This is used to avert inappropriate matching. It can also reduce
#     the number of candidate anchors so that the GPU memory is saved.
#     """
#     expanded_strides_per_image = expanded_strides[0]
#     x_centers_per_image = ((x_shifts[0] + 0.5) * expanded_strides_per_image).unsqueeze(
#         0
#     )
#     y_centers_per_image = ((y_shifts[0] + 0.5) * expanded_strides_per_image).unsqueeze(
#         0
#     )

#     # in fixed center
#     center_radius = 1.5
#     center_dist = expanded_strides_per_image.unsqueeze(0) * center_radius
#     gt_bboxes_per_image_l = (gt_bboxes_per_image[:, 0:1]) - center_dist
#     gt_bboxes_per_image_r = (gt_bboxes_per_image[:, 0:1]) + center_dist
#     gt_bboxes_per_image_t = (gt_bboxes_per_image[:, 1:2]) - center_dist
#     gt_bboxes_per_image_b = (gt_bboxes_per_image[:, 1:2]) + center_dist

#     c_l = x_centers_per_image - gt_bboxes_per_image_l
#     c_r = gt_bboxes_per_image_r - x_centers_per_image
#     c_t = y_centers_per_image - gt_bboxes_per_image_t
#     c_b = gt_bboxes_per_image_b - y_centers_per_image
#     center_deltas = torch.stack([c_l, c_t, c_r, c_b], 2)
#     is_in_centers = center_deltas.min(dim=-1).values > 0.0
#     anchor_filter = is_in_centers.sum(dim=0) > 0
#     geometry_relation = is_in_centers[:, anchor_filter]

#     return anchor_filter, geometry_relation


# def simota_matching(cost, pair_wise_ious, gt_classes, num_gt, fg_mask):
#     # Dynamic K
#     # ---------------------------------------------------------------
#     matching_matrix = torch.zeros_like(cost, dtype=torch.uint8)

#     n_candidate_k = min(10, pair_wise_ious.size(1))
#     topk_ious, _ = torch.topk(pair_wise_ious, n_candidate_k, dim=1)
#     dynamic_ks = torch.clamp(topk_ious.sum(1).int(), min=1)
#     for gt_idx in range(num_gt):
#         _, pos_idx = torch.topk(cost[gt_idx], k=dynamic_ks[gt_idx], largest=False)
#         matching_matrix[gt_idx][pos_idx] = 1

#     del topk_ious, dynamic_ks, pos_idx

#     anchor_matching_gt = matching_matrix.sum(0)
#     # deal with the case that one anchor matches multiple ground-truths
#     if anchor_matching_gt.max() > 1:
#         multiple_match_mask = anchor_matching_gt > 1
#         _, cost_argmin = torch.min(cost[:, multiple_match_mask], dim=0)
#         matching_matrix[:, multiple_match_mask] *= 0
#         matching_matrix[cost_argmin, multiple_match_mask] = 1
#     fg_mask_inboxes = anchor_matching_gt > 0
#     num_fg = fg_mask_inboxes.sum().item()

#     fg_mask[fg_mask.clone()] = fg_mask_inboxes

#     matched_gt_inds = matching_matrix[:, fg_mask_inboxes].argmax(0)
#     gt_matched_classes = gt_classes[matched_gt_inds]

#     pred_ious_this_matching = (matching_matrix * pair_wise_ious).sum(0)[fg_mask_inboxes]
#     return num_fg, gt_matched_classes, pred_ious_this_matching, matched_gt_inds
