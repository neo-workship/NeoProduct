import sqlite3
import hashlib
import datetime
import secrets
from typing import Optional, Dict, Any
import streamlit.components.v1 as components

class DatabaseManager:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # 创建会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建LLM配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                model_url TEXT NOT NULL,
                api_key TEXT NOT NULL, -- 考虑到实际应用，这里API Key应加密存储
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (user_id, model_name) -- 同一个用户不能有同名模型
            )
        ''')
        
        # 创建默认管理员账户
        admin_password = self.hash_password("admin123")
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ("admin", "admin@example.com", admin_password, "admin"))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, role: str = "user") -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # 用户名或邮箱已存在
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, email, role, is_active
            FROM users
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # 更新最后登录时间
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user[0],))
            conn.commit()
            
            user_dict = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3],
                'is_active': bool(user[4]) # 确保is_active是布尔值
            }
        else:
            user_dict = None
        
        conn.close()
        return user_dict
    
    def create_session(self, user_id: int, remember_me: bool = False) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        session_token = secrets.token_hex(32) # 生成唯一的会话令牌
        # 设置过期时间（记住我：30天，否则：24小时）
        if remember_me:
            expires_at = datetime.datetime.now() + datetime.timedelta(days=30) # 更长的时间，例如30天
        else:
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=24)
        
        cursor.execute('''
            INSERT INTO user_sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, session_token, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.role, u.is_active, s.expires_at
            FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.session_token = ? AND u.is_active = 1
        ''', (session_token,))
        
        result = cursor.fetchone()
        
        if result:
            user_id, username, email, role, is_active, expires_at_str = result
            
            # 检查会话是否过期
            expires_datetime = datetime.datetime.fromisoformat(expires_at_str)
            if expires_datetime > datetime.datetime.now():
                user_dict = {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'role': role,
                    'is_active': bool(is_active)
                }
                conn.close()
                return user_dict
            else:
                # 会话过期，删除此会话
                cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
                conn.commit()
        
        conn.close()
        return None
    
    def delete_session(self, session_token: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))    
        conn.commit()
        conn.close()
    
    def cleanup_expired_sessions(self):
        """清理数据库中所有过期的会话。"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP')
        conn.commit()
        conn.close()
    
    def update_password(self, username: str, old_password: str, new_password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        old_password_hash = self.hash_password(old_password)
        cursor.execute('''
            SELECT id FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, old_password_hash))
        
        if cursor.fetchone():
            new_password_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ?
                WHERE username = ?
            ''', (new_password_hash, username))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def get_all_users(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        return users
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET role = ?
                WHERE id = ?
            ''', (new_role, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False
    
    def toggle_user_status(self, user_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET is_active = 1 - is_active
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error toggling user status: {e}")
            return False

    # 新增LLM配置相关方法
    def add_llm_config(self, user_id: int, model_name: str, model_url: str, api_key: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO llm_configurations (user_id, model_name, model_url, api_key)
                VALUES (?, ?, ?, ?)
            ''', (user_id, model_name, model_url, api_key))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # 模型名称已存在
            return False
        except Exception as e:
            print(f"Error adding LLM config: {e}")
            return False

    def get_llm_configs_by_user(self, user_id: int) -> list[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, model_name, model_url, api_key, created_at
            FROM llm_configurations
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        configs = []
        for row in cursor.fetchall():
            configs.append({
                'id': row[0],
                'model_name': row[1],
                'model_url': row[2],
                'api_key': row[3],
                'created_at': row[4]
            })
        conn.close()
        return configs

    def get_llm_config_by_id(self, config_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, model_name, model_url, api_key, created_at
            FROM llm_configurations
            WHERE id = ?
        ''', (config_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'model_name': row[2],
                'model_url': row[3],
                'api_key': row[4],
                'created_at': row[5]
            }
        return None
    
    def delete_llm_config(self, config_id: int, user_id: int) -> bool:
        """删除指定用户ID下的LLM配置"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM llm_configurations
                WHERE id = ? AND user_id = ?
            ''', (config_id, user_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0 # 检查是否有行被删除
        except Exception as e:
            print(f"Error deleting LLM config: {e}")
            return False


class SessionManager:
    def __init__(self):
        import streamlit as st
        self.st = st
        self.token_param = "session_token"
        self.remember_param = "remember_me"
    
    def save_session_to_cookies(self, session_token: str, remember_me: bool = False):
        """使用 query_params 保存会话信息"""
        # 获取当前的 query_params
        current_params = dict(self.st.query_params)
        
        # 设置会话参数
        current_params[self.token_param] = session_token
        if remember_me:
            current_params[self.remember_param] = "true"
        elif self.remember_param in current_params:
            # 如果不是记住我，删除记住我参数
            del current_params[self.remember_param]
        
        # 更新 query_params
        self.st.query_params.update(current_params)
        
        # 同时保存到 session_state 中，便于立即使用
        self.st.session_state[f"_param_{self.token_param}"] = session_token
        if remember_me:
            self.st.session_state[f"_param_{self.remember_param}"] = "true"
    
    def load_session_from_cookies(self) -> Optional[str]:
        """从 query_params 加载会话信息"""
        # 首先尝试从 session_state 获取（如果刚刚设置）
        session_key = f"_param_{self.token_param}"
        if session_key in self.st.session_state:
            return self.st.session_state[session_key]
        
        # 从 query_params 获取
        return self.st.query_params.get(self.token_param)
    
    def is_remember_me(self) -> bool:
        """检查是否启用了记住我功能"""
        # 首先尝试从 session_state 获取
        remember_key = f"_param_{self.remember_param}"
        if remember_key in self.st.session_state:
            return self.st.session_state[remember_key] == "true"
        
        # 从 query_params 获取
        return self.st.query_params.get(self.remember_param) == "true"
    
    def clear_session_from_cookies(self):
        """清除会话信息"""
        # 从 query_params 中删除会话相关参数
        current_params = dict(self.st.query_params)
        
        params_to_remove = [self.token_param, self.remember_param]
        for param in params_to_remove:
            if param in current_params:
                del current_params[param]
        
        # 更新 query_params
        self.st.query_params.clear()
        self.st.query_params.update(current_params)
        
        # 同时从 session_state 中清除
        session_keys = [f"_param_{self.token_param}", f"_param_{self.remember_param}"]
        for key in session_keys:
            if key in self.st.session_state:
                del self.st.session_state[key]
    
    def ensure_session_in_url(self):
        """确保当前会话信息在 URL 中（用于页面导航）"""
        if hasattr(self.st.session_state, 'session_token'):
            session_token = self.st.session_state.session_token
            remember_me = self.is_remember_me()
            
            # 检查 URL 中是否已经有正确的会话参数
            current_token = self.st.query_params.get(self.token_param)
            if current_token != session_token:
                self.save_session_to_cookies(session_token, remember_me)

    # 为了保持向后兼容性，保留原有的方法名
    def save_session_to_url(self, session_token: str, remember_me: bool = False):
        """保持向后兼容性的方法"""
        self.save_session_to_cookies(session_token, remember_me)
    
    def load_session_from_url(self) -> Optional[str]:
        """保持向后兼容性的方法"""
        return self.load_session_from_cookies()
    
    def clear_session_from_url(self):
        """保持向后兼容性的方法"""
        self.clear_session_from_cookies()

class AuthManager:
    def __init__(self):
        # Streamlit 的 import 需要在运行时，因为 st 对象只有在脚本执行时才可用
        import streamlit as st
        self.st = st
        self.db = DatabaseManager()
        self.session_manager = SessionManager()
        
        # 在初始化时尝试恢复会话
        self._auto_restore_session()
    
    def _auto_restore_session(self):
        """自动恢复会话（如果存在）"""
        if not self.st.session_state.get('authenticated', False):
            self.restore_session()
    
    def login(self, username: str, password: str, remember_me: bool = False) -> bool:
        user = self.db.authenticate_user(username, password)
        if user:
            session_token = self.db.create_session(user['id'], remember_me)       
            # 更新 Streamlit 的 session_state
            self.st.session_state.user = user
            self.st.session_state.authenticated = True
            self.st.session_state.session_token = session_token
            # 保存到 URL 参数
            self.session_manager.save_session_to_cookies(session_token, remember_me)
            
            return True
        return False
    
    def logout(self):
        # 删除数据库中的会话
        if hasattr(self.st.session_state, 'session_token'):
            self.db.delete_session(self.st.session_state.session_token)        
        # 清除 Streamlit 的 session_state
        for key in ['user', 'authenticated', 'session_token', 'selected_llm_config', 'messages']: # 添加清除LLM配置和聊天记录
            if key in self.st.session_state:
                del self.st.session_state[key]     
        # 清除 URL 参数
        self.session_manager.clear_session_from_cookies()
    
    def restore_session(self) -> bool:
        session_token = self.session_manager.load_session_from_cookies()        
        if session_token:
            user = self.db.validate_session(session_token)
            if user:
                self.st.session_state.user = user
                self.st.session_state.authenticated = True
                self.st.session_state.session_token = session_token
                # 确保会话信息在 URL 中
                self.session_manager.ensure_session_in_url()
                return True
            else:
                # 会话无效或过期，清除 URL 参数
                self.session_manager.clear_session_from_cookies()
        return False
    
    def is_authenticated(self) -> bool:
        # 如果session state中没有认证信息，尝试从 URL 参数恢复
        if not self.st.session_state.get('authenticated', False):
            return self.restore_session()
        else:
            # 即使已认证，也要确保 URL 中有会话参数（用于页面导航）
            self.session_manager.ensure_session_in_url()
        return True
    
    def is_admin(self) -> bool:
        if self.is_authenticated():
            user_data = self.st.session_state.get('user')
            if user_data:
                return user_data.get('role') == 'admin'
        return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        if self.is_authenticated():
            return self.st.session_state.get('user')
        return None

    # 新增LLM配置相关方法
    def add_llm_config_for_current_user(self, model_name: str, model_url: str, api_key: str) -> bool:
        if not self.is_authenticated():
            self.st.error("请先登录才能添加模型配置。")
            return False
        user_id = self.st.session_state.user['id']
        return self.db.add_llm_config(user_id, model_name, model_url, api_key)

    def get_llm_configs_for_current_user(self) -> list[Dict[str, Any]]:
        if not self.is_authenticated():
            # self.st.error("请先登录才能获取模型配置。") # 不在此处显示错误，由调用方处理
            return []
        user_id = self.st.session_state.user['id']
        return self.db.get_llm_configs_by_user(user_id)

    def get_llm_config_by_id(self, config_id: int) -> Optional[Dict[str, Any]]:
        if not self.is_authenticated():
            self.st.error("请先登录才能获取模型配置详情。")
            return None
        config = self.db.get_llm_config_by_id(config_id)
        if config and config['user_id'] == self.st.session_state.user['id']:
            return config
        else:
            self.st.error("无权访问此模型配置或配置不存在。")
            return None

    def delete_llm_config_for_current_user(self, config_id: int) -> bool:
        if not self.is_authenticated():
            self.st.error("请先登录才能删除模型配置。")
            return False
        user_id = self.st.session_state.user['id']
        # 确保用户只能删除自己的配置
        config_to_delete = self.db.get_llm_config_by_id(config_id)
        if config_to_delete and config_to_delete['user_id'] == user_id:
            return self.db.delete_llm_config(config_id, user_id)
        else:
            self.st.error("无权删除此模型配置或配置不存在。")
            return False