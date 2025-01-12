import utils
import tkinter as tk
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="视频处理工具")
    parser.add_argument("--gui", action="store_true", help="打开 GUI 界面")
    parser.add_argument("--video", type=str, help="输入视频文件或文件夹路径")
    parser.add_argument(
        "--out", type=str, help="输出文件夹路径（默认与输入视频文件路径相同）"
    )
    parser.add_argument(
        "--compress",
        type=int,
        default=28,
        help="压缩视频，设置 CRF 值（0-51，越小质量越高，默认 28）",
    )
    parser.add_argument(
        "--accelerate",
        type=float,
        default=2.0,
        help="加速视频，设置加速倍数（默认 2.0）",
    )
    parser.add_argument(
        "--gif", type=int, default=1080, help="转换为 GIF，设置分辨率宽度（默认 1080）"
    )

    args = parser.parse_args()

    if args.gui:
        root = tk.Tk()
        app = utils.VideoToolApp(root)
        root.mainloop()
    else:
        if not args.video:
            print("错误：未指定输入视频文件或文件夹路径。")
            parser.print_help()  # 显示帮助信息
            return

        # 如果未指定输出路径，则默认使用输入视频文件的路径
        if not args.out:
            if os.path.isfile(args.video):
                args.out = os.path.dirname(args.video)  # 使用视频文件所在的目录
            elif os.path.isdir(args.video):
                args.out = args.video  # 使用文件夹本身
            else:
                print("错误：输入路径无效。")
                parser.print_help()  # 显示帮助信息
                return

        # 根据参数执行相应的操作
        if args.compress:
            output_path = os.path.join(
                args.out, f"compressed_{utils.get_timestamp()}.mp4"
            )
            utils.compress_video(args.video, output_path, args.compress)
        elif args.accelerate:
            output_path = os.path.join(
                args.out, f"accelerated_{utils.get_timestamp()}.mp4"
            )
            utils.accelerate_video(args.video, output_path, args.accelerate)
        elif args.gif:
            output_path = os.path.join(
                args.out, f"converted_{utils.get_timestamp()}.gif"
            )
            utils.convert_to_gif(args.video, output_path, scale=args.gif)
        else:
            print("错误：未指定操作类型（--compress, --accelerate, --gif）。")
            parser.print_help()  # 显示帮助信息


if __name__ == "__main__":
    main()
