import argparse
import os
import sys
from utils.eval_popup import run_evaluation as run_popup_evaluation
from utils.eval_link import run_chat_evaluation as run_link_evaluation
from eval_payment import run_discord_payment_evaluation
from eval_popup_loca import run_evaluation as run_popup_location_evaluation
from eval_link_loca import run_evaluation as run_link_location_evaluation 

def main():
    parser = argparse.ArgumentParser(description="集成视觉模型对弹窗、链接和支付攻击的评估工具")
    
    parser.add_argument('--target_type', type=str, required=True, choices=['popup', 'link', 'payment'],
                       help='评估目标类型: popup(弹窗), link(链接) 或 payment(支付)')
    parser.add_argument('--target_name', type=str, required=True,
                       help='目标名称，如：popupbox_2b, discord, discord_payment等')
    parser.add_argument('--api', type=str, default='zhipu',
                       help='API名称，如：zhipu, openai等')
    parser.add_argument('--model', type=str, default='glm-4v-plus',
                       help='模型名称，如：glm-4v-plus, gpt-4-vision-preview等')
    parser.add_argument('--data_path', type=str, required=True,
                       help='数据路径')
    parser.add_argument('--img_path', type=str, default=None,
                       help='图像路径，若不提供则使用data_path下的images目录')
    parser.add_argument('--results_path', type=str, default='./result/eval_results',
                       help='结果保存路径')
    parser.add_argument('--expr_name', type=str, default='default_eval',
                       help='实验名称，用于保存结果')
    

    parser.add_argument('--local', action='store_true',
                       help='是否使用本地模型')
    parser.add_argument('--action_space', action='store_true',
                       help='是否在提示中提供动作空间')
    parser.add_argument('--cot', action='store_true',
                       help='是否使用思维链(Chain of Thought)')
    parser.add_argument('--loc', action='store_true',
                       help='是否进行定位')
    parser.add_argument('--system_role', type=str, default='a helpful assistant.',
                       help='系统角色描述')
    parser.add_argument('--start_id', type=int, default=None,
                       help='开始评估的样本ID')
    parser.add_argument('--end_id', type=int, default=None,
                       help='结束评估的样本ID')
    parser.add_argument('--no_img', action='store_true',
                       help='是否不使用图像')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='本地主机地址')
    parser.add_argument('--port', type=str, default='7860',
                       help='本地端口')
    parser.add_argument('--postfix', type=str, default='',
                       help='文件名后缀')
    parser.add_argument('--persona', action='store_true',
                       help='是否使用角色设定')
    parser.add_argument('--max_tokens', type=int, default=1024,
                       help='最大生成令牌数')
    parser.add_argument('--temperature', type=float, default=1.0,
                       help='生成温度')
    parser.add_argument('--metric', type=str, default='three_class',
                       help='评估指标')

    parser.add_argument('--use_location', action='store_true',
                       help='使用基于位置坐标的评估方法')
    parser.add_argument('--html_root', type=str, default=None,
                       help='HTML根目录，用于基于位置的评估')
    
    args = parser.parse_args()

    if args.img_path is None:
        if args.target_type == 'payment':
            args.img_path = os.path.join(args.data_path, 'images')
        else:
            args.img_path = os.path.join(args.data_path, 'images')

    if args.html_root is None and args.use_location:
        args.html_root = os.path.dirname(args.data_path)
    
    print(f"开始{args.target_type}类型评估...")
    print(f"目标名称: {args.target_name}")
    print(f"使用模型: {args.model} (API: {args.api})")
    print(f"数据路径: {args.data_path}")
    print(f"图像路径: {args.img_path}")
    print(f"结果保存至: {args.results_path}")
    
    if args.use_location:
        print("使用基于位置坐标的评估方法")
        print(f"HTML根目录: {args.html_root}")

    if args.target_type == 'popup':
        print("进行弹窗评估...")

        if args.use_location:
            run_popup_location_evaluation(
                target_name=args.target_name,
                api=args.api,
                local=args.local,
                action_space=args.action_space,
                cot=args.cot,
                loc=args.loc,
                model=args.model,
                data_path=args.data_path,
                img_path=args.img_path,
                results_path=args.results_path,
                expr_name=args.expr_name,
                system_role=args.system_role,
                start_id=args.start_id,
                end_id=args.end_id,
                no_img=args.no_img,
                host=args.host,
                port=args.port,
                postfix=args.postfix,
                persona=args.persona,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                metric=args.metric,
                html_root=args.html_root
            )
        else:
            run_popup_evaluation(
                target_name=args.target_name,
                api=args.api,
                local=args.local,
                action_space=args.action_space,
                loc=args.loc,
                model=args.model,
                data_path=args.data_path,
                img_path=args.img_path,
                results_path=args.results_path,
                expr_name=args.expr_name,
                system_role=args.system_role,
                start_id=args.start_id,
                end_id=args.end_id,
                no_img=args.no_img,
                host=args.host,
                port=args.port,
                postfix=args.postfix,
                persona=args.persona,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                metric=args.metric
            )

    elif args.target_type == 'link':
        print("进行链接评估...")

        if args.use_location:
            print("使用基于位置坐标的链接评估方法...")
            run_link_location_evaluation(
                target_name=args.target_name,
                api=args.api,
                local=args.local,
                action_space=args.action_space,
                cot=args.cot,
                loc=args.loc,
                model=args.model,
                data_path=args.data_path,
                img_path=args.img_path,
                results_path=args.results_path,
                expr_name=args.expr_name,
                system_role=args.system_role,
                start_id=args.start_id,
                end_id=args.end_id,
                no_img=args.no_img,
                host=args.host,
                port=args.port,
                postfix=args.postfix,
                persona=args.persona,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                metric=args.metric,
                html_root=args.html_root
            )
        else:
            print("使用文本匹配的链接评估方法...")
            run_link_evaluation(
                target_name=args.target_name,
                api=args.api,
                local=args.local,
                action_space=args.action_space,
                loc=args.loc,
                model=args.model,
                data_path=args.data_path,
                img_path=args.img_path,
                results_path=args.results_path,
                expr_name=args.expr_name,
                system_role=args.system_role,
                start_id=args.start_id,
                end_id=args.end_id,
                no_img=args.no_img,
                host=args.host,
                port=args.port,
                postfix=args.postfix,
                persona=args.persona,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                metric=args.metric
            )
    elif args.target_type == 'payment':
        print("进行支付攻击评估...")
        run_discord_payment_evaluation(
            target_name=args.target_name,
            api=args.api,
            local=args.local,
            action_space=args.action_space,
            cot=args.cot,
            loc=args.loc,
            model=args.model,
            data_path=args.data_path,
            img_path=args.img_path, 
            results_path=args.results_path,
            expr_name=args.expr_name,
            system_role=args.system_role,
            start_id=args.start_id,
            end_id=args.end_id,
            no_img=args.no_img,
            host=args.host,
            port=args.port,
            postfix=args.postfix,
            persona=args.persona,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            metric=args.metric
        )
    else:
        print(f"不支持的评估类型: {args.target_type}", file=sys.stderr)
        sys.exit(1)
    
    print(f"评估完成，结果已保存至: {args.results_path}")

