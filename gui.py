import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
import sys
from LeakGuard.google_search import search_google
from LeakGuard.github_search import search_github
from LeakGuard.email_leak import check_one_email, batch_process_emails_for
from LeakGuard.pass_leak import check_pass_leak, batch_check_pass_leak
from LeakGuard.utils import set_sensitiveWords, set_blacklistUsers, read_file
from LeakGuard.hunter_search import search_hunter


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)

    def flush(self):
        pass


class LeakGuardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LeakGuard - 综合性泄露检测工具 By AgonySec")
        self.root.geometry("900x750")
        self.root.minsize(800, 600)

        # 设置日志处理器以捕获日志输出
        self.log_text_handler = TextHandler(self)

        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[self.log_text_handler]
        )
        self.logger = logging.getLogger(__name__)

        # 重定向stdout到GUI文本框
        self.stdout_redirector = None

        # 添加当前标签页跟踪变量
        self.current_tab = None

        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建 Notebook (标签页)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # 创建各个功能标签页
        self.create_email_tab(self.notebook)
        self.create_password_tab(self.notebook)
        self.create_google_tab(self.notebook)
        self.create_github_tab(self.notebook)
        self.create_hunter_tab(self.notebook)
        self.create_settings_tab(self.notebook)

        # 创建输出区域框架
        output_frame = ttk.LabelFrame(main_frame, text="输出信息")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建文本框和滚动条
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_text = tk.Text(text_frame, wrap=tk.WORD, height=12)
        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.output_text.xview)
        self.output_text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.output_text.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # 控制按钮框架
        control_frame = ttk.Frame(output_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="清空输出", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="自动滚动", variable=self.auto_scroll_var).pack(side=tk.LEFT, padx=5)

        # 创建底部按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        self.run_button = ttk.Button(button_frame, text="开始检测", command=self.run_detection)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 运行状态
        self.running = False

        # 重定向标准输出
        self.stdout_redirector = TextRedirector(self.output_text)
        sys.stdout = self.stdout_redirector

    def on_tab_changed(self, event=None):
        """处理标签页切换事件，清空之前标签页的输入内容"""
        # 获取当前选中的标签页索引
        current_tab_index = self.notebook.index(self.notebook.select())
        previous_tab = self.current_tab
        self.current_tab = current_tab_index

        # 如果这是第一次加载或标签页没有变化，则不执行清空操作
        if previous_tab is None or previous_tab == current_tab_index:
            return

        # 根据之前选中的标签页清空对应输入框
        if previous_tab == 0:  # 邮箱检测标签页
            self.clear_email_inputs()
        elif previous_tab == 1:  # 密码检测标签页
            self.clear_password_inputs()
        elif previous_tab == 2:  # Google搜索标签页
            self.clear_google_inputs()
        elif previous_tab == 3:  # GitHub搜索标签页
            self.clear_github_inputs()
        elif previous_tab == 4:  # Hunter搜索标签页
            self.clear_hunter_inputs()
        # 注意：设置标签页(索引5)不需要清空，因为它不涉及检测输入

    def clear_email_inputs(self):
        """清空邮箱检测标签页的输入内容"""
        if hasattr(self, 'email_entry') and self.email_entry:
            self.email_entry.delete(0, tk.END)
        if hasattr(self, 'email_file_entry') and self.email_file_entry:
            self.email_file_entry.delete(0, tk.END)

    def clear_password_inputs(self):
        """清空密码检测标签页的输入内容"""
        if hasattr(self, 'password_entry') and self.password_entry:
            self.password_entry.delete(0, tk.END)
        if hasattr(self, 'pass_file_entry') and self.pass_file_entry:
            self.pass_file_entry.delete(0, tk.END)

    def clear_google_inputs(self):
        """清空Google搜索标签页的输入内容"""
        if hasattr(self, 'google_suffix_entry') and self.google_suffix_entry:
            self.google_suffix_entry.delete(0, tk.END)
        if hasattr(self, 'google_file_entry') and self.google_file_entry:
            self.google_file_entry.delete(0, tk.END)

    def clear_github_inputs(self):
        """清空GitHub搜索标签页的输入内容"""
        if hasattr(self, 'github_query_entry') and self.github_query_entry:
            self.github_query_entry.delete(0, tk.END)
        if hasattr(self, 'github_file_entry') and self.github_file_entry:
            self.github_file_entry.delete(0, tk.END)

    def clear_hunter_inputs(self):
        """清空Hunter搜索标签页的输入内容"""
        if hasattr(self, 'hunter_domain_entry') and self.hunter_domain_entry:
            self.hunter_domain_entry.delete(0, tk.END)


    def create_email_tab(self, notebook):
        email_frame = ttk.Frame(notebook)
        notebook.add(email_frame, text="邮箱检测")

        # 主框架
        main_frame = ttk.Frame(email_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 单个邮箱检测
        single_email_frame = ttk.LabelFrame(main_frame, text="单个邮箱检测")
        single_email_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(single_email_frame, text="邮箱地址:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_entry = ttk.Entry(single_email_frame, width=40)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(single_email_frame, text="清空", command=lambda: self.email_entry.delete(0, tk.END)).grid(row=0, column=2, padx=5, pady=5)

        # 批量邮箱检测
        batch_email_frame = ttk.LabelFrame(main_frame, text="批量邮箱检测")
        batch_email_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(batch_email_frame, text="邮箱文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_file_entry = ttk.Entry(batch_email_frame, width=40)
        self.email_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(batch_email_frame, text="浏览", command=self.browse_email_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(batch_email_frame, text="清空", command=lambda: self.email_file_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

    def create_password_tab(self, notebook):
        password_frame = ttk.Frame(notebook)
        notebook.add(password_frame, text="密码检测")

        # 主框架
        main_frame = ttk.Frame(password_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 单个密码检测
        single_pass_frame = ttk.LabelFrame(main_frame, text="单个密码检测")
        single_pass_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(single_pass_frame, text="密码:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.password_entry = ttk.Entry(single_pass_frame, width=40, show="*")
        self.password_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(single_pass_frame, text="清空", command=lambda: self.password_entry.delete(0, tk.END)).grid(row=0, column=2, padx=5, pady=5)

        # 批量密码检测
        batch_pass_frame = ttk.LabelFrame(main_frame, text="批量密码检测")
        batch_pass_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(batch_pass_frame, text="密码文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pass_file_entry = ttk.Entry(batch_pass_frame, width=40)
        self.pass_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(batch_pass_frame, text="浏览", command=self.browse_pass_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(batch_pass_frame, text="清空", command=lambda: self.pass_file_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

    def create_google_tab(self, notebook):
        google_frame = ttk.Frame(notebook)
        notebook.add(google_frame, text="Google搜索")

        # 主框架
        main_frame = ttk.Frame(google_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 单个邮箱后缀搜索
        single_google_frame = ttk.LabelFrame(main_frame, text="单个邮箱后缀搜索")
        single_google_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(single_google_frame, text="邮箱后缀:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.google_suffix_entry = ttk.Entry(single_google_frame, width=40)
        self.google_suffix_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(single_google_frame, text="例如: @qq.com").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Button(single_google_frame, text="清空", command=lambda: self.google_suffix_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

        # 批量邮箱后缀搜索
        batch_google_frame = ttk.LabelFrame(main_frame, text="批量邮箱后缀搜索")
        batch_google_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(batch_google_frame, text="后缀文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.google_file_entry = ttk.Entry(batch_google_frame, width=40)
        self.google_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(batch_google_frame, text="浏览", command=self.browse_google_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(batch_google_frame, text="清空", command=lambda: self.google_file_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

    def create_github_tab(self, notebook):
        github_frame = ttk.Frame(notebook)
        notebook.add(github_frame, text="GitHub搜索")

        # 主框架
        main_frame = ttk.Frame(github_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 单个关键字搜索
        single_github_frame = ttk.LabelFrame(main_frame, text="单个关键字搜索")
        single_github_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(single_github_frame, text="关键字:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.github_query_entry = ttk.Entry(single_github_frame, width=40)
        self.github_query_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(single_github_frame, text="清空", command=lambda: self.github_query_entry.delete(0, tk.END)).grid(row=0, column=2, padx=5, pady=5)

        # 批量关键字搜索
        batch_github_frame = ttk.LabelFrame(main_frame, text="批量关键字搜索")
        batch_github_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(batch_github_frame, text="关键字文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.github_file_entry = ttk.Entry(batch_github_frame, width=40)
        self.github_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(batch_github_frame, text="浏览", command=self.browse_github_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(batch_github_frame, text="清空", command=lambda: self.github_file_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

    def create_hunter_tab(self, notebook):
        hunter_frame = ttk.Frame(notebook)
        notebook.add(hunter_frame, text="Hunter搜索")

        # 主框架
        main_frame = ttk.Frame(hunter_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Hunter搜索
        hunter_search_frame = ttk.LabelFrame(main_frame, text="Hunter邮箱搜索")
        hunter_search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(hunter_search_frame, text="域名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.hunter_domain_entry = ttk.Entry(hunter_search_frame, width=40)
        self.hunter_domain_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(hunter_search_frame, text="例如: example.com").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Button(hunter_search_frame, text="清空", command=lambda: self.hunter_domain_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

    def create_settings_tab(self, notebook):
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="设置")

        # 主框架
        main_frame = ttk.Frame(settings_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 输出设置
        output_frame = ttk.LabelFrame(main_frame, text="输出设置")
        output_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(output_frame, text="输出文件名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_entry = ttk.Entry(output_frame, width=40)
        self.output_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(output_frame, text="(不包含后缀)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Button(output_frame, text="清空", command=lambda: self.output_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

        # 输出格式
        format_frame = ttk.Frame(output_frame)
        format_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        self.output_format = tk.StringVar(value="xlsx")
        ttk.Radiobutton(format_frame, text="XLSX", variable=self.output_format, value="xlsx").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="JSON", variable=self.output_format, value="json").pack(side=tk.LEFT, padx=5)

        # 黑名单用户文件
        blacklist_frame = ttk.LabelFrame(main_frame, text="黑名单设置")
        blacklist_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(blacklist_frame, text="黑名单用户文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.blacklist_file_entry = ttk.Entry(blacklist_frame, width=40)
        self.blacklist_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(blacklist_frame, text="浏览", command=self.browse_blacklist_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(blacklist_frame, text="清空", command=lambda: self.blacklist_file_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

        # 敏感词文件
        sensitive_frame = ttk.LabelFrame(main_frame, text="敏感词设置")
        sensitive_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(sensitive_frame, text="敏感词文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.sensitive_file_entry = ttk.Entry(sensitive_frame, width=40)
        self.sensitive_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(sensitive_frame, text="浏览", command=self.browse_sensitive_file).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(sensitive_frame, text="清空", command=lambda: self.sensitive_file_entry.delete(0, tk.END)).grid(row=0, column=3, padx=5, pady=5)

    def browse_email_file(self):
        filename = filedialog.askopenfilename(
            title="选择邮箱文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.email_file_entry.delete(0, tk.END)
            self.email_file_entry.insert(0, filename)

    def browse_pass_file(self):
        filename = filedialog.askopenfilename(
            title="选择密码文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.pass_file_entry.delete(0, tk.END)
            self.pass_file_entry.insert(0, filename)

    def browse_google_file(self):
        filename = filedialog.askopenfilename(
            title="选择Google邮箱后缀文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.google_file_entry.delete(0, tk.END)
            self.google_file_entry.insert(0, filename)

    def browse_github_file(self):
        filename = filedialog.askopenfilename(
            title="选择GitHub关键字文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.github_file_entry.delete(0, tk.END)
            self.github_file_entry.insert(0, filename)

    def browse_blacklist_file(self):
        filename = filedialog.askopenfilename(
            title="选择黑名单用户文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.blacklist_file_entry.delete(0, tk.END)
            self.blacklist_file_entry.insert(0, filename)

    def browse_sensitive_file(self):
        filename = filedialog.askopenfilename(
            title="选择敏感词文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.sensitive_file_entry.delete(0, tk.END)
            self.sensitive_file_entry.insert(0, filename)

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

    def run_detection(self):
        # 在新线程中运行检测，避免阻塞GUI
        self.running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()

        thread = threading.Thread(target=self._run_detection_thread)
        thread.daemon = True
        thread.start()

    def _setup_blacklist_and_sensitive_words(self):
        if self.blacklist_file_entry.get():
            try:
                blacklist_users = read_file(self.blacklist_file_entry.get())
                set_blacklistUsers(blacklist_users)
                self.logger.info(f"已加载 {len(blacklist_users)} 个黑名单用户")
            except Exception as e:
                self.logger.error(f"加载黑名单用户文件失败: {str(e)}")

        if self.sensitive_file_entry.get():
            try:
                sensitive_words = read_file(self.sensitive_file_entry.get())
                set_sensitiveWords(sensitive_words)
                self.logger.info(f"已加载 {len(sensitive_words)} 个敏感词")
            except Exception as e:
                self.logger.error(f"加载敏感词文件失败: {str(e)}")

    def _run_detection_thread(self):
        try:
            self.logger.info("="*50)
            self.logger.info("开始泄露检测...")

            # 获取设置
            output_file = self.output_entry.get() if self.output_entry.get() else None
            mode = self.output_format.get()

            # 检查邮箱输入冲突
            if self.email_entry.get() and self.email_file_entry.get():
                self.logger.error("请输入单个邮箱地址或文件路径，不要同时输入！")
                return

            # 设置黑名单和敏感词
            self._setup_blacklist_and_sensitive_words()

            # 执行各项检测
            executed = False

            if self.github_query_entry.get() or self.github_file_entry.get():
                self.logger.info("执行GitHub搜索...")
                if self.github_query_entry.get():
                    search_github(query=self.github_query_entry.get(), output_file=output_file, mode=mode)
                    executed = True
                if self.github_file_entry.get():
                    search_github(file=self.github_file_entry.get(), output_file=output_file, mode=mode)
                    executed = True

            if self.google_suffix_entry.get() or self.google_file_entry.get():
                self.logger.info("执行Google搜索...")
                if self.google_suffix_entry.get():
                    search_google(email_suffix=self.google_suffix_entry.get(), output_file=output_file, mode=mode)
                    executed = True
                if self.google_file_entry.get():
                    search_google(file=self.google_file_entry.get(), output_file=output_file, mode=mode)
                    executed = True

            if self.email_entry.get() or self.email_file_entry.get():
                self.logger.info("执行邮箱泄露检测...")
                if self.email_entry.get():
                    check_one_email(self.email_entry.get(), output_file, mode)
                    executed = True
                if self.email_file_entry.get():
                    batch_process_emails_for(self.email_file_entry.get(), output_file, mode)
                    executed = True

            if self.password_entry.get() or self.pass_file_entry.get():
                self.logger.info("执行密码泄露检测...")
                if self.password_entry.get():
                    check_pass_leak(self.password_entry.get())
                    executed = True
                if self.pass_file_entry.get():
                    batch_check_pass_leak(self.pass_file_entry.get())
                    executed = True

            if self.hunter_domain_entry.get():
                self.logger.info("执行Hunter搜索...")
                search_hunter(domain=self.hunter_domain_entry.get(), output_file=output_file, mode=mode)
                executed = True

            if not executed:
                self.logger.warning("未选择任何检测项目，请选择至少一个检测项再运行")

            self.logger.info("检测完成！")
            self.logger.info("="*50)

        except Exception as e:
            self.logger.error(f"检测过程中发生错误: {str(e)}")
        finally:
            self.running = False
            self.root.after(0, self._enable_buttons)

    def _enable_buttons(self):
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress.stop()

    def stop_detection(self):
        self.running = False
        self.logger.info("检测已停止")
        self._enable_buttons()


class TextHandler(logging.Handler):
    def __init__(self, gui):
        logging.Handler.__init__(self)
        self.gui = gui

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.gui.output_text.insert(tk.END, msg + '\n')
            if self.gui.auto_scroll_var.get():
                self.gui.output_text.see(tk.END)

        self.gui.root.after(0, append)


def main():
    root = tk.Tk()
    app = LeakGuardGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
