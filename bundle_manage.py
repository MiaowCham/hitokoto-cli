import json
import jsonlines
import os
import sys
from datetime import datetime
from loguru import logger


def get_script_directory():
    """
    获取脚本所在目录
    
    Returns:
        str: 脚本所在目录的绝对路径
    """
    logger.debug("获取脚本所在目录")
    # 检查是否在 PyInstaller 环境中运行
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # 在 PyInstaller 单文件模式下，使用可执行文件所在目录
        script_dir = os.path.dirname(sys.executable)
        logger.debug(f"PyInstaller环境，使用可执行文件目录: {script_dir}")
    else:
        # 正常 Python 环境，获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"普通Python环境，使用脚本目录: {script_dir}")
    
    logger.debug(f"脚本所在目录: {script_dir}")
    return script_dir


def get_bundle_directory():
    """
    获取bundle目录路径
    
    Returns:
        str: bundle目录的绝对路径
    """
    logger.debug("获取bundle目录路径")
    script_dir = get_script_directory()
    bundle_dir = os.path.join(script_dir, 'bundle')
    logger.debug(f"bundle目录路径: {bundle_dir}")
    return bundle_dir


def save_package_info(download_info):
    """
    保存语句包信息到package-info.json文件
    
    Args:
        download_info: 下载信息字典
    
    Returns:
        bool: 是否保存成功
    """
    logger.debug("开始保存语句包信息")
    try:
        bundle_dir = get_bundle_directory()
        package_info_path = os.path.join(bundle_dir, 'package-info.json')
        logger.debug(f"语句包信息文件路径: {package_info_path}")
        
        logger.debug(f"正在写入语句包信息，文件数量: {download_info.get('files_amount')}, 语句总数: {download_info.get('amount')}")
        with open(package_info_path, 'w', encoding='utf-8') as f:
            json.dump(download_info, f, ensure_ascii=False, indent=2)
        
        print(f"语句包信息已保存到: {package_info_path}")
        logger.success(f"语句包信息已成功保存到: {package_info_path}")
        return True
        
    except Exception as e:
        print(f"保存语句包信息失败: {str(e)}")
        logger.error(f"保存语句包信息失败: {str(e)}")
        return False


def load_package_info():
    """
    加载语句包信息
    
    Returns:
        dict: 语句包信息，如果文件不存在或加载失败则返回None
    """
    logger.debug("尝试加载语句包信息")
    try:
        bundle_dir = get_bundle_directory()
        package_info_path = os.path.join(bundle_dir, 'package-info.json')
        logger.debug(f"语句包信息文件路径: {package_info_path}")
        
        if not os.path.exists(package_info_path):
            logger.warning(f"语句包信息文件不存在: {package_info_path}")
            return None
        
        logger.debug(f"正在读取语句包信息文件")
        with open(package_info_path, 'r', encoding='utf-8') as f:
            package_info = json.load(f)
        
        logger.success(f"成功加载语句包信息，文件数量: {package_info.get('files_amount')}, 语句总数: {package_info.get('amount')}")
        return package_info
            
    except Exception as e:
        print(f"加载语句包信息失败: {str(e)}")
        logger.error(f"加载语句包信息失败: {str(e)}")
        return None


