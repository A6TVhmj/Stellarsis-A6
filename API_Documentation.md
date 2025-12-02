# 网站API文档

这是一个基于Flask的社交平台，包含聊天室、论坛、用户管理等功能。以下是API端点的详细文档。

## 目录

1. [认证API](#认证api)
2. [聊天室API](#聊天室api)
3. [论坛API](#论坛api)
4. [用户API](#用户api)
5. [Socket.IO事件](#socketio事件)
6. [管理员API](#管理员api)
7. [通用API](#通用api)

## 认证API

### 登录
- **URL**: `/login`
- **方法**: `POST`
- **描述**: 用户登录
- **参数**:
  - `username`: 用户名
  - `password`: 密码
- **返回**: 重定向到首页或登录页面

### 登出
- **URL**: `/logout`
- **方法**: `GET`
- **描述**: 用户登出
- **返回**: 重定向到登录页面

### 修改密码
- **URL**: `/change_password`
- **方法**: `POST`
- **描述**: 修改用户密码
- **参数**:
  - `old_password`: 旧密码
  - `new_password`: 新密码
  - `confirm_password`: 确认新密码

## 聊天室API

### 获取聊天室历史消息
- **URL**: `/api/chat/<int:room_id>/history`
- **方法**: `GET`
- **认证**: 需要登录
- **描述**: 获取指定聊天室的历史消息
- **参数**:
  - `limit`: 消息数量限制（默认50，最大100）
  - `offset`: 偏移量（默认0）
- **返回**:
```json
{
  "messages": [
    {
      "id": 1,
      "content": "消息内容",
      "timestamp": "2023-01-01T00:00:00",
      "user_id": 1,
      "username": "用户名",
      "nickname": "昵称",
      "color": "#000000",
      "badge": "徽章"
    }
  ]
}
```

### 发送聊天消息
- **URL**: `/api/chat/send`
- **方法**: `POST`
- **认证**: 需要登录
- **描述**: 发送聊天消息
- **参数**:
  - `room_id`: 聊天室ID
  - `message`: 消息内容
- **返回**:
```json
{
  "success": true
}
```

### 删除聊天消息
- **URL**: `/api/chat/<int:room_id>/messages/<int:message_id>`
- **方法**: `DELETE`
- **认证**: 需要登录
- **描述**: 删除指定聊天室中的消息
- **权限**:
  - 管理员或su权限：可删除任意消息
  - 777权限：可删除自己的消息
- **返回**:
```json
{
  "success": true,
  "message": "消息已删除"
}
```

## 论坛API

### 发布回复
- **URL**: `/api/forum/reply`
- **方法**: `POST`
- **认证**: 需要登录
- **描述**: 在帖子下发布回复
- **参数**:
  - `thread_id`: 帖子ID
  - `content`: 回复内容
- **返回**:
```json
{
  "success": true,
  "reply_id": 1,
  "user_id": 1,
  "username": "用户名",
  "nickname": "昵称",
  "color": "#000000",
  "badge": "徽章",
  "timestamp": "2023-01-01T00:00:00",
  "content": "回复内容"
}
```

### 删除回复
- **URL**: `/api/forum/reply/<int:reply_id>`
- **方法**: `DELETE`
- **认证**: 需要登录
- **描述**: 删除论坛回复
- **权限**:
  - 管理员或su权限：可删除任意回复
  - 777权限：可删除自己的回复
- **返回**:
```json
{
  "success": true,
  "message": "回复已删除"
}
```

### 删除主题帖
- **URL**: `/api/forum/thread/<int:thread_id>`
- **方法**: `DELETE`
- **认证**: 需要登录
- **描述**: 删除论坛主题帖
- **权限**:
  - 管理员或su权限：可删除任意主题
  - 777权限：可删除自己的主题
- **返回**:
```json
{
  "success": true,
  "message": "删除成功",
  "redirect": "/forum/section/1"
}
```

## 用户API

### 获取关注列表
- **URL**: `/api/follows`
- **方法**: `GET`
- **认证**: 需要登录
- **描述**: 获取当前用户的关注列表
- **返回**:
```json
{
  "success": true,
  "follows": [
    {
      "id": 1,
      "username": "用户名",
      "nickname": "昵称",
      "followed_at": "2023-01-01T00:00:00"
    }
  ]
}
```

### 添加关注
- **URL**: `/api/follows`
- **方法**: `POST`
- **认证**: 需要登录
- **描述**: 关注其他用户
- **参数**:
  - `username`: 要关注的用户名（或使用user_id）
  - `user_id`: 要关注的用户ID（或使用username）
- **返回**:
```json
{
  "success": true,
  "message": "关注成功",
  "user": {
    "id": 1,
    "username": "用户名",
    "nickname": "昵称"
  }
}
```

### 取消关注
- **URL**: `/api/follows/<int:followed_id>`
- **方法**: `DELETE`
- **认证**: 需要登录
- **描述**: 取消关注指定用户
- **返回**:
```json
{
  "success": true,
  "message": "已取消关注"
}
```

### 搜索用户
- **URL**: `/api/search_user`
- **方法**: `GET`
- **认证**: 需要登录
- **描述**: 根据用户名或昵称搜索用户
- **参数**:
  - `username`: 要搜索的用户名或昵称
- **返回**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "用户名",
    "nickname": "昵称"
  }
}
```

### 模糊搜索用户
- **URL**: `/api/search_users`
- **方法**: `GET`
- **认证**: 需要登录
- **描述**: 模糊搜索用户（用户名或昵称包含查询字符串）
- **参数**:
  - `username`: 搜索关键词
- **返回**:
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "username": "用户名",
      "nickname": "昵称"
    }
  ]
}
```

## Socket.IO事件

### 连接事件
- **事件名**: `connect`
- **描述**: 客户端连接到服务器
- **认证**: 需要登录
- **触发**: 客户端连接时自动触发

### 加入聊天室
- **事件名**: `join`
- **描述**: 加入指定聊天室
- **参数**:
  - `room`: 聊天室ID
- **认证**: 需要登录

### 离开聊天室
- **事件名**: `leave`
- **描述**: 离开指定聊天室
- **参数**:
  - `room`: 聊天室ID
- **认证**: 需要登录

### 发送消息
- **事件名**: `send_message`
- **描述**: 发送聊天消息到指定聊天室
- **参数**:
  - `room_id`: 聊天室ID
  - `message`: 消息内容
  - `client_id`: 客户端消息ID（可选）
- **认证**: 需要登录
- **返回**: 通过`message`事件广播给房间内所有用户

### 获取在线用户数
- **事件名**: `get_online_users`
- **描述**: 获取在线用户数（未在代码中找到实现）

### 获取全局在线数
- **事件名**: `get_global_online_count`
- **描述**: 获取全局在线用户数（未在代码中找到实现）

## 管理员API

### 获取系统信息
- **URL**: `/api/admin/system-info`
- **方法**: `GET`
- **认证**: 需要管理员权限
- **描述**: 获取服务器系统信息
- **返回**:
```json
{
  "success": true,
  "memory_usage": "100.50 MB",
  "server_time": "2023-01-01T00:00:00",
  "python_version": "3.x.x",
  "flask_version": "2.3.2"
}
```

### 清除缓存
- **URL**: `/api/admin/clear-cache`
- **方法**: `POST`
- **认证**: 需要管理员权限
- **描述**: 清除系统缓存
- **返回**:
```json
{
  "success": true,
  "message": "缓存清除成功"
}
```

### 重启服务器
- **URL**: `/api/admin/restart`
- **方法**: `POST`
- **认证**: 需要管理员权限
- **描述**: 重启服务器
- **返回**:
```json
{
  "success": true,
  "message": "服务器正在重启"
}
```

### 更新用户信息
- **URL**: `/api/admin/users/<int:user_id>`
- **方法**: `PUT`
- **认证**: 需要管理员权限
- **描述**: 更新指定用户的信息
- **参数**:
  - `username`: 新用户名（可选）
  - `nickname`: 新昵称（可选）
  - `color`: 新颜色（可选）
  - `badge`: 新徽章（可选）
- **返回**:
```json
{
  "success": true,
  "message": "用户信息更新成功"
}
```

### 删除用户
- **URL**: `/api/admin/users/<int:user_id>`
- **方法**: `DELETE`
- **认证**: 需要管理员权限
- **描述**: 删除指定用户及其相关数据
- **返回**:
```json
{
  "success": true,
  "message": "用户删除成功"
}
```

### 更新用户角色
- **URL**: `/api/admin/users/<int:user_id>/role`
- **方法**: `PUT`
- **认证**: 需要管理员权限
- **描述**: 更新指定用户的角色
- **参数**:
  - `role`: 新角色（"user"或"admin"）
- **返回**:
```json
{
  "success": true,
  "message": "用户角色已更新"
}
```

### 获取用户权限
- **URL**: `/api/admin/users/<int:user_id>/permissions`
- **方法**: `GET`
- **认证**: 需要管理员权限
- **描述**: 获取指定用户的权限信息

### 更新用户权限
- **URL**: `/api/admin/users/<int:user_id>/permissions`
- **方法**: `PUT`
- **认证**: 需要管理员权限
- **描述**: 更新指定用户的权限

### 创建用户
- **URL**: `/api/admin/users`
- **方法**: `POST`
- **认证**: 需要管理员权限
- **描述**: 创建新用户

## 通用API

### 获取在线用户数
- **URL**: `/api/online_count`
- **方法**: `GET`
- **认证**: 需要登录
- **描述**: 获取全局在线用户数（5分钟内活动的用户）
- **返回**:
```json
{
  "count": 10
}
```

### 获取未读消息数
- **URL**: `/api/last_views/unread_counts`
- **方法**: `GET`
- **认证**: 需要登录
- **描述**: 获取用户在可访问聊天室和论坛分区的未读消息数
- **返回**:
```json
{
  "success": true,
  "chat": {
    "1": 5,
    "2": 0
  },
  "forum": {
    "1": 3,
    "3": 7
  }
}
```

## 权限说明

该系统使用分级权限系统：

- `su`: 超级用户权限，可执行所有操作
- `777`: 高级权限，可执行大部分操作，但不能管理其他用户
- `444`: 查看权限，只能查看内容
- `Null`: 无权限，无法访问

## 错误处理

大多数API端点在遇到错误时会返回以下格式的响应：

```json
{
  "success": false,
  "message": "错误信息"
}
```

## 注意事项

1. 所有API端点都需要用户登录（除了登录相关端点）
2. 管理员API需要管理员权限
3. 部分操作需要特定权限级别
4. 消息内容经过XSS防护处理
5. 数据库操作失败时会回滚事务