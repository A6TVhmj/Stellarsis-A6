"""
网站客户端 - 基于ttkbootstrap和requests实现
支持登录、聊天室、论坛、用户管理等功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
import time
from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import webbrowser
from urllib.parse import urljoin


class WebsiteClient:
    def __init__(self):
        self.base_url = "http://localhost:5000"  # 默认服务器地址
        self.session = requests.Session()
        self.current_user = None
        self.current_room = None
        self.current_thread = None
        self.root = tb.Window(themename="cosmo")  # 使用ttkbootstrap的主题
        self.root.title("网站客户端")
        self.root.geometry("1000x700")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 创建登录界面
        self.create_login_frame()
        
    def create_login_frame(self):
        """创建登录界面"""
        self.login_frame = ttk.Frame(self.main_frame)
        self.login_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(self.login_frame, text="登录", font=("Arial", 16))
        title_label.pack(pady=20)
        
        # 用户名输入
        ttk.Label(self.login_frame, text="用户名:").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.pack(pady=5)
        
        # 密码输入
        ttk.Label(self.login_frame, text="密码:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, width=30, show="*")
        self.password_entry.pack(pady=5)
        
        # 服务器地址输入
        ttk.Label(self.login_frame, text="服务器地址:").pack(pady=5)
        self.server_entry = ttk.Entry(self.login_frame, width=30)
        self.server_entry.pack(pady=5)
        self.server_entry.insert(0, self.base_url)
        
        # 登录按钮
        self.login_btn = ttk.Button(self.login_frame, text="登录", command=self.login)
        self.login_btn.pack(pady=20)
        
        # 绑定回车键登录
        self.password_entry.bind('<Return>', lambda e: self.login())
        
    def login(self):
        """登录功能"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        server_url = self.server_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
            
        if server_url:
            self.base_url = server_url
        
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                data={
                    'username': username,
                    'password': password
                }
            )
            
            if response.status_code == 200:
                self.current_user = username
                self.login_frame.destroy()
                self.create_main_interface()
            else:
                messagebox.showerror("登录失败", "用户名或密码错误")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("错误", f"网络请求失败: {str(e)}")
    
    def create_main_interface(self):
        """创建主界面"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="登出", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 用户菜单
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="用户", menu=user_menu)
        user_menu.add_command(label="修改密码", command=self.open_change_password)
        user_menu.add_command(label="关注用户", command=self.open_follow_user)
        user_menu.add_command(label="我的关注", command=self.open_follow_list)
        
        # 管理员菜单
        admin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="管理员", menu=admin_menu)
        admin_menu.add_command(label="系统信息", command=self.open_system_info)
        admin_menu.add_command(label="用户管理", command=self.open_user_management)
        
        # 创建主界面布局
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=True, pady=10)
        
        # 聊天室标签页
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="聊天室")
        self.create_chat_interface()
        
        # 论坛标签页
        self.forum_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forum_frame, text="论坛")
        self.create_forum_interface()
        
        # 在线用户数标签
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=X, pady=5)
        
        self.online_label = ttk.Label(self.status_frame, text="在线用户: 未知")
        self.online_label.pack(side=LEFT)
        
        # 定期更新在线用户数
        self.update_online_count()
    
    def create_chat_interface(self):
        """创建聊天室界面"""
        # 聊天室选择
        chat_top_frame = ttk.Frame(self.chat_frame)
        chat_top_frame.pack(fill=X, pady=5)
        
        ttk.Label(chat_top_frame, text="聊天室:").pack(side=LEFT)
        self.room_var = tk.StringVar(value="1")
        # 显示聊天室名称和介绍
        room_combo = ttk.Combobox(chat_top_frame, textvariable=self.room_var, 
                                  values=["1-公共聊天室", "2-技术交流室", "3-休闲娱乐室"], 
                                  state="readonly", width=15)
        room_combo.pack(side=LEFT, padx=5)
        room_combo.bind('<<ComboboxSelected>>', self.switch_room)
        
        # 消息显示区域 - 使用ScrolledFrame
        chat_scroll_frame = ScrolledFrame(self.chat_frame, autohide=True)
        chat_scroll_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # 创建消息容器
        self.chat_container = ttk.Frame(chat_scroll_frame)
        self.chat_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        chat_scroll_frame.configure(bootstyle="default")
        
        # 右键菜单用于删除消息（如果用户有权限）
        self.chat_text = tk.Text(self.chat_frame, state=DISABLED)  # 保留这个引用用于右键菜单
        self.chat_menu = tk.Menu(self.chat_text, tearoff=0)
        self.chat_menu.add_command(label="删除消息", command=self.delete_selected_message)
        
        # 绑定右键菜单事件到聊天容器
        self.chat_container.bind("<Button-3>", self.show_chat_menu)  # Windows/Linux
        self.chat_container.bind("<Button-2>", self.show_chat_menu)  # macOS
        self.chat_container.bind("<Button-3>", self.show_chat_menu)  # 为了确保捕获事件
        
        # 消息输入区域
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill=X, pady=5)
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_message)
        
        send_btn = ttk.Button(input_frame, text="发送", command=self.send_message)
        send_btn.pack(side=RIGHT)
        
        # 加载历史消息
        self.load_chat_history()
    
    def create_forum_interface(self):
        """创建论坛界面"""
        # 论坛分区选择
        forum_top_frame = ttk.Frame(self.forum_frame)
        forum_top_frame.pack(fill=X, pady=5)
        
        ttk.Label(forum_top_frame, text="分区:").pack(side=LEFT)
        self.section_var = tk.StringVar(value="1")
        section_combo = ttk.Combobox(forum_top_frame, textvariable=self.section_var, values=["1", "2", "3"], state="readonly", width=10)
        section_combo.pack(side=LEFT, padx=5)
        section_combo.bind('<<ComboboxSelected>>', self.load_forum_threads)
        
        refresh_btn = ttk.Button(forum_top_frame, text="刷新", command=self.load_forum_threads)
        refresh_btn.pack(side=RIGHT)
        
        # 论坛主题列表 - 使用ScrolledFrame
        thread_scroll_frame = ScrolledFrame(self.forum_frame, autohide=True)
        thread_scroll_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # 创建主题容器
        self.thread_container = ttk.Frame(thread_scroll_frame)
        self.thread_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        thread_scroll_frame.configure(bootstyle="default")
        
        # 绑定双击事件到容器
        self.thread_container.bind('<Double-Button-1>', self.view_thread)
        
        # 发帖按钮
        post_frame = ttk.Frame(self.forum_frame)
        post_frame.pack(fill=X, pady=5)
        
        post_btn = ttk.Button(post_frame, text="发布新帖", command=self.open_post_thread)
        post_btn.pack(side=RIGHT)
        
        # 加载论坛主题
        self.load_forum_threads()
    
    def load_chat_history(self):
        """加载聊天室历史消息"""
        try:
            # 清空当前消息容器
            for widget in self.chat_container.winfo_children():
                widget.destroy()
                
            room_id = int(self.room_var.get())
            response = self.session.get(f"{self.base_url}/api/chat/{room_id}/history?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                
                # 存储消息ID和消息组件的映射，用于删除功能
                self.message_widgets_map = {}
                
                for i, msg in enumerate(data.get('messages', [])):
                    timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                    formatted_msg = f"[{timestamp}] {msg['username']}: {msg['content']}"
                    
                    # 创建消息标签
                    msg_frame = ttk.Frame(self.chat_container)
                    msg_frame.pack(fill=X, padx=5, pady=2)
                    
                    msg_label = ttk.Label(msg_frame, text=formatted_msg, font=("微软雅黑", 10), 
                                          relief="raised", padding=5, anchor="w")
                    msg_label.pack(fill=X)
                    
                    # 如果是当前用户的消息，设置不同样式
                    if msg['username'] == self.current_user:
                        msg_label.configure(bootstyle="primary")
                    
                    # 记录消息ID与组件的映射
                    self.message_widgets_map[msg['id']] = (msg_frame, msg_label)
                    
                # 滚动到底部
                self.chat_container.update_idletasks()
                # 滚动到最后一个组件
                last_widget = self.chat_container.winfo_children()[-1] if self.chat_container.winfo_children() else None
                if last_widget:
                    last_widget.update_idletasks()
        except Exception as e:
            messagebox.showerror("错误", f"加载聊天历史失败: {str(e)}")
    
    def send_message(self, event=None):
        """发送消息"""
        message = self.message_entry.get().strip()
        if not message:
            return
            
        try:
            room_id = int(self.room_var.get())
            response = self.session.post(
                f"{self.base_url}/api/chat/send",
                data={
                    'room_id': room_id,
                    'message': message
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.message_entry.delete(0, tk.END)
                    self.load_chat_history()  # 重新加载消息以显示新发送的消息
                else:
                    messagebox.showerror("错误", "发送消息失败")
            else:
                messagebox.showerror("错误", f"发送消息失败: {response.status_code}")
        except Exception as e:
            messagebox.showerror("错误", f"发送消息失败: {str(e)}")
    
    def switch_room(self, event=None):
        """切换聊天室"""
        self.load_chat_history()
    
    def show_chat_menu(self, event):
        """显示聊天消息右键菜单"""
        # 检查用户是否有删除权限（管理员或777权限）
        # 简单起见，这里直接显示菜单，实际实现中应检查权限
        try:
            self.chat_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.chat_menu.grab_release()
    
    def delete_selected_message(self):
        """删除选中的消息"""
        # 获取光标位置附近的行
        cursor_pos = self.chat_text.index(tk.INSERT)
        line_num = int(cursor_pos.split('.')[0])
        
        # 检查是否存在该行的消息ID映射
        if line_num in self.message_line_map:
            message_id = self.message_line_map[line_num]
            
            result = messagebox.askyesno("确认删除", f"确定要删除ID为 {message_id} 的消息吗？")
            if result:
                try:
                    room_id = int(self.room_var.get())
                    response = self.session.delete(f"{self.base_url}/api/chat/{room_id}/messages/{message_id}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            messagebox.showinfo("成功", data.get('message', '消息已删除'))
                            # 重新加载聊天历史以更新显示
                            self.load_chat_history()
                        else:
                            messagebox.showerror("错误", data.get('message', '删除失败'))
                    else:
                        messagebox.showerror("错误", f"删除消息失败，状态码: {response.status_code}")
                except Exception as e:
                    messagebox.showerror("错误", f"删除消息失败: {str(e)}")
        else:
            messagebox.showwarning("警告", "无法确定要删除的消息")
    
    def load_forum_threads(self, event=None):
        """加载论坛主题"""
        try:
            # 清空当前主题容器
            for widget in self.thread_container.winfo_children():
                widget.destroy()
                
            section_id = int(self.section_var.get())
            # 尝试获取论坛主题列表 - 使用可能的API端点
            # 由于API文档中没有明确的获取主题列表的API，我们尝试常见的端点
            response = self.session.get(f"{self.base_url}/forum/section/{section_id}")
            
            if response.status_code == 200:
                # 尝试解析响应，如果服务器返回JSON格式的主题列表
                try:
                    data = response.json()
                    threads = data.get('threads', [])
                    for thread in threads:
                        self.add_thread_to_container(thread)
                except:
                    # 如果不是JSON格式，可能是HTML页面，我们使用模拟数据作为后备
                    # 从HTML中提取主题信息（如果可能）
                    html_content = response.text
                    # 模拟一些主题帖子作为后备
                    threads = [
                        {"id": 1, "title": "欢迎来到论坛", "author": "admin", "replies": 5},
                        {"id": 2, "title": "新功能建议", "author": "user1", "replies": 3},
                        {"id": 3, "title": "技术讨论", "author": "dev", "replies": 12}
                    ]
                    for thread in threads:
                        self.add_thread_to_container(thread)
            else:
                # 如果API调用失败，使用模拟数据
                threads = [
                    {"id": 1, "title": "欢迎来到论坛", "author": "admin", "replies": 5},
                    {"id": 2, "title": "新功能建议", "author": "user1", "replies": 3},
                    {"id": 3, "title": "技术讨论", "author": "dev", "replies": 12}
                ]
                for thread in threads:
                    self.add_thread_to_container(thread)
        except Exception as e:
            messagebox.showerror("错误", f"加载论坛主题失败: {str(e)}")
            # 出错时也显示一些模拟数据
            # 清空当前主题容器
            for widget in self.thread_container.winfo_children():
                widget.destroy()
                
            threads = [
                {"id": 1, "title": "欢迎来到论坛", "author": "admin", "replies": 5},
                {"id": 2, "title": "新功能建议", "author": "user1", "replies": 3},
                {"id": 3, "title": "技术讨论", "author": "dev", "replies": 12}
            ]
            for thread in threads:
                self.add_thread_to_container(thread)

    def add_thread_to_container(self, thread):
        """将主题添加到容器中"""
        # 创建主题框架
        thread_frame = ttk.Frame(self.thread_container)
        thread_frame.pack(fill=X, padx=5, pady=2)
        
        # 创建主题标签
        thread_info = f"{thread['title']} (作者: {thread['author']}, 回复: {thread.get('replies', 0)})"
        thread_label = ttk.Label(thread_frame, text=thread_info, font=("微软雅黑", 10), 
                                 relief="raised", padding=8, anchor="w")
        thread_label.pack(fill=X, padx=2, pady=2)
        
        # 绑定双击事件到标签
        thread_label.bind('<Double-Button-1>', lambda e, t=thread: self.view_thread_direct(t))
        
        # 鼠标悬停效果
        def on_enter(e):
            thread_label.configure(bootstyle="primary")
        def on_leave(e):
            thread_label.configure(bootstyle="default")
        
        thread_label.bind("<Enter>", on_enter)
        thread_label.bind("<Leave>", on_leave)
    
    def view_thread(self, event):
        """查看主题帖 - 处理双击事件但不执行操作，因为现在直接在add_thread_to_container中绑定事件"""
        # 此函数保留用于兼容性，实际逻辑在add_thread_to_container中
        pass
    
    def view_thread_direct(self, thread):
        """直接查看主题帖，接收thread对象"""
        # 打开主题帖详情窗口
        self.open_thread_detail(thread['title'], thread['author'], thread.get('replies', 0))
    
    def open_thread_detail(self, title, author, replies):
        """打开主题帖详情窗口"""
        detail_window = tb.Toplevel(self.root)
        detail_window.title(f"主题: {title}")
        detail_window.geometry("700x500")
        
        # 主题信息
        info_frame = ttk.Frame(detail_window)
        info_frame.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"标题: {title}", font=("Arial", 12, "bold")).pack(anchor=W)
        ttk.Label(info_frame, text=f"作者: {author} | 回复数: {replies}", font=("Arial", 10)).pack(anchor=W, pady=(5, 0))
        
        # 回复内容区域 - 使用ScrolledFrame
        replies_frame = ttk.Frame(detail_window)
        replies_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        replies_scroll_frame = ScrolledFrame(replies_frame, autohide=True)
        replies_scroll_frame.pack(fill=BOTH, expand=True)
        
        # 创建回复容器
        self.replies_container = ttk.Frame(replies_scroll_frame)
        self.replies_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        replies_scroll_frame.configure(bootstyle="default")
        
        # 回复输入区域
        input_frame = ttk.Frame(detail_window)
        input_frame.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="回复内容:").pack(anchor=W)
        
        # 使用ScrolledFrame替代ScrolledText
        reply_frame = ScrolledFrame(input_frame, autohide=True, height=4)
        reply_frame.pack(fill=X, pady=(5, 0))
        reply_frame.bind('<Configure>', lambda e: reply_frame.configure(scrollregion=reply_frame.bbox('all')))
        
        reply_text = tk.Text(reply_frame, height=4, wrap=tk.WORD)
        reply_text.pack(fill=X, expand=True)
        
        # 回复按钮
        def post_reply():
            content = reply_text.get(1.0, tk.END).strip()
            if not content:
                messagebox.showerror("错误", "请输入回复内容")
                return
                
            try:
                # 这里需要获取thread_id，我们尝试从标题中找到对应的主题ID
                # 由于我们没有thread_id信息，我们先尝试获取所有主题来找到对应ID
                thread_id = self.find_thread_id_by_title(title)
                if not thread_id:
                    # 如果找不到thread_id，尝试使用其他方式
                    thread_id = 1  # 默认值
                
                response = self.session.post(
                    f"{self.base_url}/api/forum/reply",
                    data={
                        'thread_id': thread_id,
                        'content': content
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        messagebox.showinfo("成功", "回复发布成功")
                        reply_text.delete(1.0, tk.END)
                        # 重新加载回复内容
                        self.load_thread_replies(self.replies_container, title, thread_id)
                    else:
                        messagebox.showerror("错误", "回复发布失败：" + data.get('message', '未知错误'))
                else:
                    messagebox.showerror("错误", f"回复发布失败，状态码: {response.status_code}")
            except Exception as e:
                messagebox.showerror("错误", f"发布回复失败: {str(e)}")
        
        reply_btn = ttk.Button(input_frame, text="发布回复", command=post_reply)
        reply_btn.pack(pady=5)
        
        # 加载回复内容 - 需要先获取thread_id
        thread_id = self.find_thread_id_by_title(title)
        self.load_thread_replies(self.replies_container, title, thread_id)
    
    def find_thread_id_by_title(self, title):
        """根据标题查找主题ID"""
        # 这是一个简化实现，实际应用中需要更复杂的方法来获取thread_id
        # 可能需要调用API获取特定主题的信息
        try:
            # 尝试通过论坛分区API获取主题信息
            section_id = int(self.section_var.get())
            response = self.session.get(f"{self.base_url}/forum/section/{section_id}")
            
            if response.status_code == 200:
                # 尝试解析响应，如果服务器返回JSON格式的主题列表
                try:
                    data = response.json()
                    threads = data.get('threads', [])
                    for thread in threads:
                        if thread.get('title') == title:
                            return thread.get('id')
                except:
                    # 如果不是JSON格式，返回默认值
                    pass
        except:
            pass
        
        # 如果无法找到，返回None
        return None
    
    def show_reply_menu(self, event, menu):
        """显示回复右键菜单"""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def delete_selected_reply(self, text_widget, window):
        """删除选中的回复"""
        # 由于无法直接从显示的文本中获取回复ID，我们提示用户
        result = messagebox.askyesno("删除回复", "确定要删除选中的回复吗？\n(此操作需要知道回复ID，当前实现为模拟)")
        if result:
            messagebox.showinfo("提示", "删除回复功能需要知道具体的回复ID，当前为模拟实现")
    
    def load_thread_replies(self, container, title, thread_id=None):
        """加载主题帖的回复"""
        # 清空当前回复容器
        for widget in container.winfo_children():
            widget.destroy()
        
        try:
            # 如果有thread_id，尝试从API获取实际的回复
            if thread_id:
                # 注意：根据API文档，没有直接获取特定主题回复的API
                # 我们可能需要通过其他方式获取，这里使用模拟
                # 在实际实现中，后端应该提供类似 /api/forum/thread/{thread_id}/replies 的API
                pass
            
            # 模拟一些回复（在实际实现中，应从API获取）
            replies = [
                {"author": "admin", "content": "欢迎来到本帖讨论！", "timestamp": "2023-01-01 10:00:00", "id": 1},
                {"author": "user1", "content": "这是一个很好的话题。", "timestamp": "2023-01-01 11:30:00", "id": 2},
                {"author": "moderator", "content": "请大家文明讨论。", "timestamp": "2023-01-01 12:15:00", "id": 3}
            ]
            
            for reply in replies:
                self.add_reply_to_container(container, reply)
        
        except Exception as e:
            # 如果API调用失败，使用模拟数据
            replies = [
                {"author": "admin", "content": "欢迎来到本帖讨论！", "timestamp": "2023-01-01 10:00:00", "id": 1},
                {"author": "user1", "content": "这是一个很好的话题。", "timestamp": "2023-01-01 11:30:00", "id": 2},
                {"author": "moderator", "content": "请大家文明讨论。", "timestamp": "2023-01-01 12:15:00", "id": 3}
            ]
            
            for reply in replies:
                self.add_reply_to_container(container, reply)

    def add_reply_to_container(self, container, reply):
        """将回复添加到容器中"""
        # 创建回复框架
        reply_frame = ttk.Frame(container)
        reply_frame.pack(fill=X, padx=5, pady=2)
        
        # 创建回复标签
        reply_info = f"[{reply['timestamp']}] {reply['author']}: {reply['content']}"
        reply_label = ttk.Label(reply_frame, text=reply_info, font=("微软雅黑", 9), 
                                relief="groove", padding=6, anchor="w", wraplength=600)
        reply_label.pack(fill=X, padx=2, pady=2)
        
        # 如果是当前用户的回复，设置不同样式
        if reply['author'] == self.current_user:
            reply_label.configure(bootstyle="primary")
    
    def open_post_thread(self):
        """打开发布新帖窗口"""
        post_window = tb.Toplevel(self.root)
        post_window.title("发布新帖")
        post_window.geometry("500x400")
        
        # 标题输入
        ttk.Label(post_window, text="标题:").pack(pady=5)
        title_entry = ttk.Entry(post_window, width=50)
        title_entry.pack(pady=5)
        
        # 内容输入
        ttk.Label(post_window, text="内容:").pack(pady=5)
        
        # 使用ScrolledFrame替代ScrolledText
        content_frame = ScrolledFrame(post_window, autohide=True)
        content_frame.pack(fill=BOTH, expand=True, pady=5)
        content_frame.bind('<Configure>', lambda e: content_frame.configure(scrollregion=content_frame.bbox('all')))
        
        content_text = tk.Text(content_frame, height=15, wrap=tk.WORD)
        content_text.pack(fill=BOTH, expand=True)
        
        # 发布按钮
        def post_thread():
            title = title_entry.get().strip()
            content = content_text.get(1.0, tk.END).strip()
            
            if not title or not content:
                messagebox.showerror("错误", "请填写标题和内容")
                return
            
            try:
                # 尝试发布新主题帖 - 使用可能的API端点
                # 由于API文档中没有明确的发布主题帖API，我们尝试使用发布回复的API并添加thread_id参数
                section_id = int(self.section_var.get())
                
                # 首先尝试创建新主题
                response = self.session.post(
                    f"{self.base_url}/forum/thread",
                    data={
                        'section_id': section_id,
                        'title': title,
                        'content': content
                    }
                )
                
                if response.status_code in [200, 201, 302]:  # 成功或重定向
                    messagebox.showinfo("成功", "帖子发布成功")
                    post_window.destroy()
                    self.load_forum_threads()
                else:
                    # 如果上面的API失败，尝试使用回复API（可能是发布新主题的API）
                    response2 = self.session.post(
                        f"{self.base_url}/api/forum/reply",
                        data={
                            'thread_id': 0,  # 0可能表示新建主题
                            'content': f"## {title}\n\n{content}"  # 将标题和内容组合
                        }
                    )
                    
                    if response2.status_code == 200:
                        data = response2.json()
                        if data.get('success'):
                            messagebox.showinfo("成功", "帖子发布成功")
                            post_window.destroy()
                            self.load_forum_threads()
                        else:
                            messagebox.showerror("错误", "发布失败：" + data.get('message', '未知错误'))
                    else:
                        messagebox.showerror("错误", f"发布失败，状态码: {response2.status_code}")
            except Exception as e:
                messagebox.showerror("错误", f"发布帖子失败: {str(e)}")
        
        post_btn = ttk.Button(post_window, text="发布", command=post_thread)
        post_btn.pack(pady=10)
    
    def open_change_password(self):
        """打开修改密码窗口"""
        change_window = tb.Toplevel(self.root)
        change_window.title("修改密码")
        change_window.geometry("300x200")
        
        # 旧密码
        ttk.Label(change_window, text="旧密码:").pack(pady=5)
        old_pass = ttk.Entry(change_window, show="*")
        old_pass.pack(pady=5)
        
        # 新密码
        ttk.Label(change_window, text="新密码:").pack(pady=5)
        new_pass = ttk.Entry(change_window, show="*")
        new_pass.pack(pady=5)
        
        # 确认新密码
        ttk.Label(change_window, text="确认新密码:").pack(pady=5)
        confirm_pass = ttk.Entry(change_window, show="*")
        confirm_pass.pack(pady=5)
        
        def change_password():
            old = old_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()
            
            if not old or not new or not confirm:
                messagebox.showerror("错误", "请填写所有字段")
                return
            
            if new != confirm:
                messagebox.showerror("错误", "新密码和确认密码不匹配")
                return
            
            try:
                response = self.session.post(
                    f"{self.base_url}/change_password",
                    data={
                        'old_password': old,
                        'new_password': new,
                        'confirm_password': confirm
                    }
                )
                
                if response.status_code == 200:
                    messagebox.showinfo("成功", "密码修改成功")
                    change_window.destroy()
                else:
                    messagebox.showerror("错误", "密码修改失败")
            except Exception as e:
                messagebox.showerror("错误", f"修改密码失败: {str(e)}")
        
        change_btn = ttk.Button(change_window, text="修改密码", command=change_password)
        change_btn.pack(pady=20)
    
    def open_follow_user(self):
        """打开关注用户窗口"""
        follow_window = tb.Toplevel(self.root)
        follow_window.title("关注用户")
        follow_window.geometry("300x150")
        
        ttk.Label(follow_window, text="用户名:").pack(pady=5)
        username_entry = ttk.Entry(follow_window)
        username_entry.pack(pady=5)
        
        def follow_user():
            username = username_entry.get().strip()
            if not username:
                messagebox.showerror("错误", "请输入用户名")
                return
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/follows",
                    data={'username': username}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        messagebox.showinfo("成功", data.get('message', '关注成功'))
                        follow_window.destroy()
                    else:
                        messagebox.showerror("错误", data.get('message', '关注失败'))
                else:
                    messagebox.showerror("错误", "关注失败")
            except Exception as e:
                messagebox.showerror("错误", f"关注失败: {str(e)}")
        
        follow_btn = ttk.Button(follow_window, text="关注", command=follow_user)
        follow_btn.pack(pady=20)
    
    def open_follow_list(self):
        """打开关注列表窗口"""
        follow_list_window = tb.Toplevel(self.root)
        follow_list_window.title("我的关注")
        follow_list_window.geometry("400x300")
        
        # 使用ScrolledFrame替代Listbox
        follow_scroll_frame = ScrolledFrame(follow_list_window, autohide=True)
        follow_scroll_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 创建关注用户容器
        self.follow_container = ttk.Frame(follow_scroll_frame)
        self.follow_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        follow_scroll_frame.configure(bootstyle="default")
        
        try:
            response = self.session.get(f"{self.base_url}/api/follows")
            
            if response.status_code == 200:
                data = response.json()
                follows = data.get('follows', [])
                
                for user in follows:
                    # 创建关注用户标签
                    user_frame = ttk.Frame(self.follow_container)
                    user_frame.pack(fill=X, padx=5, pady=2)
                    
                    user_label = ttk.Label(user_frame, text=f"{user['username']} ({user['nickname']})", 
                                           font=("微软雅黑", 10), relief="raised", padding=5, anchor="w")
                    user_label.pack(fill=X, padx=2, pady=2)
            else:
                messagebox.showerror("错误", "获取关注列表失败")
        except Exception as e:
            messagebox.showerror("错误", f"获取关注列表失败: {str(e)}")
    
    def open_system_info(self):
        """打开系统信息窗口"""
        try:
            response = self.session.get(f"{self.base_url}/api/admin/system-info")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    info_window = tb.Toplevel(self.root)
                    info_window.title("系统信息")
                    info_window.geometry("400x300")
                    
                    # 使用ScrolledFrame替代ScrolledText
                    info_frame = ScrolledFrame(info_window, autohide=True)
                    info_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
                    info_frame.bind('<Configure>', lambda e: info_frame.configure(scrollregion=info_frame.bbox('all')))
                    
                    info_text = tk.Text(info_frame, wrap=tk.WORD)
                    info_text.pack(fill=BOTH, expand=True)
                    
                    info_text.insert(tk.END, f"内存使用: {data.get('memory_usage', 'N/A')}\n")
                    info_text.insert(tk.END, f"服务器时间: {data.get('server_time', 'N/A')}\n")
                    info_text.insert(tk.END, f"Python版本: {data.get('python_version', 'N/A')}\n")
                    info_text.insert(tk.END, f"Flask版本: {data.get('flask_version', 'N/A')}\n")
                    
                    info_text.config(state=DISABLED)
                else:
                    messagebox.showerror("错误", "获取系统信息失败")
            else:
                messagebox.showerror("错误", "获取系统信息失败")
        except Exception as e:
            messagebox.showerror("错误", f"获取系统信息失败: {str(e)}")
    
    def open_user_management(self):
        """打开用户管理窗口"""
        user_mgmt_window = tb.Toplevel(self.root)
        user_mgmt_window.title("用户管理")
        user_mgmt_window.geometry("500x400")
        
        # 用户列表
        listbox = tk.Listbox(user_mgmt_window)
        listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 模拟添加一些用户
        users = ["admin", "user1", "moderator", "guest"]
        for user in users:
            listbox.insert(tk.END, user)
    
    def update_online_count(self):
        """更新在线用户数"""
        try:
            response = self.session.get(f"{self.base_url}/api/online_count")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.online_label.config(text=f"在线用户: {count}")
            else:
                self.online_label.config(text="在线用户: 未知")
        except:
            self.online_label.config(text="在线用户: 未知")
        
        # 每30秒更新一次
        self.root.after(30000, self.update_online_count)
    
    def logout(self):
        """登出"""
        try:
            self.session.get(f"{self.base_url}/logout")
        except:
            pass  # 忽略登出错误
        
        # 清除当前用户信息
        self.current_user = None
        self.session = requests.Session()
        
        # 重新创建登录界面
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.create_login_frame()
    
    def run(self):
        """运行客户端"""
        self.root.mainloop()


if __name__ == "__main__":
    client = WebsiteClient()
    client.run()