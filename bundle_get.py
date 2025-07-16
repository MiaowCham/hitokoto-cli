import requests
import json
import os
import sys
from datetime import datetime
from loguru import logger
from bundle_manage import update_package_info_and_index


def get_bundle_sources():
    """
    获取语句包来源配置
    
    Returns:
        dict: 包含各个来源的URL配置
    """
    logger.debug("获取语句包来源配置")
    sources = {
        'of': 'https://sentences-bundle.hitokoto.cn/',  # 官方
        'gh': 'https://raw.githubusercontent.com/hitokoto-osc/sentences-bundle/master/',  # Github
        'jsd': 'https://cdn.jsdelivr.net/gh/hitokoto-osc/sentences-bundle@latest/'  # JSDelivr
    }
    logger.debug(f"语句包来源配置: {sources}")
    return sources


def get_script_directory():
    """
    获取脚本所在目录（用于确定bundle存储路径）
    
    Returns:
        str: 脚本所在目录的绝对路径
    """
    logger.debug("获取脚本所在目录")
    # 检查是否在 PyInstaller 环境中运行
    if getattr(sys, 'frozen', False):
        # 在 PyInstaller 环境下（包括 --onefile 和 --onedir 模式）
        # 使用可执行文件所在目录
        script_dir = os.path.dirname(sys.executable)
        logger.debug(f"PyInstaller环境，使用可执行文件目录: {script_dir}")
    else:
        # 正常 Python 环境，获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"普通Python环境，使用脚本目录: {script_dir}")
    
    logger.debug(f"脚本所在目录: {script_dir}")
    return script_dir


def ensure_bundle_directory():
    """
    确保bundle目录存在
    
    Returns:
        str: bundle目录的绝对路径
    """
    logger.debug("确保bundle目录存在")
    script_dir = get_script_directory()
    bundle_dir = os.path.join(script_dir, 'bundle')
    logger.debug(f"bundle目录路径: {bundle_dir}")
    
    if not os.path.exists(bundle_dir):
        logger.info(f"bundle目录不存在，正在创建: {bundle_dir}")
        os.makedirs(bundle_dir)
        print(f"创建bundle目录: {bundle_dir}")
        logger.success(f"成功创建bundle目录: {bundle_dir}")
    else:
        logger.debug(f"bundle目录已存在: {bundle_dir}")
    
    return bundle_dir


def download_sentence_file(source_url, sentence_type, bundle_dir):
    """
    下载指定类型的语句文件
    
    Args:
        source_url: 来源URL
        sentence_type: 语句类型 (a-l)
        bundle_dir: bundle目录路径
    
    Returns:
        tuple: (是否成功, 语句数量, 错误信息)
    """
    logger.debug(f"准备下载语句文件，类型: {sentence_type}, 来源: {source_url}")
    file_url = f"{source_url}sentences/{sentence_type}.json"
    file_path = os.path.join(bundle_dir, f"{sentence_type}.json")
    logger.debug(f"下载URL: {file_url}")
    logger.debug(f"保存路径: {file_path}")
    
    try:
        print(f"正在下载 {sentence_type}.json 从 {file_url}")
        logger.info(f"正在下载 {sentence_type}.json 从 {file_url}")
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()
        logger.debug(f"下载请求成功，状态码: {response.status_code}")
        
        # 解析JSON以验证格式和计算数量
        data = response.json()
        if not isinstance(data, list):
            logger.error(f"文件格式不正确，应为JSON数组: {file_url}")
            return False, 0, "文件格式不正确，应为JSON数组"
        
        logger.debug(f"成功解析JSON数据，包含 {len(data)} 条语句")
        
        # 保存文件
        logger.debug(f"正在保存文件: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"成功下载 {sentence_type}.json，包含 {len(data)} 条语句")
        logger.success(f"成功下载并保存 {sentence_type}.json，包含 {len(data)} 条语句")
        return True, len(data), None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"下载 {sentence_type}.json 失败: 网络请求错误 - {str(e)}")
        return False, 0, f"网络请求失败: {str(e)}"
    except json.JSONDecodeError as e:
        logger.error(f"下载 {sentence_type}.json 失败: JSON解析错误 - {str(e)}")
        return False, 0, f"JSON解析失败: {str(e)}"
    except Exception as e:
        logger.error(f"下载 {sentence_type}.json 失败: 未知错误 - {str(e)}")
        return False, 0, f"未知错误: {str(e)}"