def generate_index_file():
    """
    生成索引文件index.json
    
    Returns:
        tuple: (是否成功, 索引条目数量, 错误信息)
    """
    logger.info("开始生成索引文件")
    try:
        bundle_dir = get_bundle_directory()
        index_path = os.path.join(bundle_dir, 'index.jsonl')
        logger.debug(f"索引文件路径: {index_path}")
        
        # 语句类型列表
        sentence_types = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
        logger.debug(f"语句类型列表: {sentence_types}")
        
        index_entries = []
        total_entries = 0
        
        logger.info(f"开始处理各类型语句文件，共 {len(sentence_types)} 种类型")
        for sentence_type in sentence_types:
            file_path = os.path.join(bundle_dir, f'{sentence_type}.json')
            logger.debug(f"处理语句文件: {file_path}")
            
            if not os.path.exists(file_path):
                logger.warning(f"语句文件不存在，跳过: {file_path}")
                continue
            
            try:
                logger.debug(f"正在读取语句文件: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    sentences = json.load(f)
                
                if not isinstance(sentences, list):
                    print(f"警告: {sentence_type}.json 格式不正确，跳过")
                    logger.warning(f"警告: {sentence_type}.json 格式不正确，跳过")
                    continue
                
                logger.debug(f"开始为 {len(sentences)} 条语句创建索引条目")
                # 为每个语句创建索引条目
                valid_entries = 0
                for sentence in sentences:
                    if not isinstance(sentence, dict):
                        logger.warning(f"跳过非字典类型的语句条目")
                        continue
                    
                    # 提取必要字段
                    entry = {
                        'id': sentence.get('id'),
                        'uuid': sentence.get('uuid'),
                        'type': sentence.get('type', sentence_type),
                        'file': f'bundle/{sentence_type}.json',
                        'length': sentence.get('length', len(sentence.get('hitokoto', '')))
                    }
                    
                    # 验证必要字段
                    if entry['id'] is not None and entry['uuid']:
                        index_entries.append(entry)
                        total_entries += 1
                        valid_entries += 1
                    else:
                        logger.warning(f"跳过缺少必要字段的语句条目: id={entry['id']}, uuid={entry['uuid']}")
                
                print(f"已处理 {sentence_type}.json: {len(sentences)} 条语句")
                logger.info(f"已处理 {sentence_type}.json: 总计 {len(sentences)} 条语句，有效 {valid_entries} 条")
                
            except Exception as e:
                print(f"处理 {sentence_type}.json 时出错: {str(e)}")
                logger.error(f"处理 {sentence_type}.json 时出错: {str(e)}")
                continue
        
        if not index_entries:
            logger.error("没有找到有效的语句数据")
            return False, 0, "没有找到有效的语句数据"
        
        # 保存索引文件（使用jsonlines格式）
        logger.debug(f"正在保存索引文件: {index_path}，共 {total_entries} 条索引")
        with jsonlines.open(index_path, 'w') as writer:
            for entry in index_entries:
                writer.write(entry)
        
        print(f"索引文件已生成: {index_path}")
        print(f"总计索引条目: {total_entries}")
        logger.success(f"索引文件已成功生成: {index_path}，总计 {total_entries} 条索引条目")
        
        return True, total_entries, None
        
    except Exception as e:
        error_msg = f"生成索引文件失败: {str(e)}"
        logger.error(error_msg)
        return False, 0, error_msg


def check_bundle_integrity():
    """
    检查语句包完整性
    
    Returns:
        tuple: (是否通过检查, 检查结果信息)
    """
    logger.info("开始检查语句包完整性")
    try:
        # 加载package-info.json
        logger.debug("尝试加载package-info.json")
        package_info = load_package_info()
        if not package_info:
            logger.error("未找到package-info.json文件")
            return False, "未找到package-info.json文件"
        
        bundle_dir = get_bundle_directory()
        issues = []
        
        # 检查文件是否存在
        expected_files = package_info.get('files', [])
        logger.debug(f"需要检查的文件数量: {len(expected_files)}")
        for file_info in expected_files:
            file_name = file_info.get('name')
            if not file_name:
                logger.warning("文件信息中缺少文件名，跳过")
                continue
                
            file_path = os.path.join(bundle_dir, file_name)
            logger.debug(f"检查文件: {file_name}")
            if not os.path.exists(file_path):
                logger.warning(f"缺失文件: {file_name}")
                issues.append(f"缺失文件: {file_name}")
                continue
            
            # 检查文件内容数量
            try:
                logger.debug(f"检查文件内容: {file_name}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                actual_count = len(data) if isinstance(data, list) else 0
                expected_count = file_info.get('amount', 0)
                
                if actual_count != expected_count:
                    logger.warning(f"{file_name}: 预期{expected_count}条，实际{actual_count}条")
                    issues.append(f"{file_name}: 预期{expected_count}条，实际{actual_count}条")
                else:
                    logger.debug(f"{file_name}: 内容数量正确，共{actual_count}条")
                    
            except Exception as e:
                logger.error(f"{file_name}: 读取失败 - {str(e)}")
                issues.append(f"{file_name}: 读取失败 - {str(e)}")
        
        # 检查索引文件
        index_path = os.path.join(bundle_dir, 'index.jsonl')
        logger.debug(f"检查索引文件: {index_path}")
        if not os.path.exists(index_path):
            logger.warning("缺失索引文件: index.jsonl")
            issues.append("缺失索引文件: index.jsonl")
        
        if issues:
            logger.warning(f"完整性检查发现{len(issues)}个问题")
            return False, "\n".join(["发现以下问题:"] + issues)
        else:
            logger.success("语句包完整性检查通过")
            return True, "语句包完整性检查通过"
            
    except Exception as e:
        error_msg = f"检查过程中出错: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def update_package_info_and_index(download_info):
    """
    更新语句包信息和索引文件
    
    Args:
        download_info: 下载信息字典
    
    Returns:
        tuple: (是否成功, 错误信息)
    """
    logger.info("开始更新语句包信息和索引文件")
    logger.debug(f"下载信息: {download_info}")
    
    # 保存package-info.json
    logger.debug("尝试保存语句包信息")
    if not save_package_info(download_info):
        logger.error("保存语句包信息失败")
        return False, "保存语句包信息失败"
    logger.success("语句包信息保存成功")
    
    # 生成索引文件
    logger.debug("开始生成索引文件")
    success, index_count, error = generate_index_file()
    if not success:
        error_msg = f"生成索引文件失败: {error}"
        logger.error(error_msg)
        return False, error_msg
    
    print(f"管理文件生成完成，索引条目: {index_count}")
    logger.success(f"语句包信息和索引文件更新成功，索引条目数: {index_count}")
    return True, None


if __name__ == "__main__":
    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(sys.stderr, level="DEBUG")  # 添加标准错误输出处理器
    
    # 测试代码
    print("测试语句包管理功能...")
    logger.info("开始测试语句包管理功能")
    
    # 检查是否有语句包
    logger.debug("尝试加载语句包信息")
    package_info = load_package_info()
    if package_info:
        print("\n当前语句包信息:")
        print(f"来源: {package_info.get('source')}")
        print(f"文件数量: {package_info.get('files_amount')}")
        print(f"语句总数: {package_info.get('amount')}")
        print(f"更新时间: {package_info.get('last_update')}")
        logger.info(f"已加载语句包信息: 来源={package_info.get('source')}, 文件数量={package_info.get('files_amount')}, 语句总数={package_info.get('amount')}")
        
        # 检查完整性
        print("\n检查语句包完整性...")
        logger.info("开始检查语句包完整性")
        is_valid, check_result = check_bundle_integrity()
        print(check_result)
        if is_valid:
            logger.success("语句包完整性检查通过")
        else:
            logger.warning("语句包完整性检查未通过")
        
        # 重新生成索引
        print("\n重新生成索引文件...")
        logger.info("开始重新生成索引文件")
        success, count, error = generate_index_file()
        if success:
            print(f"索引生成成功，共 {count} 条记录")
            logger.success(f"索引生成成功，共 {count} 条记录")
        else:
            print(f"索引生成失败: {error}")
            logger.error(f"索引生成失败: {error}")
    else:
        print("未找到语句包，请先获取语句包")
        logger.warning("未找到语句包，请先获取语句包")