/*
 Navicat Premium Dump SQL

 Source Server         : holo_analysis
 Source Server Type    : MySQL
 Source Server Version : 80013 (8.0.13)
 Source Host           : localhost:3306
 Source Schema         : holo_analysis_sys

 Target Server Type    : MySQL
 Target Server Version : 80013 (8.0.13)
 File Encoding         : 65001

 Date: 03/04/2026 22:13:30
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for features
-- ----------------------------
DROP TABLE IF EXISTS `features`;
CREATE TABLE `features`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `hole_id` int(11) NULL DEFAULT NULL,
  `volume` double(11, 6) NULL DEFAULT NULL,
  `surface_area` double(11, 6) NULL DEFAULT NULL,
  `equivalent_diameter` double(11, 6) NULL DEFAULT NULL,
  `sphericity` double(11, 6) NULL DEFAULT NULL,
  `rectangularity` double(11, 6) NULL DEFAULT NULL,
  `aspect_ratio` double(11, 6) NULL DEFAULT NULL,
  `long_edge` double(11, 6) NULL DEFAULT NULL,
  `center_distance` double(11, 6) NULL DEFAULT NULL,
  `operation_id` int(11) NULL DEFAULT NULL,
  `analysis_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `project_id`(`project_id` ASC) USING BTREE,
  INDEX `operation_id`(`operation_id` ASC) USING BTREE,
  CONSTRAINT `features_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `features_ibfk_2` FOREIGN KEY (`operation_id`) REFERENCES `operation_logs` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of features
-- ----------------------------

-- ----------------------------
-- Table structure for hole_data
-- ----------------------------
DROP TABLE IF EXISTS `hole_data`;
CREATE TABLE `hole_data`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `total_number_of_voids` int(11) NOT NULL,
  `void_space_density` double(11, 6) NULL DEFAULT NULL,
  `total_void_volume` double(11, 6) NULL DEFAULT NULL,
  `total_void_surface_area` double(11, 6) NULL DEFAULT NULL,
  `maximum_volume` double(11, 6) NULL DEFAULT NULL,
  `mean_volume` double(11, 6) NULL DEFAULT NULL,
  `minimum_volume` double(11, 6) NULL DEFAULT NULL,
  `maximum_surface_area` double(11, 6) NULL DEFAULT NULL,
  `mean_surface_area` double(11, 6) NULL DEFAULT NULL,
  `minimum_surface_area` double(11, 6) NULL DEFAULT NULL,
  `maximum_equivalent_diameter` double(11, 6) NULL DEFAULT NULL,
  `mean_equivalent_diameter` double(11, 6) NULL DEFAULT NULL,
  `minimum_equivalent_diameter` double(11, 6) NULL DEFAULT NULL,
  `maximum_sphericity` double(11, 6) NULL DEFAULT NULL,
  `mean_sphericity` double(11, 6) NULL DEFAULT NULL,
  `minimum_sphericity` double(11, 6) NULL DEFAULT NULL,
  `maximum_rectangularity` double(11, 6) NULL DEFAULT NULL,
  `mean_rectangularity` double(11, 6) NULL DEFAULT NULL,
  `minimum_rectangularity` double(11, 6) NULL DEFAULT NULL,
  `maximum_aspect_ratio` double(11, 6) NULL DEFAULT NULL,
  `mean_aspect_ratio` double(11, 6) NULL DEFAULT NULL,
  `minimum_aspect_ratio` double(11, 6) NULL DEFAULT NULL,
  `maximum_long_edge` double(11, 6) NULL DEFAULT NULL,
  `mean_long_edge` double(11, 6) NULL DEFAULT NULL,
  `minimum_long_edge` double(11, 6) NULL DEFAULT NULL,
  `maximum_center_distance` double(11, 6) NULL DEFAULT NULL,
  `mean_center_distance` double(11, 6) NULL DEFAULT NULL,
  `minimum_center_distance` double(11, 6) NULL DEFAULT NULL,
  `maximum_void_volume_fraction` double(11, 6) NULL DEFAULT NULL,
  `volume_coefficient_of_variation` double(11, 6) NULL DEFAULT NULL,
  `volume_gini_coefficient` double(11, 6) NULL DEFAULT NULL,
  `maximum_volume_jump_ratio` double(11, 6) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `project_id`(`project_id` ASC) USING BTREE,
  CONSTRAINT `hole_data_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of hole_data
-- ----------------------------

-- ----------------------------
-- Table structure for operation_logs
-- ----------------------------
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `project_id` int(11) NULL DEFAULT NULL,
  `operation_type` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `operation_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `project_id`(`project_id` ASC) USING BTREE,
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `operation_logs_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2983 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of operation_logs
-- ----------------------------
INSERT INTO `operation_logs` VALUES (2744, 2, 14, 'FILE_UPLOAD_BATCH', 'success', '2026-01-17 19:13:28');
INSERT INTO `operation_logs` VALUES (2746, 2, NULL, '用户登入', 'success', '2026-01-17 20:12:54');
INSERT INTO `operation_logs` VALUES (2747, 2, NULL, '用户登入', 'success', '2026-01-17 20:32:59');
INSERT INTO `operation_logs` VALUES (2748, 2, 14, 'HOLE_DETECTION', 'success', '2026-01-17 20:34:40');
INSERT INTO `operation_logs` VALUES (2749, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-01-17 20:59:41');
INSERT INTO `operation_logs` VALUES (2750, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 21:24:47');
INSERT INTO `operation_logs` VALUES (2751, 2, NULL, '用户登入', 'success', '2026-01-17 21:26:49');
INSERT INTO `operation_logs` VALUES (2752, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 21:26:56');
INSERT INTO `operation_logs` VALUES (2753, 2, NULL, '用户登入', 'success', '2026-01-17 21:32:48');
INSERT INTO `operation_logs` VALUES (2754, 2, NULL, '用户登入', 'success', '2026-01-17 21:34:59');
INSERT INTO `operation_logs` VALUES (2755, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 21:35:07');
INSERT INTO `operation_logs` VALUES (2756, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 21:37:12');
INSERT INTO `operation_logs` VALUES (2757, 2, NULL, '用户登入', 'success', '2026-01-17 21:44:36');
INSERT INTO `operation_logs` VALUES (2758, 2, NULL, '用户登入', 'success', '2026-01-17 22:04:34');
INSERT INTO `operation_logs` VALUES (2759, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 22:04:40');
INSERT INTO `operation_logs` VALUES (2760, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 22:17:36');
INSERT INTO `operation_logs` VALUES (2761, 2, NULL, '用户登入', 'success', '2026-01-17 22:17:47');
INSERT INTO `operation_logs` VALUES (2762, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 22:17:59');
INSERT INTO `operation_logs` VALUES (2763, 2, NULL, '用户登入', 'success', '2026-01-17 22:33:29');
INSERT INTO `operation_logs` VALUES (2764, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 22:33:35');
INSERT INTO `operation_logs` VALUES (2765, 2, NULL, '用户登入', 'success', '2026-01-17 22:44:04');
INSERT INTO `operation_logs` VALUES (2766, 2, NULL, '用户登入', 'success', '2026-01-17 22:45:03');
INSERT INTO `operation_logs` VALUES (2767, 2, NULL, '用户登入', 'success', '2026-01-17 22:46:21');
INSERT INTO `operation_logs` VALUES (2768, 2, NULL, '用户登入', 'success', '2026-01-17 22:47:07');
INSERT INTO `operation_logs` VALUES (2769, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 22:47:15');
INSERT INTO `operation_logs` VALUES (2770, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 23:07:43');
INSERT INTO `operation_logs` VALUES (2771, 2, NULL, '用户登入', 'success', '2026-01-17 23:33:29');
INSERT INTO `operation_logs` VALUES (2772, 2, NULL, '用户登入', 'success', '2026-01-17 23:36:25');
INSERT INTO `operation_logs` VALUES (2773, 2, NULL, '用户登入', 'success', '2026-01-17 23:38:29');
INSERT INTO `operation_logs` VALUES (2774, 2, NULL, '用户登入', 'success', '2026-01-17 23:39:51');
INSERT INTO `operation_logs` VALUES (2775, 2, 14, 'TARGET_SLICING', 'started', '2026-01-17 23:39:58');
INSERT INTO `operation_logs` VALUES (2776, 2, 14, 'MAX_HOLE_3D_VIEW', 'success', '2026-01-17 23:42:29');
INSERT INTO `operation_logs` VALUES (2777, 2, NULL, '用户登入', 'success', '2026-01-18 14:26:46');
INSERT INTO `operation_logs` VALUES (2778, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:26:55');
INSERT INTO `operation_logs` VALUES (2779, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:37:00');
INSERT INTO `operation_logs` VALUES (2780, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:40:14');
INSERT INTO `operation_logs` VALUES (2781, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:47:04');
INSERT INTO `operation_logs` VALUES (2782, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:53:29');
INSERT INTO `operation_logs` VALUES (2783, 2, NULL, '用户登入', 'success', '2026-01-18 14:54:08');
INSERT INTO `operation_logs` VALUES (2784, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:54:15');
INSERT INTO `operation_logs` VALUES (2785, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:56:38');
INSERT INTO `operation_logs` VALUES (2786, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:56:58');
INSERT INTO `operation_logs` VALUES (2787, 2, NULL, '用户登入', 'success', '2026-01-18 14:57:47');
INSERT INTO `operation_logs` VALUES (2788, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 14:58:28');
INSERT INTO `operation_logs` VALUES (2789, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 15:03:49');
INSERT INTO `operation_logs` VALUES (2790, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 15:04:12');
INSERT INTO `operation_logs` VALUES (2791, 2, NULL, '用户登入', 'success', '2026-01-18 15:04:51');
INSERT INTO `operation_logs` VALUES (2792, 2, 14, 'TARGET_SLICING', 'started', '2026-01-18 15:04:58');
INSERT INTO `operation_logs` VALUES (2793, 2, NULL, '用户登入', 'success', '2026-01-18 15:09:47');
INSERT INTO `operation_logs` VALUES (2794, 2, NULL, '用户登出', 'success', '2026-01-18 15:09:54');
INSERT INTO `operation_logs` VALUES (2795, 2, NULL, '用户登出', 'success', '2026-01-18 15:09:54');
INSERT INTO `operation_logs` VALUES (2796, 1, NULL, '用户登入', 'success', '2026-01-18 15:10:01');
INSERT INTO `operation_logs` VALUES (2797, 1, NULL, 'PROJECT_DELETE', 'success', '2026-01-18 15:10:53');
INSERT INTO `operation_logs` VALUES (2798, 1, 15, 'PROJECT_CREATE', 'success', '2026-01-18 15:11:06');
INSERT INTO `operation_logs` VALUES (2799, 1, NULL, '用户登入', 'success', '2026-01-18 17:17:15');
INSERT INTO `operation_logs` VALUES (2800, 1, NULL, 'PROJECT_CREATE', 'success', '2026-01-18 17:17:47');
INSERT INTO `operation_logs` VALUES (2801, 1, NULL, '用户登入', 'success', '2026-01-18 17:28:10');
INSERT INTO `operation_logs` VALUES (2802, 1, NULL, 'PROJECT_DELETE', 'success', '2026-01-18 17:28:37');
INSERT INTO `operation_logs` VALUES (2803, 1, 17, 'PROJECT_CREATE', 'success', '2026-01-18 17:30:26');
INSERT INTO `operation_logs` VALUES (2804, 1, NULL, '用户登入', 'success', '2026-01-18 17:36:00');
INSERT INTO `operation_logs` VALUES (2805, 1, NULL, 'TEST_LOGIN', 'success', '2026-01-18 17:38:31');
INSERT INTO `operation_logs` VALUES (2806, 1, NULL, '用户登入', 'success', '2026-01-18 18:19:26');
INSERT INTO `operation_logs` VALUES (2807, 1, NULL, '用户登入', 'success', '2026-01-18 18:28:01');
INSERT INTO `operation_logs` VALUES (2808, 1, NULL, '用户登出', 'success', '2026-01-18 18:33:46');
INSERT INTO `operation_logs` VALUES (2809, 1, NULL, '用户登出', 'success', '2026-01-18 18:33:46');
INSERT INTO `operation_logs` VALUES (2810, 2, NULL, '用户登入', 'success', '2026-01-18 18:34:04');
INSERT INTO `operation_logs` VALUES (2811, 2, 18, 'PROJECT_CREATE', 'success', '2026-01-18 18:36:29');
INSERT INTO `operation_logs` VALUES (2812, 1, NULL, '用户登入', 'success', '2026-01-18 18:37:12');
INSERT INTO `operation_logs` VALUES (2813, 1, NULL, 'USER_REGISTER', 'success', '2026-01-18 18:37:44');
INSERT INTO `operation_logs` VALUES (2814, 2, 14, 'FILE_UPLOAD_BATCH', 'success', '2026-01-18 18:39:30');
INSERT INTO `operation_logs` VALUES (2815, 2, 14, 'BINARY_CONVERSION', 'success', '2026-01-18 18:40:52');
INSERT INTO `operation_logs` VALUES (2816, 1, NULL, '用户登入', 'success', '2026-01-18 23:21:16');
INSERT INTO `operation_logs` VALUES (2817, 1, NULL, '用户登入', 'success', '2026-01-20 14:14:08');
INSERT INTO `operation_logs` VALUES (2818, 1, 19, 'PROJECT_CREATE', 'success', '2026-01-20 14:17:31');
INSERT INTO `operation_logs` VALUES (2819, 2, NULL, '用户登入', 'failed', '2026-03-10 18:14:25');
INSERT INTO `operation_logs` VALUES (2820, 2, NULL, '用户登入', 'failed', '2026-03-10 18:14:32');
INSERT INTO `operation_logs` VALUES (2821, 2, NULL, '用户登入', 'success', '2026-03-10 18:37:33');
INSERT INTO `operation_logs` VALUES (2822, 2, 14, 'MASK_RCNN_DETECTION', 'success', '2026-03-10 18:37:58');
INSERT INTO `operation_logs` VALUES (2823, 2, NULL, '用户登入', 'success', '2026-03-10 20:24:28');
INSERT INTO `operation_logs` VALUES (2824, 2, 14, 'MASK_RCNN_DETECTION', 'success', '2026-03-10 20:24:50');
INSERT INTO `operation_logs` VALUES (2825, 2, NULL, '用户登入', 'success', '2026-03-10 21:03:18');
INSERT INTO `operation_logs` VALUES (2826, 2, NULL, '用户登入', 'success', '2026-03-10 21:10:20');
INSERT INTO `operation_logs` VALUES (2827, 2, 14, 'MASK_RCNN_DETECTION', 'success', '2026-03-10 21:15:28');
INSERT INTO `operation_logs` VALUES (2828, 2, NULL, '用户登入', 'success', '2026-03-13 13:49:54');
INSERT INTO `operation_logs` VALUES (2829, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-13 13:50:24');
INSERT INTO `operation_logs` VALUES (2830, 2, NULL, '用户登入', 'success', '2026-03-23 13:56:11');
INSERT INTO `operation_logs` VALUES (2831, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-23 13:56:22');
INSERT INTO `operation_logs` VALUES (2832, 2, NULL, '用户登入', 'success', '2026-03-25 18:27:56');
INSERT INTO `operation_logs` VALUES (2833, 2, NULL, '用户登入', 'success', '2026-03-25 20:33:30');
INSERT INTO `operation_logs` VALUES (2834, 2, 14, '3D_MODEL_CONSTRUCTION', 'failed', '2026-03-25 20:33:37');
INSERT INTO `operation_logs` VALUES (2835, 2, NULL, '用户登入', 'success', '2026-03-25 20:51:23');
INSERT INTO `operation_logs` VALUES (2836, 2, 14, '3D_MODEL_CONSTRUCTION', 'failed', '2026-03-25 20:51:31');
INSERT INTO `operation_logs` VALUES (2837, 2, NULL, '用户登入', 'success', '2026-03-25 20:56:28');
INSERT INTO `operation_logs` VALUES (2838, 2, 14, '3D_MODEL_CONSTRUCTION', 'failed', '2026-03-25 20:56:35');
INSERT INTO `operation_logs` VALUES (2839, 2, NULL, '用户登入', 'success', '2026-03-25 21:00:09');
INSERT INTO `operation_logs` VALUES (2840, 2, NULL, '用户登入', 'success', '2026-03-26 00:23:42');
INSERT INTO `operation_logs` VALUES (2841, 2, NULL, '用户登入', 'success', '2026-03-26 00:25:13');
INSERT INTO `operation_logs` VALUES (2842, 2, NULL, '用户登入', 'success', '2026-03-26 00:48:02');
INSERT INTO `operation_logs` VALUES (2843, 2, NULL, '用户登入', 'success', '2026-03-26 01:01:08');
INSERT INTO `operation_logs` VALUES (2844, 2, NULL, '用户登入', 'success', '2026-03-26 12:35:18');
INSERT INTO `operation_logs` VALUES (2845, 2, NULL, '用户登入', 'success', '2026-03-26 12:50:12');
INSERT INTO `operation_logs` VALUES (2846, 2, NULL, '用户登入', 'success', '2026-03-26 13:33:21');
INSERT INTO `operation_logs` VALUES (2847, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 13:33:35');
INSERT INTO `operation_logs` VALUES (2848, 2, NULL, '用户登入', 'success', '2026-03-26 15:28:33');
INSERT INTO `operation_logs` VALUES (2849, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 15:28:53');
INSERT INTO `operation_logs` VALUES (2850, 2, NULL, '用户登入', 'failed', '2026-03-26 15:44:09');
INSERT INTO `operation_logs` VALUES (2851, 2, NULL, '用户登入', 'success', '2026-03-26 15:44:20');
INSERT INTO `operation_logs` VALUES (2852, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 15:44:38');
INSERT INTO `operation_logs` VALUES (2853, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 15:53:26');
INSERT INTO `operation_logs` VALUES (2854, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 15:55:32');
INSERT INTO `operation_logs` VALUES (2855, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 15:59:42');
INSERT INTO `operation_logs` VALUES (2856, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 16:03:52');
INSERT INTO `operation_logs` VALUES (2857, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 16:04:30');
INSERT INTO `operation_logs` VALUES (2858, 2, NULL, '用户登入', 'success', '2026-03-26 17:09:15');
INSERT INTO `operation_logs` VALUES (2859, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 17:09:34');
INSERT INTO `operation_logs` VALUES (2860, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 17:17:36');
INSERT INTO `operation_logs` VALUES (2861, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 17:23:24');
INSERT INTO `operation_logs` VALUES (2862, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 17:26:03');
INSERT INTO `operation_logs` VALUES (2863, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 17:33:05');
INSERT INTO `operation_logs` VALUES (2864, 2, NULL, '用户登入', 'success', '2026-03-26 17:44:02');
INSERT INTO `operation_logs` VALUES (2865, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 17:44:21');
INSERT INTO `operation_logs` VALUES (2866, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 17:48:10');
INSERT INTO `operation_logs` VALUES (2867, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:01:11');
INSERT INTO `operation_logs` VALUES (2868, 2, NULL, '用户登入', 'success', '2026-03-26 18:07:03');
INSERT INTO `operation_logs` VALUES (2869, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:07:30');
INSERT INTO `operation_logs` VALUES (2870, 2, NULL, '用户登入', 'success', '2026-03-26 18:13:52');
INSERT INTO `operation_logs` VALUES (2871, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:14:11');
INSERT INTO `operation_logs` VALUES (2872, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:14:46');
INSERT INTO `operation_logs` VALUES (2873, 2, NULL, '用户登入', 'success', '2026-03-26 18:19:00');
INSERT INTO `operation_logs` VALUES (2874, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:19:18');
INSERT INTO `operation_logs` VALUES (2875, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:25:17');
INSERT INTO `operation_logs` VALUES (2876, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:28:44');
INSERT INTO `operation_logs` VALUES (2877, 2, NULL, '用户登入', 'success', '2026-03-26 18:34:29');
INSERT INTO `operation_logs` VALUES (2878, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:34:48');
INSERT INTO `operation_logs` VALUES (2879, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:48:28');
INSERT INTO `operation_logs` VALUES (2880, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:52:13');
INSERT INTO `operation_logs` VALUES (2881, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:52:32');
INSERT INTO `operation_logs` VALUES (2882, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:54:13');
INSERT INTO `operation_logs` VALUES (2883, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:55:47');
INSERT INTO `operation_logs` VALUES (2884, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 18:59:11');
INSERT INTO `operation_logs` VALUES (2885, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:02:17');
INSERT INTO `operation_logs` VALUES (2886, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:09:22');
INSERT INTO `operation_logs` VALUES (2887, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:11:53');
INSERT INTO `operation_logs` VALUES (2888, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:17:35');
INSERT INTO `operation_logs` VALUES (2889, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:20:11');
INSERT INTO `operation_logs` VALUES (2890, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:21:41');
INSERT INTO `operation_logs` VALUES (2891, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:25:58');
INSERT INTO `operation_logs` VALUES (2892, 2, 14, '3D_MODEL_CONSTRUCTION', 'failed', '2026-03-26 19:42:51');
INSERT INTO `operation_logs` VALUES (2893, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:43:56');
INSERT INTO `operation_logs` VALUES (2894, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:51:34');
INSERT INTO `operation_logs` VALUES (2895, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:55:03');
INSERT INTO `operation_logs` VALUES (2896, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 19:58:03');
INSERT INTO `operation_logs` VALUES (2897, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 20:05:37');
INSERT INTO `operation_logs` VALUES (2898, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 20:08:10');
INSERT INTO `operation_logs` VALUES (2899, 2, NULL, '用户登入', 'success', '2026-03-26 22:06:45');
INSERT INTO `operation_logs` VALUES (2900, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 22:07:10');
INSERT INTO `operation_logs` VALUES (2901, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 22:22:03');
INSERT INTO `operation_logs` VALUES (2902, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 23:06:35');
INSERT INTO `operation_logs` VALUES (2903, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-26 23:08:18');
INSERT INTO `operation_logs` VALUES (2904, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-26 23:12:55');
INSERT INTO `operation_logs` VALUES (2905, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-26 23:20:52');
INSERT INTO `operation_logs` VALUES (2906, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-26 23:28:44');
INSERT INTO `operation_logs` VALUES (2907, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-26 23:35:01');
INSERT INTO `operation_logs` VALUES (2908, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-26 23:52:31');
INSERT INTO `operation_logs` VALUES (2909, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-26 23:53:49');
INSERT INTO `operation_logs` VALUES (2910, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-27 00:13:54');
INSERT INTO `operation_logs` VALUES (2911, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-27 00:14:14');
INSERT INTO `operation_logs` VALUES (2912, 2, NULL, '用户登入', 'success', '2026-03-27 00:17:16');
INSERT INTO `operation_logs` VALUES (2913, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-27 00:17:40');
INSERT INTO `operation_logs` VALUES (2914, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-27 00:18:13');
INSERT INTO `operation_logs` VALUES (2915, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-27 00:19:41');
INSERT INTO `operation_logs` VALUES (2916, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-27 00:20:25');
INSERT INTO `operation_logs` VALUES (2917, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-27 00:26:19');
INSERT INTO `operation_logs` VALUES (2918, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-27 00:27:14');
INSERT INTO `operation_logs` VALUES (2919, 2, 14, 'VOI_REGION_CONFIRMATION', 'success', '2026-03-27 00:28:22');
INSERT INTO `operation_logs` VALUES (2920, 2, NULL, '用户登入', 'success', '2026-03-27 12:03:21');
INSERT INTO `operation_logs` VALUES (2921, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-27 12:03:46');
INSERT INTO `operation_logs` VALUES (2922, 2, NULL, '用户登入', 'success', '2026-03-27 21:02:24');
INSERT INTO `operation_logs` VALUES (2923, 2, NULL, '用户登入', 'success', '2026-03-27 22:05:42');
INSERT INTO `operation_logs` VALUES (2924, 2, 14, 'MASK_RCNN_DETECTION', 'success', '2026-03-27 22:20:43');
INSERT INTO `operation_logs` VALUES (2925, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-03-27 22:22:09');
INSERT INTO `operation_logs` VALUES (2926, 1, NULL, '用户登入', 'success', '2026-03-29 17:54:53');
INSERT INTO `operation_logs` VALUES (2927, 2, NULL, '用户登入', 'success', '2026-03-29 17:55:03');
INSERT INTO `operation_logs` VALUES (2928, 2, NULL, 'PROJECT_CREATE', 'success', '2026-03-29 18:43:21');
INSERT INTO `operation_logs` VALUES (2929, 2, NULL, 'PROJECT_DELETE', 'success', '2026-03-29 18:44:49');
INSERT INTO `operation_logs` VALUES (2930, 2, NULL, '用户登入', 'success', '2026-03-29 20:13:22');
INSERT INTO `operation_logs` VALUES (2931, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-29 20:41:24');
INSERT INTO `operation_logs` VALUES (2932, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-29 20:42:28');
INSERT INTO `operation_logs` VALUES (2933, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-29 20:43:28');
INSERT INTO `operation_logs` VALUES (2934, 2, NULL, '用户登入', 'success', '2026-03-30 13:18:07');
INSERT INTO `operation_logs` VALUES (2935, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-03-30 13:18:47');
INSERT INTO `operation_logs` VALUES (2936, 2, NULL, '用户登入', 'success', '2026-04-01 19:37:03');
INSERT INTO `operation_logs` VALUES (2937, 2, 14, 'MASK_RCNN_DETECTION', 'success', '2026-04-01 19:37:32');
INSERT INTO `operation_logs` VALUES (2938, 2, NULL, '用户登入', 'success', '2026-04-01 19:44:28');
INSERT INTO `operation_logs` VALUES (2939, 2, 14, 'MASK_RCNN_DETECTION', 'success', '2026-04-01 19:44:43');
INSERT INTO `operation_logs` VALUES (2940, 2, NULL, '用户登入', 'success', '2026-04-01 19:55:39');
INSERT INTO `operation_logs` VALUES (2941, 2, 14, 'MASK_RCNN_DETECTION', 'success', '2026-04-01 19:59:45');
INSERT INTO `operation_logs` VALUES (2942, 2, NULL, '用户登入', 'success', '2026-04-01 21:15:46');
INSERT INTO `operation_logs` VALUES (2943, 2, NULL, '用户登入', 'success', '2026-04-01 21:20:15');
INSERT INTO `operation_logs` VALUES (2944, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-04-01 21:22:41');
INSERT INTO `operation_logs` VALUES (2945, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-04-01 21:38:32');
INSERT INTO `operation_logs` VALUES (2946, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-04-01 21:44:53');
INSERT INTO `operation_logs` VALUES (2947, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-04-01 21:58:06');
INSERT INTO `operation_logs` VALUES (2948, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-04-01 22:27:03');
INSERT INTO `operation_logs` VALUES (2949, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-04-01 22:32:38');
INSERT INTO `operation_logs` VALUES (2950, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-04-01 22:45:08');
INSERT INTO `operation_logs` VALUES (2951, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-04-01 22:49:43');
INSERT INTO `operation_logs` VALUES (2952, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-04-01 22:58:55');
INSERT INTO `operation_logs` VALUES (2953, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-04-01 23:03:12');
INSERT INTO `operation_logs` VALUES (2954, 2, 14, '3D_MODEL_CONSTRUCTION', 'success', '2026-04-01 23:04:19');
INSERT INTO `operation_logs` VALUES (2955, 2, 14, 'DATA_PREPROCESSING', 'success', '2026-04-01 23:07:27');
INSERT INTO `operation_logs` VALUES (2956, 2, NULL, '用户登入', 'success', '2026-04-01 23:09:59');
INSERT INTO `operation_logs` VALUES (2957, 2, NULL, '用户登入', 'success', '2026-04-01 23:14:52');
INSERT INTO `operation_logs` VALUES (2958, 2, NULL, '用户登入', 'success', '2026-04-02 00:48:28');
INSERT INTO `operation_logs` VALUES (2959, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 00:48:41');
INSERT INTO `operation_logs` VALUES (2960, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 00:59:28');
INSERT INTO `operation_logs` VALUES (2961, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 01:00:33');
INSERT INTO `operation_logs` VALUES (2962, 2, NULL, '用户登入', 'success', '2026-04-02 01:02:53');
INSERT INTO `operation_logs` VALUES (2963, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 01:03:12');
INSERT INTO `operation_logs` VALUES (2964, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 01:08:48');
INSERT INTO `operation_logs` VALUES (2965, 2, NULL, '用户登入', 'success', '2026-04-02 01:09:58');
INSERT INTO `operation_logs` VALUES (2966, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 01:10:19');
INSERT INTO `operation_logs` VALUES (2967, 2, NULL, '用户登入', 'success', '2026-04-02 01:11:34');
INSERT INTO `operation_logs` VALUES (2968, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-02 01:11:53');
INSERT INTO `operation_logs` VALUES (2969, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-02 01:17:22');
INSERT INTO `operation_logs` VALUES (2970, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-02 01:17:53');
INSERT INTO `operation_logs` VALUES (2971, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-02 01:24:23');
INSERT INTO `operation_logs` VALUES (2972, 2, NULL, '用户登入', 'success', '2026-04-02 17:52:41');
INSERT INTO `operation_logs` VALUES (2973, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-02 17:53:11');
INSERT INTO `operation_logs` VALUES (2974, 2, NULL, '用户登入', 'success', '2026-04-02 18:56:00');
INSERT INTO `operation_logs` VALUES (2975, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 18:56:21');
INSERT INTO `operation_logs` VALUES (2976, 2, NULL, '用户登入', 'success', '2026-04-02 19:35:49');
INSERT INTO `operation_logs` VALUES (2977, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'failed', '2026-04-02 19:36:14');
INSERT INTO `operation_logs` VALUES (2978, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-02 19:38:10');
INSERT INTO `operation_logs` VALUES (2979, 2, NULL, '用户登入', 'success', '2026-04-02 21:50:27');
INSERT INTO `operation_logs` VALUES (2980, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-02 21:50:54');
INSERT INTO `operation_logs` VALUES (2981, 2, NULL, '用户登入', 'success', '2026-04-03 15:12:24');
INSERT INTO `operation_logs` VALUES (2982, 2, 14, 'MORPHOLOGICAL_ANALYSIS', 'success', '2026-04-03 15:12:58');

-- ----------------------------
-- Table structure for projects
-- ----------------------------
DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `user_id` int(11) NOT NULL,
  `created_time` datetime NULL DEFAULT NULL,
  `updated_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `projects_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of projects
-- ----------------------------
INSERT INTO `projects` VALUES (14, 'uTest2', '', 2, '2026-01-17 18:06:26', '2026-01-17 18:06:26');
INSERT INTO `projects` VALUES (15, 'aTest1', '', 1, '2026-01-18 15:11:06', '2026-01-18 15:11:06');
INSERT INTO `projects` VALUES (17, 'aTest2', '', 1, '2026-01-18 17:30:26', '2026-01-18 17:30:26');
INSERT INTO `projects` VALUES (18, 'uTest3', '', 2, '2026-01-18 18:36:29', '2026-01-18 18:36:29');
INSERT INTO `projects` VALUES (19, 'aTest3', '', 1, '2026-01-20 14:17:31', '2026-01-20 14:17:31');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `role` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `last_login` datetime NULL DEFAULT NULL,
  `current_session_id` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `session_created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'pbkdf2:sha256:600000$aCqJMYeEluSoN3V8$e74112f8b457da7ca8e8e6051940eaa60777a25820906075eb3a2e12eff759ce', 'admin', '2025-11-16 14:08:15', '2026-03-29 17:54:53', NULL, NULL);
INSERT INTO `users` VALUES (2, 'user', 'pbkdf2:sha256:600000$hZ459JKd1wQPfsrL$c96ebffcadb7439583b09d6af222d7ad95ce05855907b82f313dcf88233fe105', 'user', '2025-11-17 15:44:13', '2026-04-03 15:12:24', 'b3d640ee-bfbf-45f9-a547-255af97e0762', '2026-04-03 15:12:24');
INSERT INTO `users` VALUES (3, 'testuser', 'pbkdf2:sha256:600000$hOjvtkfoEPIoh97F$1d5f998710ef0bbaa7075531f64ecbc6c8fdce16d006d9746876bb7c159ec068', 'user', '2025-11-18 05:27:37', NULL, NULL, NULL);
INSERT INTO `users` VALUES (6, 'testuser2', 'pbkdf2:sha256:600000$NsPP7ydH4EMxGycl$3131d9b79c40c9f86ce6c9d95d07c785e8d3732245ea6c6693c14c502f774421', 'user', '2025-11-18 08:22:25', NULL, NULL, NULL);
INSERT INTO `users` VALUES (9, 'test', 'pbkdf2:sha256:600000$An6yHEtuqMeQqeUP$1e055cedcb1c4c95ff9f091e581e397fc224d9217e30b9c124febb8556962d58', 'user', '2025-11-23 20:43:24', NULL, NULL, NULL);
INSERT INTO `users` VALUES (10, 'ddd', 'pbkdf2:sha256:600000$8YWfs8JFnDqmwl24$883b0a16fae3365b8274a25003514bdd6818549793a8a424f90a604de812fa7f', 'user', '2025-11-26 13:08:16', NULL, NULL, NULL);
INSERT INTO `users` VALUES (11, 'www', 'pbkdf2:sha256:600000$Ybs8C5CsKvn30J0g$f0b1baeaa196b93d3244f2df16b8b112396af6bcafa76ad885632c5fc325b038', 'user', '2026-01-18 18:37:44', NULL, NULL, NULL);

SET FOREIGN_KEY_CHECKS = 1;