def download_single_file_with_retry(sentence_type, bundle_dir, primary_source, primary_url):
    """
    为单个文件实现换源重试机制
    
    Args:
        sentence_type: 语句类型
        bundle_dir: bundle目录路径
        primary_source: 主要来源名称
        primary_url: 主要来源URL
    
    Returns:
        tuple: (是否成功, 语句数量, 使用的来源, 错误信息)
    """
    logger.debug(f"为文件 {sentence_type}.json 实现换源重试机制，主要来源: {primary_source}")
    sources = get_bundle_sources()
    
    # 构建重试顺序：其他两个源 + 原来源最后一次尝试
    retry_order = []
    for source_name, source_url in sources.items():
        if source_name != primary_source:
            retry_order.append((source_name, source_url))
    retry_order.append((primary_source, primary_url))  # 最后再试一次原来源
    
    logger.debug(f"重试顺序: {[source[0] for source in retry_order]}")
    
    # 首先尝试主要来源
    logger.info(f"首先尝试从主要来源 {primary_source} 下载 {sentence_type}.json")
    success, count, error = download_sentence_file(primary_url, sentence_type, bundle_dir)
    if success:
        logger.success(f"从主要来源 {primary_source} 成功下载 {sentence_type}.json")
        return True, count, primary_source, None
    
    # 如果是404错误，说明文件不存在，不需要重试
    if "404" in str(error) or "Not Found" in str(error):
        logger.warning(f"文件 {sentence_type}.json 在 {primary_source} 不存在 (404)，不进行重试")
        return False, 0, primary_source, error
    
    print(f"  {sentence_type}.json 从 {primary_source} 下载失败，尝试换源重试...")
    logger.warning(f"{sentence_type}.json 从 {primary_source} 下载失败，尝试换源重试...")
    
    # 依次尝试其他来源
    for source_name, source_url in retry_order:
        print(f"  尝试从 {source_name} 下载 {sentence_type}.json")
        logger.info(f"尝试从 {source_name} 下载 {sentence_type}.json")
        success, count, error = download_sentence_file(source_url, sentence_type, bundle_dir)
        
        if success:
            print(f"  成功从 {source_name} 获取 {sentence_type}.json")
            logger.success(f"成功从 {source_name} 获取 {sentence_type}.json")
            return True, count, source_name, None
        
        # 如果是404错误，说明该来源也没有这个文件
        if "404" in str(error) or "Not Found" in str(error):
            logger.warning(f"文件 {sentence_type}.json 在 {source_name} 不存在 (404)，继续尝试下一个来源")
            continue
        
        logger.error(f"从 {source_name} 下载 {sentence_type}.json 失败: {error}")
    
    logger.error(f"所有来源都无法下载 {sentence_type}.json，最后错误: {error}")
    return False, 0, primary_source, f"所有来源都失败，最后错误: {error}"


def download_bundle_from_source(source_name, source_url):
    """
    从指定来源下载完整的语句包
    
    Args:
        source_name: 来源名称 (of/gh/jsd)
        source_url: 来源URL
    
    Returns:
        tuple: (是否成功, 下载信息字典, 错误信息)
    """
    print(f"开始从 {source_name} 下载语句包...")
    logger.info(f"开始从 {source_name} 下载语句包...")
    
    bundle_dir = ensure_bundle_directory()
    
    # 语句类型列表
    sentence_types = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    logger.debug(f"语句类型列表: {sentence_types}")
    
    downloaded_files = []
    total_sentences = 0
    failed_types = []
    source_usage = {}  # 记录每个来源的使用情况
    
    logger.info(f"开始下载各类型语句文件，共 {len(sentence_types)} 种类型")
    for sentence_type in sentence_types:
        logger.debug(f"处理语句类型: {sentence_type}")
        success, count, used_source, error = download_single_file_with_retry(
            sentence_type, bundle_dir, source_name, source_url
        )
        
        if success:
            logger.debug(f"成功下载 {sentence_type}.json，添加到下载列表")
            downloaded_files.append({
                'name': f'{sentence_type}.json',
                'amount': count,
                'source': used_source
            })
            total_sentences += count
            logger.debug(f"当前已下载语句总数: {total_sentences}")
            
            # 统计来源使用情况
            if used_source not in source_usage:
                source_usage[used_source] = 0
            source_usage[used_source] += 1
            logger.debug(f"来源 {used_source} 使用次数: {source_usage[used_source]}")
        else:
            logger.warning(f"无法下载 {sentence_type}.json")
            failed_types.append(sentence_type)
            # 如果不是404错误，说明是真正的下载失败
            if not ("404" in str(error) or "Not Found" in str(error)):
                print(f"下载 {sentence_type}.json 失败: {error}")
                logger.error(f"下载 {sentence_type}.json 失败: {error}")
    
    if not downloaded_files:
        logger.error("没有成功下载任何文件")
        return False, None, "没有成功下载任何文件"
    
    # 构建下载信息
    logger.debug("构建下载信息字典")
    download_info = {
        'source': source_name,
        'source_url': source_url.rstrip('/'),
        'files_amount': len(downloaded_files),
        'files': downloaded_files,
        'amount': total_sentences,
        'last_update': datetime.now().isoformat(),
        'last_check': datetime.now().isoformat(),
        'source_usage': source_usage,  # 添加来源使用统计
        'failed_types': failed_types   # 添加失败类型记录
    }
    logger.debug(f"下载信息: 文件数量={download_info['files_amount']}, 语句总数={download_info['amount']}")
    
    # 输出详细的下载结果
    print(f"\n下载完成统计:")
    print(f"成功下载: {len(downloaded_files)} 个文件，共 {total_sentences} 条语句")
    logger.info(f"下载完成统计: 成功下载 {len(downloaded_files)} 个文件，共 {total_sentences} 条语句")
    
    if source_usage:
        print(f"来源使用情况:")
        logger.info("来源使用情况:")
        for src, count in source_usage.items():
            print(f"  {src}: {count} 个文件")
            logger.info(f"  {src}: {count} 个文件")
    
    if failed_types:
        print(f"未能获取的类型: {', '.join(failed_types)}")
        logger.warning(f"未能获取的类型: {', '.join(failed_types)}")
    
    # 判断是否完全成功
    total_expected = len(sentence_types)
    is_complete = len(downloaded_files) == total_expected
    logger.debug(f"下载完整性检查: 预期={total_expected}, 实际={len(downloaded_files)}, 完整={is_complete}")
    
    if not is_complete:
        warning_msg = f"部分成功: 预期 {total_expected} 个文件，实际获取 {len(downloaded_files)} 个"
        logger.warning(warning_msg)
        return True, download_info, warning_msg
    
    logger.success(f"成功完整下载语句包，共 {len(downloaded_files)} 个文件，{total_sentences} 条语句")
    return True, download_info, None


