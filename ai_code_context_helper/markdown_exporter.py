import os
import chardet
from charset_normalizer import from_bytes
from typing import Tuple, List
from ai_code_context_helper.config import SUPPORTED_EXTENSIONS

def detect_encoding(file_path: str) -> str:
    """混合检测编码（优化中文优先检测）"""
    file_size = os.path.getsize(file_path)
    
    # 中文优先检测策略
    def check_chinese_encodings(data: bytes) -> str:
        for encoding in ['gbk', 'gb2312', 'gb18030']:
            try:
                data.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        return None

    # 小文件处理
    if file_size < 100000:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            # 优先中文编码检测
            chinese_enc = check_chinese_encodings(raw_data)
            if chinese_enc:
                return chinese_enc
            # 备用检测
            result = chardet.detect(raw_data)
            return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
    
    # 大文件分块检测
    with open(file_path, 'rb') as f:
        chunks = []
        chunks.append(f.read(50000))
        if file_size > 200000:
            f.seek(file_size // 2)
            chunks.append(f.read(50000))
        if file_size > 100000:
            f.seek(-50000, os.SEEK_END)
            chunks.append(f.read(50000))
        combined = b''.join(chunks)
        # 优先中文编码检测
        chinese_enc = check_chinese_encodings(combined)
        if chinese_enc:
            return chinese_enc
        # 备用检测
        result = from_bytes(combined).best()
        return result.encoding if result else 'utf-8'

def validate_encoding(file_path: str, encoding: str) -> bool:
    """验证编码可用性"""
    if not encoding:
        return False
    try:
        with open(file_path, 'r', encoding=encoding, errors='strict') as f:
            for _ in range(10):
                line = f.readline()
                if not line:
                    break
        return True
    except (UnicodeDecodeError, LookupError):
        return False

def read_file_with_encoding(file_path: str, 
                           fallback_encodings: list = None) -> Tuple[str, str]:
    """多编码尝试读取文件"""
    if fallback_encodings is None:
        fallback_encodings = ['utf-8', 'gbk', 'latin-1']
        
    detected = detect_encoding(file_path)
    tried = set()
    
    # 优先尝试检测到的编码
    if detected and detected not in tried:
        if validate_encoding(file_path, detected):
            with open(file_path, 'r', encoding=detected) as f:
                return f.read(), detected
        tried.add(detected)
    
    # 尝试备选编码
    for enc in fallback_encodings:
        if enc in tried:
            continue
        if validate_encoding(file_path, enc):
            with open(file_path, 'r', encoding=enc) as f:
                return f.read(), enc
        tried.add(enc)
    
    # 最后尝试宽松模式
    for enc in ['utf-8', 'gbk']:
        try:
            with open(file_path, 'r', encoding=enc, errors='replace') as f:
                return f.read(), f"{enc} (替换错误字符)"
        except Exception:
            continue
    
    return None, None

def get_relative_display_path(file_path: str, base_dir: str) -> str:
    """获取用于显示的相对路径（去除重复的根目录名）"""
    try:
        if not base_dir:
            return os.path.basename(file_path)
        
        base_dir = os.path.abspath(base_dir)
        file_path = os.path.abspath(file_path)
        
        # 计算公共路径
        common_path = os.path.commonpath([base_dir, file_path])
        
        # 如果文件在根目录下，直接返回相对路径（不包含根目录名）
        if common_path == base_dir:
            rel_path = os.path.relpath(file_path, base_dir)
            return rel_path.replace("\\", "/")
        
        # 对于不在根目录下的文件，返回完整相对路径
        return file_path.replace("\\", "/")
    except Exception:
        return os.path.basename(file_path)

def generate_markdown(output_path: str, 
                      files: list,  # 只接收文件绝对路径列表
                      project_root: str,  # 新增参数，项目根目录
                      include_markers: bool = True, 
                      show_encoding: bool = False) -> Tuple[int, List[str]]:
    """
    生成最终Markdown文件
    Args:
        output_path: 输出文件路径
        files: 要处理的文件列表，每个元素是文件绝对路径
        project_root: 项目根目录
        include_markers: 是否包含代码块标记
        show_encoding: 是否显示编码信息
    Returns:
        (成功数量, 错误信息列表)
    """
    error_files = []
    processed = 0
    try:
        with open(output_path, 'w', encoding='utf-8') as md_file:
            for file_path in files:
                try:
                    if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
                        error_files.append(f"无效文件: {file_path}")
                        continue
                    # 用项目根目录生成相对路径
                    display_path = get_relative_display_path(file_path, project_root)
                    _, ext = os.path.splitext(display_path)
                    lang = SUPPORTED_EXTENSIONS.get(ext.lower(), '')
                    content, encoding = read_file_with_encoding(file_path)
                    if content is None:
                        error_files.append(f"编码错误: {file_path}")
                        continue
                    header = f"### {display_path}\n"
                    md_file.write(header)
                    if show_encoding and encoding:
                        clean_enc = encoding.replace(" (替换错误字符)", "")
                        md_file.write(f"<!-- 文件编码: {clean_enc} -->\n")
                    if include_markers:
                        md_file.write(f"<!-- [START OF FILE: {os.path.basename(file_path)}] -->\n")
                    code_block = f"```{lang}\n"
                    md_file.write(code_block)
                    md_file.write(content)
                    if not content.endswith('\n'):
                        md_file.write('\n')
                    md_file.write("```\n\n")
                    if include_markers:
                        md_file.write(f"<!-- [END OF FILE: {os.path.basename(file_path)}] -->\n\n")
                    processed += 1
                except Exception as e:
                    error_files.append(f"处理失败 ({file_path}): {str(e)}")
    except Exception as e:
        error_files.append(f"写入失败: {str(e)}")
    return processed, error_files