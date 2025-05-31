import os
import argparse
import importlib
import time
import sys
from utils.attack_popup import do_annotate_popup
from utils.attack_chat_link import do_annotate_discord
from targets import TARGETS
import builtins

def main():
    parser = argparse.ArgumentParser(description="运行不同类型的环境攻击测试")
    
    parser.add_argument('--target', type=str, default='discord_link',
                        choices=['discord_link', 'discord_payment', 'mail', 'popup'],
                        help='攻击类型: discord_link, discord_payment, mail, popup')
    parser.add_argument('--api', type=str, default='zhipu',
                        help='API类型: zhipu, openai, 等')
    parser.add_argument('--model', type=str, default='glm-4-plus',
                        help='模型名称: glm-4-plus, gpt-4o, 等')
    parser.add_argument('--samples', type=int, default=50,
                        help='生成样本数量')
    parser.add_argument('--output_dir', type=str, default='',
                        help='结果输出目录（如果为空，将使用默认目录）')
    parser.add_argument('--optimize', action='store_true', default=True,
                        help='启用迭代优化（默认开启）')
    parser.add_argument('--no-optimize', action='store_false', dest='optimize',
                        help='禁用迭代优化')
    parser.add_argument('--max_iter', type=int, default=5,
                        help='最大迭代次数（仅当开启优化时有效）')
    
    args = parser.parse_args()

    ROOT_DIR = '/Users/luinage/lab/autoEnvAttack/AutoEIA'

    if not args.output_dir:
        timestamp = int(time.time())
        optimize_flag = "opt" if args.optimize else "no-opt"
        args.output_dir = os.path.join(ROOT_DIR, f'result/{args.target}/{args.model}_{optimize_flag}_{timestamp}')

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'images'), exist_ok=True)

    print(f"攻击类型: {args.target}")
    print(f"API: {args.api}")
    print(f"模型: {args.model}")
    print(f"样本数量: {args.samples}")
    print(f"迭代优化: {'开启' if args.optimize else '关闭'}")
    if args.optimize:
        print(f"最大迭代次数: {args.max_iter}")
    print(f"输出目录: {args.output_dir}")
    
    os.environ['ENABLE_OPTIMIZATION'] = "1" if args.optimize else "0"
    os.environ['MAX_ITER_STEPS'] = str(args.max_iter)
    
    if args.target == 'discord_link':
        try:
            print("正在执行Discord链接攻击...")
            from utils.attack_chat_link import do_annotate_discord
            do_annotate_discord(args.output_dir, args.samples, args.model, args.api)
        except Exception as e:
            print(f"执行Discord链接攻击失败: {e}")
            import traceback
            traceback.print_exc()
            
    elif args.target == 'discord_payment':
        try:
            from attack_chat_pay import do_annotate_discord
            print("正在执行Discord支付攻击...")
            do_annotate_discord(args.output_dir, args.samples, args.model, args.api)
        except Exception as e:
            print(f"执行Discord支付攻击失败: {e}")
            import traceback
            traceback.print_exc()
            
    elif args.target == 'mail':
        try:
            from attack_mail import do_annotate
            print("正在执行邮件攻击...")
            target_name = 'mail_2b'
            do_annotate(target_name, args.output_dir, args.samples, args.model, args.api)
        except Exception as e:
            print(f"执行邮件攻击失败: {e}")
            import traceback
            traceback.print_exc()
            
    elif args.target == 'popup':
        try:
            print("正在执行弹窗攻击...")
            target_name = 'popupbox_phone_2b'
            builtins.target_name = target_name
            do_annotate_popup(target_name, args.output_dir, args.samples, args.model, args.api)
        except Exception as e:
            print(f"执行弹窗攻击失败: {e}")
            import traceback
            traceback.print_exc()
            
    else:
        print(f"未知的攻击类型: {args.target}")
        sys.exit(1)
    
    print(f"攻击执行完成! 结果已保存到: {args.output_dir}")

if __name__ == "__main__":
    main()

# Discord链接攻击（启用优化）
# python run_attack.py --target discord_link --api zhipu --model glm-4-plus --samples 50 --optimize --max_iter 5

# Discord链接攻击（禁用优化）
# python run_attack.py --target discord_link --api zhipu --model glm-4-plus --samples 50 --no-optimize

# Discord支付攻击(禁用优化)
# python run_attack.py --target discord_payment --api zhipu --model glm-4-plus --samples 50 --no-optimize

# Discord支付攻击（启用优化）
# python run_attack.py --target discord_payment --api zhipu --model glm-4-plus --samples 50 --optimize --max_iter 10

# 邮件攻击（未开放优化）
# python run_attack.py --target mail --api zhipu --model glm-4-plus --samples 50

# 弹窗攻击（启用优化）
# python run_attack.py --target popup --api openai --model gpt-4o --samples 50 --optimize --max_iter 10


# 弹窗攻击（禁用优化）
# python run_attack.py --target popup --api zhipu --model glm-4-plus --samples 50 --no-optimize