def get_bundle(source='gh'):
    """
    获取语句包的主函数
    
    Args:
        source: 来源标识 ('of'=官方, 'gh'=Github, 'jsd'=JSDelivr)
    
    Returns:
        tuple: (是否成功, 下载信息字典, 错误信息)
    """
    logger.info(f"开始获取语句包，指定来源: {source}")
    sources = get_bundle_sources()
    
    # 验证来源参数
    if source not in sources:
        error_msg = f"不支持的来源: {source}，支持的来源: {', '.join(sources.keys())}"
        logger.error(error_msg)
        return False, None, error_msg
    
    # 确定下载顺序
    if source == 'gh':
        # 默认优先Github，失败后尝试其他来源
        try_order = ['gh', 'jsd', 'of']
    else:
        # 指定来源优先，失败后尝试Github
        try_order = [source, 'gh']
        if source != 'jsd':
            try_order.append('jsd')
        if source != 'of':
            try_order.append('of')
    
    logger.debug(f"下载尝试顺序: {try_order}")
    last_error = None
    
    for try_source in try_order:
        source_url = sources[try_source]
        print(f"\n尝试从 {try_source} 获取语句包...")
        logger.info(f"尝试从 {try_source} 获取语句包...")
        
        success, download_info, error = download_bundle_from_source(try_source, source_url)
        
        if success:
            logger.success(f"从 {try_source} 成功获取语句包")
            # 自动生成管理文件
            logger.info("开始生成管理文件...")
            manage_success, manage_error = update_package_info_and_index(download_info)
            if not manage_success:
                print(f"警告: 管理文件生成失败 - {manage_error}")
                logger.warning(f"管理文件生成失败 - {manage_error}")
            else:
                logger.success("管理文件生成成功")
            
            return True, download_info, None
        else:
            last_error = error
            print(f"从 {try_source} 获取失败: {error}")
            logger.error(f"从 {try_source} 获取失败: {error}")
    
    final_error = f"所有来源都获取失败，最后错误: {last_error}"
    logger.error(final_error)
    return False, None, final_error


if __name__ == "__main__":
    # 配置日志
    logger.remove()  # 移除默认处理器
    logger.add(sys.stderr, level="DEBUG")  # 添加标准错误输出处理器
    
    # 测试代码
    print("测试语句包获取功能...")
    logger.info("测试语句包获取功能...")
    
    # 测试从Github获取
    logger.info("开始从Github获取语句包")
    success, info, error = get_bundle('gh')
    
    if success:
        print("\n获取成功！")
        logger.success("语句包获取成功！")
        print(f"来源: {info['source']}")
        print(f"文件数量: {info['files_amount']}")
        print(f"语句总数: {info['amount']}")
        print(f"更新时间: {info['last_update']}")
        logger.info(f"来源: {info['source']}, 文件数量: {info['files_amount']}, 语句总数: {info['amount']}")
    else:
        print(f"\n获取失败: {error}")
        logger.error(f"获取失败: {error}")