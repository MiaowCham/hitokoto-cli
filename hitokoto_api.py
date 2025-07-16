import requests
import json
import sys
from loguru import logger


def get_hitokoto_from_api(api_type=None, sentence_type=None, min_length=None, max_length=None):
    """
    从一言API获取语句
    
    Args:
        api_type: API类型，'in'表示国际API，'cn'表示中国API，None表示优先使用国际API
        sentence_type: 语句类型，如'a', 'b', 'c'等
        min_length: 最小长度
        max_length: 最大长度
    
    Returns:
        dict: 成功时返回完整的JSON数据，失败时返回None
    """
    logger.debug(f"从一言API获取语句，API类型: {api_type}, 语句类型: {sentence_type}, 最小长度: {min_length}, 最大长度: {max_length}")
    
    # API地址
    international_api = "https://international.v1.hitokoto.cn/"
    china_api = "https://v1.hitokoto.cn/"
    
    # 构建请求参数
    params = {}
    if sentence_type:
        params['c'] = sentence_type
        logger.debug(f"添加语句类型参数: c={sentence_type}")
    if min_length is not None:
        params['min_length'] = min_length
        logger.debug(f"添加最小长度参数: min_length={min_length}")
    if max_length is not None:
        params['max_length'] = max_length
        logger.debug(f"添加最大长度参数: max_length={max_length}")
    
    # 确定API调用顺序
    if api_type == 'cn':
        apis_to_try = [china_api]
        logger.debug(f"使用中国API: {china_api}")
    elif api_type == 'in':
        apis_to_try = [international_api]
        logger.debug(f"使用国际API: {international_api}")
    else:
        # 默认优先使用国际API，失败后尝试中国API
        apis_to_try = [international_api, china_api]
        logger.debug(f"优先使用国际API，失败后尝试中国API")
    
    # 尝试调用API
    for api_url in apis_to_try:
        try:
            logger.debug(f"尝试调用API: {api_url}, 参数: {params}")
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()  # 如果状态码不是200会抛出异常
            
            # 解析JSON响应
            logger.debug(f"API调用成功，状态码: {response.status_code}")
            data = response.json()
            logger.success(f"成功从API获取语句: {api_url}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"调用API失败: {api_url} - {str(e)}")
            print(f"调用API失败: {api_url} - {str(e)}")
            continue
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON失败: {api_url} - {str(e)}")
            print(f"解析JSON失败: {api_url} - {str(e)}")
            continue
    
    # 所有API都失败了
    logger.warning("所有API调用都失败了")
    return None


def format_hitokoto_output(data, include_source=False, output_format='text'):
    """
    格式化一言输出
    
    Args:
        data: 从API获取的JSON数据
        include_source: 是否包含来源信息
        output_format: 输出格式，'text'或'json'
    
    Returns:
        str: 格式化后的输出字符串
    """
    logger.debug(f"格式化一言输出，包含来源: {include_source}, 输出格式: {output_format}")
    if not data:
        logger.warning("无法格式化空数据")
        return "获取一言失败"
    
    if output_format == 'json':
        logger.debug("使用JSON格式输出")
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    # text格式输出
    logger.debug("使用文本格式输出")
    hitokoto_text = data.get('hitokoto', '')
    
    if include_source:
        logger.debug("包含来源信息")
        from_who = data.get('from_who')
        from_source = data.get('from')
        
        # 构建来源信息
        source_parts = []
        if from_who and from_who not in [None, 'null', '']:
            logger.debug(f"添加作者信息: {from_who}")
            source_parts.append(from_who)
        if from_source and from_source not in [None, 'null', '']:
            logger.debug(f"添加出处信息: {from_source}")
            source_parts.append(f"「{from_source}」")
        
        if source_parts:
            if len(source_parts) == 2:
                # 有作者和来源
                logger.debug("添加作者和出处")
                hitokoto_text += f" —— {source_parts[0]}{source_parts[1]}"
            else:
                # 只有作者或只有来源
                logger.debug("只添加作者或出处")
                hitokoto_text += f" —— {source_parts[0]}"
    
    logger.debug("格式化完成")
    return hitokoto_text


if __name__ == "__main__":
    # 测试代码
    print("测试国际API:")
    result = get_hitokoto_from_api(api_type='in')
    if result:
        print(format_hitokoto_output(result, include_source=False))
        print("\n包含来源:")
        print(format_hitokoto_output(result, include_source=True))
        print("\nJSON格式:")
        print(format_hitokoto_output(result, output_format='json'))
    else:
        print("API调用失败")