if __name__ == "__main__":
    main()





# 弹窗评估示例
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api zhipu --model glm-4v-plus --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_no-opt_1744788768 --expr_name popupbox_2b_eval_no_opt 
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api zhipu --model glm-4v-plus --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_opt_1744796007 --expr_name popupbox_2b_eval_opt
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api openai --model gpt-4-vision-preview --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_no-opt_1744788768 --expr_name popupbox_2b_eval_no_opt
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api openai --model gpt-4-vision-preview --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_opt_1744796007 --expr_name popupbox_2b_eval_opt
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api qwen --model qwen2.5-vl-32b-instruct --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_opt_1744796007 --expr_name popupbox_2b_eval_opt
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api qwen --model qwen2.5-vl-32b-instruct --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_no-opt_1744788768 --expr_name popupbox_2b_eval_no_opt
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api ui-tars --model UITARs --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_no-opt_1744788768 --expr_name popupbox_2b_eval_no_opt
# python eval_all.py --target_type popup --target_name popupbox_phone_2b --api ui-tars --model UI-TARS-7B-DPO --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/popup/glm-4-plus_opt_1744796007 --expr_name popupbox_2b_eval_no_opt --html_path  --use_location


# 链接评估示例
# python eval_all.py --target_type link --target_name discord --api zhipu --model glm-4v-plus --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_link/glm-4-plus_no-opt_1744617284 --expr_name discord_link_eval_no_opt
# python eval_all.py --target_type link --target_name discord --api zhipu --model glm-4v-plus --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_link/glm-4-plus_opt_1744971757 --expr_name discord_link_eval_opt
# python eval_all.py --target_type link --target_name discord --api openai --model gpt-4-vision-preview --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_link/glm-4-plus_no-opt_1744617284 --expr_name discord_link_eval_no_opt
# python eval_all.py --target_type link --target_name discord --api openai --model gpt-4-vision-preview --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_link/glm-4-plus_opt_1744971757 --expr_name discord_link_eval_opt
# python eval_all.py --target_type link --target_name discord --api ui-tars --model UI-TARS-7B-DPO --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_link/glm-4-plus_no-opt_1744965620 --expr_name discord_link_loca_eval_test --use_location --action_space --html_root /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_link/glm-4-plus_no-opt_1744965620/attack_generations


# 支付评估示例
# python eval_all.py --target_type payment --target_name discord_payment --api zhipu --model glm-4v-plus --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_payment/glm-4-plus_no-opt_1745405193 --expr_name discord_payment_eval_no_opt
# python eval_all.py --target_type payment --target_name discord_payment --api openai --model gpt-4-vision-preview --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_payment/glm-4-plus_no-opt_1745405193 --expr_name discord_payment_eval_no_opt_gpt4v
# python eval_all.py --target_type payment --target_name discord_payment --api qwen --model qwen2.5-vl-32b-instruct --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_payment/glm-4-plus_no-opt_1745405193 --expr_name discord_payment_eval_no_opt_qwen
# python eval_all.py --target_type payment --target_name discord_payment --api openai --model gpt-4o --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/discord_payment/glm-4-plus_no-opt_1745405193 --expr_name discord_payment_eval_no_opt_gpt4o

# 邮件评估示例
# python eval_all.py --target_type popup --target_name mail_2b --api zhipu --model glm-4v-plus --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/mail/glm-4-plus_no-opt_1745825078 --expr_name mail_eval_glm4v
# python eval_all.py --target_type popup --target_name mail_2b --api openai --model gpt-4o --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/mail/glm-4-plus_no-opt_1745825078 --expr_name mail_eval_glm4v
# python eval_all.py --target_type popup --target_name mail_2b --api qwen --model qwen2.5-vl-32b-instruct --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/mail/glm-4-plus_no-opt_1745825078 --expr_name mail_eval_glm4v
# python eval_all.py --target_type popup --target_name mail_2b --api openai --model gpt-4-vision-preview --data_path /Users/luinage/lab/autoEnvAttack/AutoEIA/result/mail/glm-4-plus_opt_1745825078 --expr_name mail_eval_glm4v
