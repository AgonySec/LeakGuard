import argparse
import logging
import time
from LeakGuard.google_search import search_google
from LeakGuard.github_search import search_github
from LeakGuard.email_leak import check_one_email,batch_process_emails_for
from LeakGuard.pass_leak import check_pass_leak,batch_check_pass_leak
from LeakGuard.utils import set_sensitiveWords,set_blacklistUsers
from LeakGuard.hunter_search import search_hunter


# 设置日志
logging.basicConfig(level=logging.INFO)
def parse_arguments():
    parser = argparse.ArgumentParser(description="LeakGuard 是一款 邮箱、密码泄露和关键字 综合检测工具  By Agony")
    parser.add_argument('-e', '--email', required=False, help='输入要测试的邮箱地址')
    parser.add_argument('-ef', '--email_file', required=False, help='输入包含多个邮箱地址的文件路径')
    parser.add_argument('-p', '--password', required=False, help='输入要测试的密码')
    parser.add_argument('-pf', '--passFile', required=False, help='输入包含多个密码的文件路径')
    parser.add_argument('-o', '--output', required=False, help='输出文件名，不包含后缀，默认为Google_email_timestamp.json')
    parser.add_argument('-c', action='store_true', help='信息收集模式')
    parser.add_argument('-bU', type=argparse.FileType('r', encoding='utf8'), help='设置黑名单用户文件')
    parser.add_argument('-sW', type=argparse.FileType('r', encoding='utf8'), help='设置敏感词文件')
    parser.add_argument('-google', '--google_search', required=False, help='指定要提取的邮箱后缀，例如 @qq.com, 从Google搜索中提取指定域名邮箱')
    parser.add_argument('-ggf', '--google_file', required=False, help='从txt文件中读取邮箱后缀,进行谷歌搜索')
    parser.add_argument('-github', '--github_search', help='指定关键字,进行GitHub搜索')
    parser.add_argument('-gtf', '--github_file', required=False, help='指定关键字文件,进行GitHub批量搜索')
    parser.add_argument('-hunter', '--hunter_search', help='输入网站域名，hunter.io搜索邮箱')
    parser.add_argument('-m', '--mode', choices=['json', 'xlsx'], default='xlsx', help='指定输出格式，支持 json 或 xlsx，默认为 xlsx')
    return parser.parse_args()


def setup_blacklist_and_sensitive_words(args):
    if args.bU:
        BlacklistUsers = [x.strip('\n') for x in args.bU.readlines()]
        set_blacklistUsers(BlacklistUsers)
    if args.sW:
        SensitiveWords = [x.strip('\n') for x in args.sW.readlines()]
        set_sensitiveWords(SensitiveWords)

def handle_github_search(args, output_file, mode):
    if args.github_search:
        search_github(query=args.github_search, output_file=output_file, mode=mode)
    if args.github_file:
        search_github(file=args.github_file, output_file=output_file, mode=mode)

def handle_google_search(args, output_file, mode):
    if args.google_search:
        search_google(email_suffix=args.google_search, output_file=output_file, mode=mode)
    if args.google_file:
        search_google(file=args.google_file, output_file=output_file, mode=mode)

def handle_email_leak(args, output_file, mode):
    if args.email:
        check_one_email(args.email, output_file, mode)
    if args.email_file:
        batch_process_emails_for(args.email_file, output_file, mode)

def handle_password_leak(args):
    if args.password:
        check_pass_leak(args.password)
    if args.passFile:
        batch_check_pass_leak(args.passFile)

def handle_hunter_search(args, output_file, mode):
    if args.hunter_search:
        search_hunter(domain=args.hunter_search, output_file=output_file, mode=mode)

def main():
    start_time = time.time()
    args = parse_arguments()

    output_file = args.output
    mode = args.mode

    if args.email and args.email_file:
        logging.error("[!]请输入单个邮箱地址或文件路径，不要同时输入！")
        return

    setup_blacklist_and_sensitive_words(args)

    if args.c:
        print("todo")

    handle_github_search(args, output_file, mode)
    handle_google_search(args, output_file, mode)
    handle_email_leak(args, output_file, mode)
    handle_password_leak(args)
    handle_hunter_search(args, output_file, mode)

    if not any([args.email, args.email_file, args.passFile, args.hunter_search, args.password, args.google_search, args.google_file, args.c, args.github_search, args.github_file]):
        args.print_help()

    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"[+]检测程序所花时间：{elapsed_time}")

if __name__ == "__main__":
    main()