from .recognition_dispatcher import (
	get_landmark,                  # 默认：同时跑 Qwen + 本地，冲突以 Qwen 为准；返回 {'success','landmark'}
	get_landmark_qwen,             # 仅 Qwen（可 return_details）
	get_landmarks_qwen_in_dir,     # 目录批量（Qwen）
	get_landmark_minimal,          # Qwen 优先→本地回退（极简返回）
)
