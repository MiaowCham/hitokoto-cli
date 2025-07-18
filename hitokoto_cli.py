import os
import sys
import argparse
from loguru import logger
from hitokoto_api import get_hitokoto_from_api, format_hitokoto_output
from bundle_get import get_bundle
from bundle_echo import (
    get_random_sentence, get_sentence_by_id, get_sentence_by_uuid,
    format_sentence_output, check_bundle_exists, export_sentences_to_file,
    should_use_local_bundle
)
from bundle_manage import check_bundle_integrity, update_package_info_and_index

# 默认情况下禁用日志输出
logger.remove()
# 添加一个空的处理器，不输出任何内容
logger.add(sys.stderr, level="ERROR", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

VERSION = "0.2.0"

# 检查 PyInstaller 打包环境并为版本信息加入前缀
def is_pyinstaller():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
if is_pyinstaller():
    VERSION = f"build {VERSION}"

# 版本信息
VERSION_INFO = f"""一言(Hitokoto)命令行工具
一个简单的命令行工具，用于获取和显示一言(Hitokoto)语句。支持从在线API获取或使用本地语句包。

版本: hitokoto-cli {VERSION}
项目仓库地址: https://github.com/MiaowCham/hitokoto-cli

特别感谢: 一言官方(https://hitokoto.cn/)
  - 提供了 API 服务(https://developer.hitokoto.cn/sentence/)
  - 提供了语句包下载服务(https://sentences-bundle.hitokoto.cn/)"""

def validate_sentence_type(value):
    """验证语句类型参数的函数"""
    import random
    
    if value is None:
        return None
    
    # 定义帮助显示函数
    def show_type_help():
        print("-t 指令帮助：")
        print("语句类型说明：")
        print("  a: 动画")
        print("  b: 漫画")
        print("  c: 游戏")
        print("  d: 文学")
        print("  e: 原创")
        print("  f: 来自网络")
        print("  g: 其他")
        print("  h: 影视")
        print("  i: 诗词")
        print("  j: 网易云")
        print("  k: 哲学")
        print("  l: 抖机灵")
        print("\n使用方法：")
        print("  -t a     # 获取动画类型的语句")
        print("  -t help  # 显示此帮助信息")
    
    valid_types = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    
    if value == 'none':
        # -t 无参数的情况：显示帮助并随机选择
        show_type_help()
        random_type = random.choice(valid_types)
        print(f"\n错误：-t 参数需要指定类型，请使用 a-l 中的任意字母。")
        print(f"本次将随机选择类型 '{random_type}' 继续执行。\n")
        return random_type
    elif value.lower() == 'help':
        show_type_help()
        sys.exit(0)
    elif value not in valid_types:
        show_type_help()
        print(f"\n错误：无效的语句类型 '{value}'，请使用 a-l 中的任意字母。")
        print("本次将使用默认设置（随机类型）继续执行。\n")
        return None  # 返回None表示使用默认值
    
    return value


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='一言(Hitokoto)命令行工具\n一个简单的命令行工具，用于获取和显示一言(Hitokoto)语句。支持从在线API获取或使用本地语句包。',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # -a, --api 参数，支持无附加参数
    parser.add_argument('-a', '--api', nargs='?', const='in', default=None,
                       choices=['in', 'cn'], 
                       help='强制调用指定API (默认:in=国际, cn=中国)')
    
    # -b, --bundle 参数
    parser.add_argument('-b', '--bundle', action='store_true', 
                       help='强制使用语句包')
    
    # -t, --type 参数，支持无附加参数
    parser.add_argument('-t', '--type', nargs='?', const='none', default=None,
                       help='语句类型 (默认:none=随机, a-l, 或输入 help 查看详细说明)')
    
    # --min 参数
    parser.add_argument('--min', type=int, dest='min_length',
                       help='指定最小字符数')
    
    # --max 参数
    parser.add_argument('--max', type=int, dest='max_length',
                       help='指定最大字符数')
    
    # -f, --from 参数
    parser.add_argument('-f', '--from', action='store_true', dest='include_source',
                       help='在输出中包含来源')
    
    # -i, --id 参数
    parser.add_argument('-i', '--id', dest='sentence_id',
                       help='精确查找指定语句ID/UUID (仅支持本地)')
    
    # --encode 参数
    parser.add_argument('--encode', choices=['text', 'json'], default='text',
                       help='输出格式')
    
    # -c, --check-bundle 参数
    parser.add_argument('-c', '--check-bundle', action='store_true', dest='check_bundle_flag',
                       help='检查语句包状态')
    
    # -d, --delete-bundle 参数
    parser.add_argument('-d', '--delete-bundle', action='store_true', dest='delete_bundle_flag',
                       help='删除本地语句包')
    
    # -u, --update-index 参数
    parser.add_argument('-u', '--update-index', action='store_true', dest='update_index_flag',
                       help='更新索引文件')
    
    # -g, --get-bundle 参数，支持无附加参数
    parser.add_argument('-g', '--get-bundle', nargs='?', const='of', default=None,
                       choices=['of', 'gh', 'jsd'], dest='get_bundle_source',
                       help='获取语句包 (默认:of, 可选:gh, jsd)')
    
    # -e, --echo 参数，支持无附加参数
    parser.add_argument('-e', '--echo', nargs='?', const='10', default=None,
                       dest='echo_count', help='输出至文件的语句数量，默认10条')
    
    # -p, --path 参数
    parser.add_argument('-p', '--path', dest='echo_path',
                       help='输出文件路径')
    
    # --debug 参数
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式，显示详细日志信息')
    
    # -v, --version 参数
    parser.add_argument('-v', '--version', action='version', version=VERSION_INFO,
                       help='显示版本信息')
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 提取参数
    api = args.api
    force_bundle = args.bundle
    sentence_type = validate_sentence_type(args.type)
    min_length = args.min_length
    max_length = args.max_length
    include_source = args.include_source
    sentence_id = args.sentence_id
    encode = args.encode
    check_bundle_flag = args.check_bundle_flag
    delete_bundle_flag = args.delete_bundle_flag
    update_index_flag = args.update_index_flag
    get_bundle_source = args.get_bundle_source
    echo_count = args.echo_count
    echo_path = args.echo_path
    debug = args.debug
    
    # 处理调试模式
    if debug:
        # 移除默认的处理器
        logger.remove()
        # 添加新的处理器，设置日志级别为DEBUG
        logger.add(sys.stderr, level="DEBUG", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
        logger.debug("调试模式已启用")
    
    # 注意：语句类型参数验证已在 validate_sentence_type 回调函数中处理
    
    # 处理语句包获取操作
    if get_bundle_source:
        print(f"开始获取语句包，来源: {get_bundle_source}")
        logger.info(f"开始获取语句包，来源: {get_bundle_source}")
        success, info, error = get_bundle(get_bundle_source)
        
        if success:
            if error:  # 部分成功的情况
                print(f"\n语句包获取部分成功！")
                print(f"警告: {error}")
                logger.warning(f"语句包获取部分成功！警告: {error}")
            else:  # 完全成功
                print("\n语句包获取完全成功！")
                logger.success("语句包获取完全成功！")
            
            print(f"主要来源: {info['source']}")
            print(f"文件数量: {info['files_amount']}")
            print(f"语句总数: {info['amount']}")
            logger.debug(f"语句包信息: 主要来源={info['source']}, 文件数量={info['files_amount']}, 语句总数={info['amount']}")
            
            # 显示来源使用情况
            if 'source_usage' in info and info['source_usage']:
                print("来源使用统计:")
                logger.debug("来源使用统计:")
                for src, count in info['source_usage'].items():
                    print(f"  {src}: {count} 个文件")
                    logger.debug(f"  {src}: {count} 个文件")
            
            # 显示失败的类型
            if 'failed_types' in info and info['failed_types']:
                print(f"未能获取的类型: {', '.join(info['failed_types'])}")
                logger.warning(f"未能获取的类型: {', '.join(info['failed_types'])}")
            
            print(f"更新时间: {info['last_update']}")
            logger.debug(f"更新时间: {info['last_update']}")
            return 0
        else:
            print(f"\n语句包获取失败: {error}")
            logger.error(f"语句包获取失败: {error}")
            return 1
    
    # 处理语句包检查操作
    if check_bundle_flag:
        logger.debug("开始检查语句包状态")
        if not check_bundle_exists():
            print("未找到语句包，请先使用 -g 参数获取语句包")
            logger.warning("未找到语句包，请先使用 -g 参数获取语句包")
            return 1
        
        print("正在检查语句包完整性...")
        logger.info("正在检查语句包完整性...")
        is_valid, message = check_bundle_integrity()
        print(message)
        if is_valid:
            logger.success(f"语句包检查完成: {message}")
        else:
            logger.error(f"语句包检查失败: {message}")
        return 0 if is_valid else 1
    
    # 处理删除语句包操作
    if delete_bundle_flag:
        import shutil
        from bundle_echo import get_bundle_directory
        
        logger.debug("开始删除语句包操作")
        bundle_dir = get_bundle_directory()
        if os.path.exists(bundle_dir):
            try:
                logger.info(f"正在删除语句包目录: {bundle_dir}")
                shutil.rmtree(bundle_dir)
                print("语句包已删除")
                logger.success("语句包已成功删除")
            except Exception as e:
                print(f"删除语句包失败: {e}")
                logger.error(f"删除语句包失败: {e}")
                return 1
        else:
            print("未找到语句包")
            logger.warning("未找到语句包，无需删除")
        return 0
    
    # 处理更新索引操作
    if update_index_flag:
        logger.debug("开始更新索引操作")
        if not check_bundle_exists():
            print("未找到语句包，请先使用 -g 参数获取语句包")
            logger.warning("未找到语句包，请先使用 -g 参数获取语句包")
            return 1
        
        try:
            logger.info("正在更新索引文件...")
            update_package_info_and_index()
            print("索引文件更新完成")
            logger.success("索引文件更新完成")
        except Exception as e:
            print(f"更新索引文件失败: {e}")
            logger.error(f"更新索引文件失败: {e}")
            return 1
        return 0
    
    # 处理批量输出到文件操作
    if echo_count or echo_path:
        logger.debug("开始批量输出到文件操作")
        # 确定输出数量
        try:
            count = int(echo_count) if echo_count else 10  # 默认输出10条
            logger.debug(f"输出数量: {count}")
        except ValueError:
            print("错误：数量参数必须是整数")
            logger.error(f"数量参数错误: {echo_count} 不是有效的整数")
            return 1
        
        # 确定输出路径
        if echo_path:
            output_path = echo_path
        else:
            output_path = "hitokoto.txt"  # 默认输出文件名
        logger.debug(f"输出路径: {output_path}")
        
        if not check_bundle_exists():
            print("未找到语句包，请先使用 -g 参数获取语句包")
            logger.warning("未找到语句包，请先使用 -g 参数获取语句包")
            return 1
        
        # 解析语句类型
        sentence_types = None
        if sentence_type:
            sentence_types = list(sentence_type)
            logger.debug(f"语句类型: {sentence_types}")
        
        logger.info(f"开始导出 {count} 条语句到 {output_path}")
        success = export_sentences_to_file(
            count=count,
            output_path=output_path,
            sentence_types=sentence_types,
            min_length=min_length,
            max_length=max_length,
            include_source=include_source
        )
        
        if success:
            logger.success(f"成功导出语句到文件: {output_path}")
        else:
            logger.error("导出语句到文件失败")
        
        return 0 if success else 1
    
    # 检查是否有本地语句包
    has_bundle = check_bundle_exists()
    logger.debug(f"本地语句包状态: {'存在' if has_bundle else '不存在'}")
    
    # 决定使用API还是本地语句包
    use_bundle = False
    if force_bundle:
        logger.debug("用户强制使用本地语句包")
        if not has_bundle:
            print("未找到语句包，请先使用 -g 参数获取语句包")
            logger.warning("未找到语句包，请先使用 -g 参数获取语句包")
            return 1
        use_bundle = should_use_local_bundle(force_bundle=True, has_bundle=has_bundle)
    elif api:
        logger.debug(f"用户指定使用API: {api}")
        use_bundle = False  # 强制使用API
    else:
        use_bundle = should_use_local_bundle(force_bundle=False, has_bundle=has_bundle)
        logger.debug(f"自动选择数据源: {'本地语句包' if use_bundle else 'API'}")
    
    # 使用本地语句包
    if use_bundle:
        if debug:
            print("[DEBUG] 使用本地语句包", file=sys.stderr)
        logger.info("使用本地语句包获取语句")
        sentence = None
        
        # 精确查找指定ID/UUID
        if sentence_id:
            logger.debug(f"尝试查找ID/UUID: {sentence_id}")
            # 尝试作为数字ID
            try:
                id_num = int(sentence_id)
                logger.debug(f"尝试作为数字ID: {id_num}")
                sentence = get_sentence_by_id(id_num)
            except ValueError:
                # 尝试作为UUID
                logger.debug(f"尝试作为UUID: {sentence_id}")
                sentence = get_sentence_by_uuid(sentence_id)
            
            if not sentence:
                print(f"未找到ID/UUID为 {sentence_id} 的语句")
                logger.error(f"未找到ID/UUID为 {sentence_id} 的语句")
                return 1
            logger.success(f"成功找到ID/UUID为 {sentence_id} 的语句")
        else:
            # 随机获取语句
            logger.debug(f"随机获取语句，类型: {sentence_type}, 最小长度: {min_length}, 最大长度: {max_length}")
            sentence = get_random_sentence(
                sentence_type=sentence_type,
                min_length=min_length,
                max_length=max_length
            )
            
            if not sentence:
                print("未找到符合条件的语句")
                logger.error("未找到符合条件的语句")
                return 1
            logger.success("成功获取随机语句")
        
        # 格式化输出
        logger.debug(f"格式化输出，包含来源: {include_source}, 输出格式: {encode}")
        output = format_sentence_output(
            sentence,
            include_source=include_source,
            output_format=encode
        )
        print(output)
        return 0
    
    # 使用API调用功能
    logger.info(f"使用API获取语句，API类型: {api if api else '自动'}")
    logger.debug(f"API调用参数: 类型={sentence_type}, 最小长度={min_length}, 最大长度={max_length}")
    
    result = get_hitokoto_from_api(
        api_type=api,
        sentence_type=sentence_type,
        min_length=min_length,
        max_length=max_length
    )
    
    if result:
        logger.success("API调用成功")
        logger.debug(f"API返回数据: {result}")
        # 格式化输出
        logger.debug(f"格式化输出，包含来源: {include_source}, 输出格式: {encode}")
        output = format_hitokoto_output(
            result, 
            include_source=include_source, 
            output_format=encode
        )
        print(output)
    else:
        print("获取一言失败，请检查网络连接")
        logger.error("API调用失败，请检查网络连接")
        return 1
    
    return 0


if __name__ == '__main__':
    main()