import os
import requests
from typing import Optional
from pathlib import Path
from .utils import get_cache_dir, validate_model_id

class DownloadError(Exception):
    """下载过程中的自定义异常"""
    pass

def snapshot_download(
    model_id: str,
    cache_dir: Optional[str] = None,
    token: Optional[str] = None
) -> str:
    """
    从GitLab下载模型快照
    
    Args:
        model_id: 模型ID，格式为 'username/model-name'
        cache_dir: 可选，指定下载目录
        token: 可选，GitLab API token
    
    Returns:
        str: 模型文件保存的本地目录路径
    
    Raises:
        DownloadError: 当下载失败时抛出
    """
    # 验证模型ID格式
    if not validate_model_id(model_id):
        raise ValueError(f"无效的模型ID格式: {model_id}")
    
    # 设置下载目录
    if cache_dir is None:
        cache_dir = get_cache_dir()
    
    model_dir = os.path.join(cache_dir, model_id.replace('/', '_'))
    os.makedirs(model_dir, exist_ok=True)
    
    # API配置
    api_base = "http://10.1.79.85:1425/api/v4"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        # 将模型ID中的斜杠编码为%2F，以符合GitLab API的URL要求
        encoded_model_id = model_id.replace('/', '%2F')
        
        # 获取仓库文件列表
        tree_response = requests.get(
            f"{api_base}/projects/{encoded_model_id}/repository/tree",
            params={"recursive": True},
            headers=headers
        )
        tree_response.raise_for_status()
        
        
        # 下载所有非git文件
        for item in tree_response.json():
            if item["type"] == "blob" and not item["path"].startswith(".git"):
                file_path = os.path.join(model_dir, item["path"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 下载文件内容
                file_response = requests.get(
                    f"{api_base}/projects/{encoded_model_id}/repository/files/{item['path']}/raw",
                    headers=headers
                )
                file_response.raise_for_status()
                
                with open(file_path, "wb") as f:
                    f.write(file_response.content)
                
        return model_dir
        
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"下载失败: {str(e)}") 