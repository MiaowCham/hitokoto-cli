#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语句包输出模块
负责从本地语句包中获取和输出一言
"""

import os
import sys
import json
import random
import jsonlines

from typing import Dict, List, Optional, Any
from loguru import logger


def get_bundle_directory():
    """获取语句包目录路径"""
    # 检查是否在 PyInstaller 环境中运行
    if getattr(sys, 'frozen', False):
        # 在 PyInstaller 环境下（包括 --onefile 和 --onedir 模式）
        # 使用可执行文件所在目录
        script_dir = os.path.dirname(sys.executable)
    else:
        # 正常 Python 环境，获取脚本所在目录，而不是运行目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "bundle")


def load_package_info(bundle_dir="bundle"):
    """加载语句包信息"""
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    package_info_file = os.path.join(bundle_dir, "package-info.json")
    logger.debug(f"尝试加载语句包信息文件: {package_info_file}")
    
    if not os.path.exists(package_info_file):
        logger.warning(f"语句包信息文件不存在: {package_info_file}")
        return None
    
    try:
        with open(package_info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"成功加载语句包信息文件")
            return data
    except Exception as e:
        logger.error(f"加载语句包信息文件失败: {e}")
        return None


def load_index_file(bundle_dir="bundle"):
    """加载索引文件"""
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    index_file = os.path.join(bundle_dir, "index.jsonl")
    logger.debug(f"尝试加载索引文件: {index_file}")
    
    if not os.path.exists(index_file):
        logger.warning(f"索引文件不存在: {index_file}")
        return []
    
    try:
        index_data = []
        with jsonlines.open(index_file, 'r') as reader:
            for item in reader:
                index_data.append(item)
        logger.debug(f"成功加载索引文件，共 {len(index_data)} 条记录")
        return index_data
    except Exception as e:
        logger.error(f"加载索引文件失败: {e}")
        return []


def get_sentence_by_id(sentence_id, bundle_dir="bundle"):
    """根据ID获取语句"""
    logger.debug(f"尝试根据ID获取语句: {sentence_id}")
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    # 从索引中查找
    index_data = load_index_file(bundle_dir)
    target_item = None
    
    for item in index_data:
        if item.get('id') == sentence_id:
            target_item = item
            logger.debug(f"在索引中找到ID为 {sentence_id} 的语句")
            break
    
    if not target_item:
        logger.warning(f"在索引中未找到ID为 {sentence_id} 的语句")
        return None
    
    # 读取对应文件
    file_path = os.path.join(bundle_dir, f"{target_item['type']}.json")
    logger.debug(f"尝试从文件读取语句: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"语句文件不存在: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sentences = json.load(f)
        
        # 查找对应ID的语句
        for sentence in sentences:
            if sentence.get('id') == sentence_id:
                logger.success(f"成功获取ID为 {sentence_id} 的语句")
                return sentence
        
        logger.warning(f"在文件 {file_path} 中未找到ID为 {sentence_id} 的语句")
    except Exception as e:
        logger.error(f"读取语句文件失败: {e}")
    
    return None


def get_sentence_by_uuid(sentence_uuid, bundle_dir="bundle"):
    """根据UUID获取语句"""
    logger.debug(f"尝试根据UUID获取语句: {sentence_uuid}")
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    # 从索引中查找
    index_data = load_index_file(bundle_dir)
    target_item = None
    
    for item in index_data:
        if item.get('uuid') == sentence_uuid:
            target_item = item
            logger.debug(f"在索引中找到UUID为 {sentence_uuid} 的语句")
            break
    
    if not target_item:
        logger.warning(f"在索引中未找到UUID为 {sentence_uuid} 的语句")
        return None
    
    # 读取对应文件
    file_path = os.path.join(bundle_dir, f"{target_item['type']}.json")
    logger.debug(f"尝试从文件读取语句: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"语句文件不存在: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sentences = json.load(f)
        
        # 查找对应UUID的语句
        for sentence in sentences:
            if sentence.get('uuid') == sentence_uuid:
                logger.success(f"成功获取UUID为 {sentence_uuid} 的语句")
                return sentence
        
        logger.warning(f"在文件 {file_path} 中未找到UUID为 {sentence_uuid} 的语句")
    except Exception as e:
        logger.error(f"读取语句文件失败: {e}")
    
    return None


def get_random_sentence(sentence_type=None, min_length=None, max_length=None, bundle_dir="bundle"):
    """随机获取语句"""
    logger.debug(f"尝试随机获取语句，类型: {sentence_type}, 最小长度: {min_length}, 最大长度: {max_length}")
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    # 加载索引
    index_data = load_index_file(bundle_dir)
    if not index_data:
        logger.warning("索引数据为空，无法获取随机语句")
        return None
    
    # 过滤条件
    filtered_items = []
    for item in index_data:
        # 类型过滤
        if sentence_type and item.get('type') != sentence_type:
            continue
        
        # 长度过滤
        length = item.get('length', 0)
        if min_length is not None and length < min_length:
            continue
        if max_length is not None and length > max_length:
            continue
        
        filtered_items.append(item)
    
    logger.debug(f"过滤后的语句数量: {len(filtered_items)}")
    if not filtered_items:
        logger.warning("没有符合条件的语句")
        return None
    
    # 随机选择一个
    selected_item = random.choice(filtered_items)
    logger.debug(f"随机选择的语句ID: {selected_item.get('id')}, 类型: {selected_item.get('type')}")
    
    # 读取对应文件获取完整语句
    file_path = os.path.join(bundle_dir, f"{selected_item['type']}.json")
    logger.debug(f"尝试从文件读取完整语句: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"语句文件不存在: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sentences = json.load(f)
        
        # 查找对应ID的语句
        for sentence in sentences:
            if sentence.get('id') == selected_item['id']:
                logger.success(f"成功获取随机语句，ID: {selected_item['id']}")
                return sentence
        
        logger.warning(f"在文件 {file_path} 中未找到ID为 {selected_item['id']} 的语句")
    except Exception as e:
        logger.error(f"读取语句文件失败: {e}")
    
    return None


def get_sentences_by_type(sentence_types, min_length=None, max_length=None, bundle_dir="bundle"):
    """根据类型获取语句列表"""
    logger.debug(f"尝试获取指定类型的语句列表，类型: {sentence_types}, 最小长度: {min_length}, 最大长度: {max_length}")
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    # 加载索引
    index_data = load_index_file(bundle_dir)
    if not index_data:
        logger.warning("索引数据为空，无法获取语句列表")
        return []
    
    # 过滤条件
    filtered_items = []
    for item in index_data:
        # 类型过滤
        if sentence_types and item.get('type') not in sentence_types:
            continue
        
        # 长度过滤
        length = item.get('length', 0)
        if min_length is not None and length < min_length:
            continue
        if max_length is not None and length > max_length:
            continue
        
        filtered_items.append(item)
    
    logger.debug(f"过滤后的语句数量: {len(filtered_items)}")
    return filtered_items


def generate_unique_filename(base_path, filename):
    """生成唯一文件名，避免重复"""
    logger.debug(f"尝试生成唯一文件名，基础路径: {base_path}, 文件名: {filename}")
    name, ext = os.path.splitext(filename)
    counter = 0
    
    while True:
        if counter == 0:
            full_path = os.path.join(base_path, filename)
        else:
            new_filename = f"{name}({counter}){ext}"
            full_path = os.path.join(base_path, new_filename)
        
        if not os.path.exists(full_path):
            logger.debug(f"生成的唯一文件路径: {full_path}")
            return full_path
        
        logger.debug(f"文件已存在，尝试新的计数值: {counter+1}")
        counter += 1


def export_sentences_to_file(count=10, output_path=".", sentence_types=None, min_length=None, max_length=None, include_source=False, bundle_dir="bundle"):
    """批量输出语句到文件"""
    logger.debug(f"尝试批量输出语句到文件，数量: {count}, 输出路径: {output_path}, 类型: {sentence_types}, 最小长度: {min_length}, 最大长度: {max_length}, 包含来源: {include_source}")
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    # 检查语句包是否存在
    package_info = load_package_info(bundle_dir)
    if not package_info:
        logger.error("未找到语句包，请先获取语句包")
        print("错误：未找到语句包，请先获取语句包")
        return False
    
    # 获取符合条件的语句
    if sentence_types:
        logger.debug(f"使用指定类型过滤语句: {sentence_types}")
        available_items = get_sentences_by_type(sentence_types, min_length, max_length, bundle_dir)
    else:
        # 获取所有类型
        logger.debug("使用所有类型过滤语句")
        available_items = get_sentences_by_type(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'], min_length, max_length, bundle_dir)
    
    if not available_items:
        logger.error("未找到符合条件的语句")
        print("错误：未找到符合条件的语句")
        return False
    
    if len(available_items) < count:
        logger.warning(f"符合条件的语句只有 {len(available_items)} 条，将输出全部")
        print(f"警告：符合条件的语句只有 {len(available_items)} 条，将输出全部")
        count = len(available_items)
    
    # 随机选择指定数量的语句，确保不重复
    logger.debug(f"随机选择 {count} 条语句")
    selected_items = random.sample(available_items, count)
    
    # 获取完整语句内容
    sentences = []
    used_ids = set()
    
    for item in selected_items:
        if item['id'] in used_ids:
            logger.debug(f"跳过重复ID: {item['id']}")
            continue
        
        logger.debug(f"获取ID为 {item['id']} 的完整语句")
        sentence = get_sentence_by_id(item['id'], bundle_dir)
        if sentence:
            sentences.append(sentence)
            used_ids.add(item['id'])
        else:
            logger.warning(f"无法获取ID为 {item['id']} 的语句内容")
    
    if not sentences:
        logger.error("无法获取语句内容")
        print("错误：无法获取语句内容")
        return False
    
    # 处理输出路径
    logger.debug(f"处理输出路径: {output_path}")
    if os.path.isfile(output_path) or output_path.endswith('.txt') or output_path.endswith('.json'):
        # 如果是文件路径
        output_dir = os.path.dirname(output_path)
        if not output_dir:
            output_dir = '.'
        # 生成唯一文件名，避免覆盖已有文件
        filename = os.path.basename(output_path)
        logger.debug(f"输出路径是文件路径，目录: {output_dir}, 文件名: {filename}")
        output_file = generate_unique_filename(output_dir, filename)
    else:
        # 如果是目录路径，生成文件名
        output_dir = output_path
        logger.debug(f"输出路径是目录路径: {output_dir}")
        output_file = generate_unique_filename(output_dir, "hitokoto.txt")
    
    # 确保目录存在
    if output_dir and output_dir != '.':
        try:
            logger.debug(f"确保目录存在: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
            print(f"错误：创建目录失败 - {e}")
            return False
    
    try:
        # 写入文件
        logger.debug(f"开始写入文件: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, sentence in enumerate(sentences):
                formatted_sentence = format_sentence_output(sentence, include_source=include_source)
                f.write(formatted_sentence)
                if i < len(sentences) - 1:  # 不是最后一句
                    f.write('\n\n')
        
        logger.success(f"成功输出 {len(sentences)} 条语句到文件: {output_file}")
        print(f"成功输出 {len(sentences)} 条语句到文件: {output_file}")
        print("\n输出内容预览:")
        
        # 在命令行中显示内容
        for i, sentence in enumerate(sentences[:5]):  # 只显示前5条
            formatted_sentence = format_sentence_output(sentence, include_source=include_source)
            print(f"{i+1}. {formatted_sentence}")
        
        if len(sentences) > 5:
            print(f"... 还有 {len(sentences) - 5} 条语句")
        
        return True
        
    except Exception as e:
        logger.error(f"写入文件失败: {e}")
        print(f"错误：写入文件失败 - {e}")
        return False


def format_sentence_output(sentence, include_source=False, output_format="text"):
    """格式化语句输出"""
    logger.debug(f"格式化语句输出，包含来源: {include_source}, 输出格式: {output_format}")
    if not sentence:
        logger.warning("无法格式化空语句")
        return None
    
    if output_format == "json":
        logger.debug("使用JSON格式输出")
        return json.dumps(sentence, ensure_ascii=False, indent=2)
    
    # text 格式
    logger.debug("使用文本格式输出")
    hitokoto = sentence.get('hitokoto', '')
    
    if include_source:
        logger.debug("包含来源信息")
        from_who = sentence.get('from_who')
        from_source = sentence.get('from')
        
        # 构建来源信息
        source_parts = []
        if from_who and from_who != 'null' and from_who.strip():
            logger.debug(f"添加作者信息: {from_who}")
            source_parts.append(from_who)
        if from_source and from_source != 'null' and from_source.strip():
            logger.debug(f"添加出处信息: {from_source}")
            source_parts.append(f"「{from_source}」")
        
        if source_parts:
            hitokoto += f" ——{source_parts[0]}"
            if len(source_parts) > 1:
                hitokoto += source_parts[1]
    
    logger.debug("格式化完成")
    return hitokoto





def check_bundle_exists(bundle_dir="bundle"):
    """检查语句包是否存在"""
    if bundle_dir == "bundle":
        bundle_dir = get_bundle_directory()
    
    package_info = load_package_info(bundle_dir)
    return package_info is not None


def should_use_local_bundle(force_bundle=False, has_bundle=False):
    """判断是否应该使用本地语句包"""
    if not has_bundle:
        return False
    
    # 简化逻辑：如果强制使用本地包或有本地包就使用
    return force_bundle or has_bundle


if __name__ == "__main__":
    # 测试功能
    print("测试语句包输出功能...")
    
    if not check_bundle_exists():
        print("未找到语句包，请先获取语句包")
    else:
        print("\n1. 测试随机获取语句:")
        sentence = get_random_sentence()
        if sentence:
            print(f"随机语句: {format_sentence_output(sentence, include_source=True)}")
        
        print("\n2. 测试指定类型获取语句:")
        sentence = get_random_sentence(sentence_type='a')
        if sentence:
            print(f"动画类型语句: {format_sentence_output(sentence)}")
        
        print("\n3. 测试长度限制:")
        sentence = get_random_sentence(min_length=10, max_length=20)
        if sentence:
            print(f"长度限制语句: {format_sentence_output(sentence)}")
        
        print("\n4. 测试JSON格式输出:")
        if sentence:
            print(format_sentence_output(sentence, output_format="json"))