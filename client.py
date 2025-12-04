#!/usr/bin/env python3
"""
Stellarsis 聊天论坛系统客户端
使用 ttkbootstrap 和 requests 构建
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import requests
import json
import threading
import time
from datetime import datetime
import webbrowser
from typing import Optional, Dict, List
import re


class StellarsisClient:
    def __init__(self):
        # 配置服务器地址
        self.base_url = "http://localhost:5000"  # 可以修改为实际的服务器地址
        
        # 用户会话信息
        self.session = requests.Session()
        self.current_user = None
        self.current_room_id = None
        self.current_section_id = None
        self.current_thread_id = None
        
        # 主题相关
        self.themes = [
            'cosmo', 'flatly', 'journal', 'litera', 'lumen', 'minty', 
            'pulse', 'sandstone', 'united', 'yeti', 'cerulean', 'darkly',
            'superhero', 'solar', 'cyborg', 'vapor', 'morph', 'quartz',
            'simplex', 'slate', 'solar', 'spacelab', 'washington'
        ]
        self.current_theme = 'cosmo'  # 默认主题
        
        # 创建主窗口
        self.setup_window()
        
        # 显示登录界面
        self.show_login()
    
    def setup_window(self):
        """设置主窗口"""
        self.root = ttkb.Window()
        self.root.title("Stellarsis 聊天论坛系统客户端")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置主题
        self.style = ttkb.Style(theme=self.current_theme)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    def show_login(self):
        """显示登录界面"""
        # 清除主框架内容
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建登录框架
        login_frame = ttk.LabelFrame(self.main_frame, text="用户登录", padding=20)
        login_frame.pack(fill=X, padx=50, pady=50)
        
        # 用户名
        ttk.Label(login_frame, text="用户名:").grid(row=0, column=0, sticky=W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(login_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # 密码
        ttk.Label(login_frame, text="密码:").grid(row=1, column=0, sticky=W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # 登录按钮
        login_btn = ttk.Button(login_frame, text="登录", command=self.login, bootstyle="primary")
        login_btn.grid(row=2, column=0, columnspan=2, pady=15)
        
        # 绑定回车键
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # 设置焦点
        self.username_entry.focus()
    
    def login(self):
        """执行登录"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                data={
                    'username': username,
                    'password': password
                }
            )
            
            if response.status_code == 200:
                # 检查是否重定向到聊天页面
                if '/chat' in response.url or '/forum' in response.url:
                    self.current_user = username
                    self.show_main_interface()
                else:
                    # 检查响应内容是否有错误信息
                    if '无效的用户名或密码' in response.text or '错误' in response.text:
                        messagebox.showerror("登录失败", "用户名或密码错误")
                    else:
                        messagebox.showerror("登录失败", "登录失败，请重试")
            else:
                messagebox.showerror("登录失败", f"服务器返回错误: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("连接错误", f"无法连接到服务器: {self.base_url}")
        except Exception as e:
            messagebox.showerror("错误", f"登录时发生错误: {str(e)}")
    
    def logout(self):
        """登出"""
        try:
            self.session.get(f"{self.base_url}/logout")
        except:
            pass  # 忽略登出错误
        
        self.current_user = None
        self.show_login()
    
    def show_main_interface(self):
        """显示主界面"""
        # 清除主框架内容
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面布局
        self.create_main_layout()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="登出", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        
        # 主题子菜单
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="主题", menu=theme_menu)
        for theme in self.themes:
            theme_menu.add_command(
                label=theme.title(), 
                command=lambda t=theme: self.change_theme(t)
            )
        
        settings_menu.add_command(label="用户资料", command=self.show_profile)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def change_theme(self, theme_name):
        """更改主题"""
        try:
            self.style.theme_use(theme_name)
            self.current_theme = theme_name
            messagebox.showinfo("主题更改", f"主题已更改为: {theme_name}")
        except Exception as e:
            messagebox.showerror("错误", f"更改主题失败: {str(e)}")
    
    def create_main_layout(self):
        """创建主界面布局"""
        # 创建主分隔框架
        main_paned = ttk.PanedWindow(self.main_frame, orient=VERTICAL)
        main_paned.pack(fill=BOTH, expand=True)
        
        # 顶部框架 - 导航栏
        top_frame = ttk.Frame(main_paned)
        main_paned.add(top_frame, weight=0)
        
        # 用户信息和导航按钮
        ttk.Label(top_frame, text=f"用户: {self.current_user}", font=('Arial', 10, 'bold')).pack(side=LEFT, padx=10, pady=5)
        
        # 在线用户数显示
        self.online_count_label = ttk.Label(top_frame, text="在线: 0", font=('Arial', 10))
        self.online_count_label.pack(side=LEFT, padx=10, pady=5)
        
        # 更新在线用户数
        self.update_online_count()
        # 设置定时器每30秒更新一次在线用户数
        self.schedule_online_count_update()
        
        nav_frame = ttk.Frame(top_frame)
        nav_frame.pack(side=RIGHT, padx=10, pady=5)
        
        ttk.Button(nav_frame, text="聊天", command=self.show_chat_interface, bootstyle="outline").pack(side=LEFT, padx=5)
        ttk.Button(nav_frame, text="论坛", command=self.show_forum_interface, bootstyle="outline").pack(side=LEFT, padx=5)
        ttk.Button(nav_frame, text="个人设置", command=self.show_profile, bootstyle="outline").pack(side=LEFT, padx=5)
        
        # 主内容框架
        content_paned = ttk.PanedWindow(main_paned, orient=HORIZONTAL)
        main_paned.add(content_paned, weight=1)
        
        # 左侧导航面板
        self.nav_frame = ttk.Frame(content_paned)
        content_paned.add(self.nav_frame, weight=0)
        
        # 右侧内容面板
        self.content_frame = ttk.Frame(content_paned)
        content_paned.add(self.content_frame, weight=1)
        
        # 默认显示聊天界面
        self.show_chat_interface()
    
    def show_chat_interface(self):
        """显示聊天界面"""
        # 清除内容框架
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 清除导航框架
        for widget in self.nav_frame.winfo_children():
            widget.destroy()
        
        # 创建聊天导航
        ttk.Label(self.nav_frame, text="聊天室", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 加载聊天室列表
        self.load_chat_rooms()
    
    def load_chat_rooms(self):
        """加载聊天室列表"""
        try:
            # 尝试通过API获取聊天室列表
            response = self.session.get(f"{self.base_url}/api/chat/rooms")
            if response.status_code == 200:
                data = response.json()
                rooms = data.get('rooms', [])
            else:
                # 如果API调用失败，使用默认列表
                rooms = [
                    {"id": 1, "name": "大厅", "description": "主要聊天室"},
                    {"id": 2, "name": "技术讨论", "description": "技术相关话题"},
                    {"id": 3, "name": "闲聊", "description": "非正式聊天"}
                ]
            
            for room in rooms:
                btn = ttk.Button(
                    self.nav_frame,
                    text=room["name"],
                    command=lambda r=room: self.select_chat_room(r["id"], r["name"]),
                    bootstyle="outline"
                )
                btn.pack(fill=X, padx=5, pady=2)
                
        except Exception as e:
            # 如果API调用失败，使用默认列表
            rooms = [
                {"id": 1, "name": "大厅", "description": "主要聊天室"},
                {"id": 2, "name": "技术讨论", "description": "技术相关话题"},
                {"id": 3, "name": "闲聊", "description": "非正式聊天"}
            ]
            
            for room in rooms:
                btn = ttk.Button(
                    self.nav_frame,
                    text=room["name"],
                    command=lambda r=room: self.select_chat_room(r["id"], r["name"]),
                    bootstyle="outline"
                )
                btn.pack(fill=X, padx=5, pady=2)
    
    def select_chat_room(self, room_id, room_name):
        """选择聊天室"""
        self.current_room_id = room_id
        
        # 清除内容框架
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建聊天界面
        self.create_chat_room_interface(room_name)
        
        # 加载聊天历史
        self.load_chat_history()
    
    def create_chat_room_interface(self, room_name):
        """创建聊天室界面"""
        # 房间标题
        ttk.Label(self.content_frame, text=f"房间: {room_name}", font=('Arial', 14, 'bold')).pack(pady=5)
        
        # 聊天消息显示区域
        chat_frame = ttk.Frame(self.content_frame)
        chat_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # 创建文本框和滚动条
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            height=20
        )
        self.chat_text.pack(side=tk.LEFT, fill=BOTH, expand=True)
        
        # 输入区域
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(fill=X, pady=5)
        
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(input_frame, textvariable=self.message_var)
        self.message_entry.pack(side=tk.LEFT, fill=X, expand=True, padx=(0, 5))
        
        send_btn = ttk.Button(input_frame, text="发送", command=self.send_chat_message, bootstyle="primary")
        send_btn.pack(side=tk.RIGHT)
        
        # 绑定回车键发送消息
        self.message_entry.bind('<Return>', lambda e: self.send_chat_message())
    
    def load_chat_history(self):
        """加载聊天历史"""
        if not self.current_room_id:
            return
        
        try:
            response = self.session.get(f"{self.base_url}/api/chat/{self.current_room_id}/history")
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                
                # 清除现有消息
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.delete(1.0, tk.END)
                
                # 添加消息
                for msg in messages:
                    timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                    user_display = msg['nickname'] or msg['username']
                    color = msg.get('color', '#000000')
                    
                    message_text = f"[{timestamp}] {user_display}: {msg['content']}\n"
                    self.chat_text.insert(tk.END, message_text)
                
                # 设置为只读
                self.chat_text.config(state=tk.DISABLED)
                
                # 滚动到底部
                self.chat_text.see(tk.END)
            else:
                messagebox.showerror("错误", f"加载聊天历史失败: {response.status_code}")
        except Exception as e:
            messagebox.showerror("错误", f"加载聊天历史时发生错误: {str(e)}")
    
    def send_chat_message(self):
        """发送聊天消息"""
        message = self.message_var.get().strip()
        if not message:
            return
        
        if not self.current_room_id:
            messagebox.showerror("错误", "请选择聊天室")
            return
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat/send",
                json={
                    'room_id': self.current_room_id,
                    'message': message
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    # 清空输入框
                    self.message_var.set("")
                    # 重新加载聊天历史以显示新消息
                    self.load_chat_history()
                else:
                    messagebox.showerror("错误", f"发送消息失败: {data.get('message', '未知错误')}")
            else:
                messagebox.showerror("错误", f"发送消息失败: {response.status_code}")
        except Exception as e:
            messagebox.showerror("错误", f"发送消息时发生错误: {str(e)}")
    
    def show_forum_interface(self):
        """显示论坛界面"""
        # 清除内容框架
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 清除导航框架
        for widget in self.nav_frame.winfo_children():
            widget.destroy()
        
        # 创建论坛导航
        ttk.Label(self.nav_frame, text="论坛分区", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 加载论坛分区
        self.load_forum_sections()
    
    def load_forum_sections(self):
        """加载论坛分区"""
        try:
            # 尝试通过API获取论坛分区列表
            response = self.session.get(f"{self.base_url}/api/forum/sections")
            if response.status_code == 200:
                data = response.json()
                sections = data.get('sections', [])
            else:
                # 如果API调用失败，使用默认列表
                sections = [
                    {"id": 1, "name": "公告板", "description": "系统公告和重要信息"},
                    {"id": 2, "name": "技术交流", "description": "技术讨论区"},
                    {"id": 3, "name": "生活分享", "description": "生活话题分享"}
                ]
            
            for section in sections:
                btn = ttk.Button(
                    self.nav_frame,
                    text=section["name"],
                    command=lambda s=section: self.select_forum_section(s["id"], s["name"]),
                    bootstyle="outline"
                )
                btn.pack(fill=X, padx=5, pady=2)
                
        except Exception as e:
            # 如果API调用失败，使用默认列表
            sections = [
                {"id": 1, "name": "公告板", "description": "系统公告和重要信息"},
                {"id": 2, "name": "技术交流", "description": "技术讨论区"},
                {"id": 3, "name": "生活分享", "description": "生活话题分享"}
            ]
            
            for section in sections:
                btn = ttk.Button(
                    self.nav_frame,
                    text=section["name"],
                    command=lambda s=section: self.select_forum_section(s["id"], s["name"]),
                    bootstyle="outline"
                )
                btn.pack(fill=X, padx=5, pady=2)
    
    def select_forum_section(self, section_id, section_name):
        """选择论坛分区"""
        self.current_section_id = section_id
        
        # 清除内容框架
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建论坛分区界面
        self.create_forum_section_interface(section_name)
        
        # 加载分区主题
        self.load_forum_threads()
    
    def create_forum_section_interface(self, section_name):
        """创建论坛分区界面"""
        # 分区标题
        ttk.Label(self.content_frame, text=f"分区: {section_name}", font=('Arial', 14, 'bold')).pack(pady=5)
        
        # 创建主题列表框架
        threads_frame = ttk.LabelFrame(self.content_frame, text="主题列表", padding=10)
        threads_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # 主题列表
        self.threads_listbox = tk.Listbox(threads_frame)
        self.threads_listbox.pack(fill=BOTH, expand=True, pady=5)
        
        # 绑定双击事件
        self.threads_listbox.bind('<Double-1>', lambda e: self.view_forum_thread())
        
        # 发布新主题按钮
        ttk.Button(
            threads_frame, 
            text="发布新主题", 
            command=self.create_new_thread,
            bootstyle="success"
        ).pack(pady=5)
    
    def load_forum_threads(self):
        """加载论坛主题"""
        if not self.current_section_id:
            return
        
        # 用于存储主题信息的列表
        self.thread_info_list = []
        
        try:
            # 尝试通过API获取分区主题列表
            response = self.session.get(f"{self.base_url}/api/forum/section/{self.current_section_id}/threads")
            if response.status_code == 200:
                data = response.json()
                threads = data.get('threads', [])
            else:
                # 如果API调用失败，使用默认列表
                threads = [
                    {"id": 1, "title": "欢迎来到Stellarsis", "author": "admin", "replies": 5},
                    {"id": 2, "title": "使用教程", "author": "moderator", "replies": 12},
                    {"id": 3, "title": "功能建议", "author": "user1", "replies": 3}
                ]
            
            # 清空列表
            self.threads_listbox.delete(0, tk.END)
            
            # 添加主题
            for thread in threads:
                display_text = f"{thread['title']} (作者: {thread['author']}, 回复: {thread['replies']})"
                self.threads_listbox.insert(tk.END, display_text)
                # 保存主题信息
                self.thread_info_list.append(thread)
                
        except Exception as e:
            # 如果API调用失败，使用默认列表
            threads = [
                {"id": 1, "title": "欢迎来到Stellarsis", "author": "admin", "replies": 5},
                {"id": 2, "title": "使用教程", "author": "moderator", "replies": 12},
                {"id": 3, "title": "功能建议", "author": "user1", "replies": 3}
            ]
            
            # 清空列表
            self.threads_listbox.delete(0, tk.END)
            
            # 添加主题
            for thread in threads:
                display_text = f"{thread['title']} (作者: {thread['author']}, 回复: {thread['replies']})"
                self.threads_listbox.insert(tk.END, display_text)
                # 保存主题信息
                self.thread_info_list.append(thread)
    
    def view_forum_thread(self):
        """查看论坛主题"""
        selection = self.threads_listbox.curselection()
        if not selection:
            return
        
        # 这里我们模拟查看主题，实际应用中需要获取主题ID
        thread_index = selection[0]
        thread_id = thread_index + 1  # 模拟ID
        
        self.current_thread_id = thread_id
        
        # 清除内容框架
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建主题查看界面
        self.create_forum_thread_interface()
    
    def create_forum_thread_interface(self):
        """创建论坛主题界面"""
        # 返回按钮
        ttk.Button(
            self.content_frame, 
            text="← 返回分区", 
            command=lambda: self.select_forum_section(self.current_section_id, "当前分区"),
            bootstyle="outline"
        ).pack(anchor=tk.W, pady=5)
        
        # 主题内容显示区域
        thread_frame = ttk.LabelFrame(self.content_frame, text="主题内容", padding=10)
        thread_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # 主题内容显示
        self.thread_content = scrolledtext.ScrolledText(
            thread_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            height=15
        )
        self.thread_content.pack(fill=BOTH, expand=True, pady=5)
        
        # 模拟加载主题内容
        sample_content = f"""这是主题 #{self.current_thread_id} 的内容。
        
这是一个示例帖子，展示了论坛功能。
您可以在这里查看和回复主题。

欢迎参与讨论！"""
        
        self.thread_content.config(state=tk.NORMAL)
        self.thread_content.insert(tk.END, sample_content)
        self.thread_content.config(state=tk.DISABLED)
        
        # 回复区域
        reply_frame = ttk.LabelFrame(self.content_frame, text="发表回复", padding=10)
        reply_frame.pack(fill=X, pady=5)
        
        self.reply_var = tk.StringVar()
        reply_entry = ttk.Entry(reply_frame, textvariable=self.reply_var)
        reply_entry.pack(fill=X, pady=5)
        
        ttk.Button(
            reply_frame, 
            text="发送回复", 
            command=self.send_forum_reply,
            bootstyle="primary"
        ).pack(pady=5)
    
    def send_forum_reply(self):
        """发送论坛回复"""
        reply = self.reply_var.get().strip()
        if not reply:
            messagebox.showerror("错误", "请输入回复内容")
            return
        
        if not self.current_thread_id:
            messagebox.showerror("错误", "请选择主题")
            return
        
        # 模拟发送回复
        messagebox.showinfo("提示", "回复已发送（模拟功能）")
        self.reply_var.set("")
    
    def create_new_thread(self):
        """创建新主题"""
        if not self.current_section_id:
            messagebox.showerror("错误", "请选择论坛分区")
            return
        
        # 创建新主题窗口
        new_thread_window = tk.Toplevel(self.root)
        new_thread_window.title("发布新主题")
        new_thread_window.geometry("500x400")
        new_thread_window.transient(self.root)
        new_thread_window.grab_set()
        
        # 标题输入
        ttk.Label(new_thread_window, text="主题标题:").pack(pady=5)
        title_var = tk.StringVar()
        title_entry = ttk.Entry(new_thread_window, textvariable=title_var)
        title_entry.pack(fill=X, padx=20, pady=5)
        
        # 内容输入
        ttk.Label(new_thread_window, text="主题内容:").pack(pady=5)
        content_text = scrolledtext.ScrolledText(new_thread_window, height=10)
        content_text.pack(fill=BOTH, expand=True, padx=20, pady=5)
        
        # 发布按钮
        def publish_thread():
            title = title_var.get().strip()
            content = content_text.get(1.0, tk.END).strip()
            
            if not title or not content:
                messagebox.showerror("错误", "请输入标题和内容")
                return
            
            # 模拟发布主题
            messagebox.showinfo("提示", "主题已发布（模拟功能）")
            new_thread_window.destroy()
            
            # 刷新主题列表
            self.load_forum_threads()
        
        ttk.Button(
            new_thread_window, 
            text="发布", 
            command=publish_thread,
            bootstyle="success"
        ).pack(pady=10)
    
    def show_profile(self):
        """显示用户资料界面"""
        # 创建用户资料窗口
        profile_window = tk.Toplevel(self.root)
        profile_window.title("用户资料")
        profile_window.geometry("400x300")
        profile_window.transient(self.root)
        profile_window.grab_set()
        
        # 用户名
        ttk.Label(profile_window, text=f"用户名: {self.current_user}", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 密码修改
        ttk.Label(profile_window, text="修改密码", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        
        change_pass_frame = ttk.Frame(profile_window)
        change_pass_frame.pack(fill=X, padx=20, pady=5)
        
        ttk.Label(change_pass_frame, text="当前密码:").grid(row=0, column=0, sticky=W)
        current_pass = ttk.Entry(change_pass_frame, show="*")
        current_pass.grid(row=0, column=1, padx=5, pady=2, sticky=E+W)
        
        ttk.Label(change_pass_frame, text="新密码:").grid(row=1, column=0, sticky=W)
        new_pass = ttk.Entry(change_pass_frame, show="*")
        new_pass.grid(row=1, column=1, padx=5, pady=2, sticky=E+W)
        
        ttk.Label(change_pass_frame, text="确认密码:").grid(row=2, column=0, sticky=W)
        confirm_pass = ttk.Entry(change_pass_frame, show="*")
        confirm_pass.grid(row=2, column=1, padx=5, pady=2, sticky=E+W)
        
        change_pass_frame.columnconfigure(1, weight=1)
        
        def change_password():
            current = current_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()
            
            if not current or not new or not confirm:
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            if new != confirm:
                messagebox.showerror("错误", "新密码与确认密码不匹配")
                return
            
            if len(new) < 6:
                messagebox.showerror("错误", "密码至少需要6个字符")
                return
            
            # 模拟密码修改
            messagebox.showinfo("成功", "密码已修改（模拟功能）")
            current_pass.delete(0, tk.END)
            new_pass.delete(0, tk.END)
            confirm_pass.delete(0, tk.END)
        
        ttk.Button(
            profile_window, 
            text="修改密码", 
            command=change_password,
            bootstyle="primary"
        ).pack(pady=20)
    
    def update_online_count(self):
        """更新在线用户数"""
        try:
            response = self.session.get(f"{self.base_url}/api/online_count")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.online_count_label.config(text=f"在线: {count}")
            else:
                self.online_count_label.config(text="在线: 未知")
        except:
            self.online_count_label.config(text="在线: 未知")
    
    def schedule_online_count_update(self):
        """定时更新在线用户数"""
        def update():
            self.update_online_count()
            # 每30秒更新一次
            self.root.after(30000, update)
        
        # 立即启动定时更新
        self.root.after(0, update)
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于", 
            "Stellarsis 聊天论坛系统客户端\n\n"
            "版本: 1.0.0\n"
            "使用 ttkbootstrap 和 requests 构建\n\n"
            "功能:\n"
            "- 多房间聊天\n"
            "- 论坛系统\n"
            "- 主题切换\n"
            "- 用户管理\n"
            "- 实时消息"
        )
    
    def run(self):
        """运行客户端"""
        self.root.mainloop()


if __name__ == "__main__":
    client = StellarsisClient()
    client.run()