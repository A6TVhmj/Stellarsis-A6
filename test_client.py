#!/usr/bin/env python3
"""
网站客户端测试脚本
用于验证客户端代码是否语法正确
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_client_syntax():
    """测试客户端代码语法"""
    try:
        import website_client
        print("✓ 客户端代码语法正确")
        return True
    except SyntaxError as e:
        print(f"✗ 语法错误: {e}")
        return False
    except ImportError as e:
        print(f"✗ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

def test_required_modules():
    """测试必需模块是否已安装"""
    modules = ['tkinter', 'ttkbootstrap', 'requests']
    missing = []
    
    for module in modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'ttkbootstrap':
                import ttkbootstrap
            elif module == 'requests':
                import requests
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"✗ 缺少模块: {', '.join(missing)}")
        return False
    else:
        print("✓ 所需模块均已安装")
        return True

if __name__ == "__main__":
    print("网站客户端测试")
    print("="*30)
    
    syntax_ok = test_client_syntax()
    modules_ok = test_required_modules()
    
    print("="*30)
    if syntax_ok and modules_ok:
        print("✓ 所有测试通过！客户端可以运行。")
        print("\n要运行客户端，请执行：")
        print("  python website_client.py")
        print("\n注意：需要有图形界面环境才能显示GUI窗口。")
    else:
        print("✗ 有测试失败，请检查错误信息。")