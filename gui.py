import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from io import StringIO
import webbrowser

# 导入现有功能模块
from main import GBStandardDownloader

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GB标准文档下载器v1.1 By HisokaH & 5512162@qq.com")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("gb_downloader.ico")
        except Exception as e:
            print(f"设置图标失败: {e}")
            
        # 初始化PDF生成状态
        self.is_pdf_generating = False
        
        # 配置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4a7abc")
        self.style.configure("TLabel", padding=4, background="#f0f0f0")
        
        # 创建主框架，使用grid布局
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置列和行的权重
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)  # 日志区域可扩展
        
        # 创建组件
        self.create_title()
        self.create_url_input()
        self.create_status_area()
        self.create_log_area()
        self.create_buttons()
        
        # 重定向标准输出到日志区域
        self.redirect_stdout()
        
        # 初始化下载器对象
        self.downloader = None
        
    def create_title(self):
        """创建程序标题"""
        self.title_label = ttk.Label(self.main_frame, text="GB标准文档下载器", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, pady=10, sticky="nsew")
        
        # 添加GB标准查询网站链接
        self.gb_website_label = ttk.Label(self.main_frame, text="GB标准查询", 
                                         foreground="blue", cursor="hand2", 
                                         font=("Arial", 10, "underline"))
        self.gb_website_label.grid(row=0, column=0, pady=(0, 5), sticky="e")
        # 绑定点击事件
        self.gb_website_label.bind("<Button-1>", lambda e: self.open_gb_website())
        # 添加悬停效果
        self.gb_website_label.bind("<Enter>", self.on_link_enter)
        self.gb_website_label.bind("<Leave>", self.on_link_leave)
        self.original_fg = self.gb_website_label.cget("foreground")
    
    def create_url_input(self):
        """创建URL输入区域"""
        # URL标签
        url_label = ttk.Label(self.main_frame, text="文档URL:")
        url_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        # URL输入框
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.main_frame, textvariable=self.url_var)
        self.url_entry.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        # URL示例提示
        example_label = ttk.Label(self.main_frame, text="示例: http://c.gb688.cn/bzgk/gb/showGb?type=online&hcno=9E5467EA1922E8342AF5F180319F34A0", 
                                font=("Arial", 8), foreground="gray")
        example_label.grid(row=3, column=0, sticky="w", pady=(0, 10))
    
    def create_status_area(self):
        """创建状态显示区域"""
        # 状态标签
        status_label = ttk.Label(self.main_frame, text="当前状态:")
        status_label.grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        # 状态显示
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_display = ttk.Label(self.main_frame, textvariable=self.status_var, 
                                      font=("Arial", 10, "bold"), foreground="green")
        self.status_display.grid(row=5, column=0, sticky="w", pady=(0, 10))
    
    def create_log_area(self):
        """创建日志显示区域"""
        # 日志标签
        log_label = ttk.Label(self.main_frame, text="运行日志:")
        log_label.grid(row=6, column=0, sticky="w", pady=(0, 5))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=15, font=("Arial", 9))
        self.log_text.grid(row=7, column=0, sticky="nsew", pady=(0, 10))
        self.log_text.config(state=tk.DISABLED)
    
    def create_buttons(self):
        """创建底部按钮区域"""
        # 创建按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=8, column=0, sticky="ew")
        
        # 设置按钮框架的列权重
        button_frame.columnconfigure(1, weight=1)  # 中间列可扩展，将按钮推到两侧
        
        # 下载按钮
        self.download_btn = ttk.Button(button_frame, text="开始下载", command=self.start_download)
        self.download_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 清空日志按钮
        self.clear_log_btn = ttk.Button(button_frame, text="清空日志", command=self.clear_log)
        self.clear_log_btn.grid(row=0, column=1)
        
        # 退出按钮
        self.exit_btn = ttk.Button(button_frame, text="退出", command=self.confirm_exit)
        self.exit_btn.grid(row=0, column=2, padx=(10, 0))
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        
    def confirm_exit(self):
        """确认退出功能"""
        if self.is_pdf_generating:
            # PDF正在生成，显示确认对话框
            result = messagebox.askyesno("确认退出", "PDF文件正在生成中，确定要退出程序吗？")
            if result:
                # 用户确认退出
                self.root.destroy()
        else:
            # PDF未在生成，直接退出
            self.root.destroy()
    
    def redirect_stdout(self):
        """重定向标准输出到日志区域"""
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget
                
            def write(self, string):
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)
            
            def flush(self):
                pass
        
        sys.stdout = StdoutRedirector(self.log_text)
    
    def start_download(self):
        """开始下载流程"""
        url = self.url_var.get().strip()
        
        # 验证URL格式
        if not url.startswith("http://c.gb688.cn/bzgk/gb/showGb"):
            messagebox.showerror("错误", "URL格式不正确，请提供正确的GB标准文档URL")
            return
        
        # 更新状态
        self.status_var.set("下载中...")
        self.status_display.config(foreground="blue")
        self.download_btn.config(state=tk.DISABLED)
        
        # 设置PDF生成状态为True
        self.is_pdf_generating = True
        
        # 在新线程中执行下载，避免阻塞GUI
        def download_thread():
            try:
                # 创建下载器实例
                self.downloader = GBStandardDownloader(document_url=url)
                
                # 执行下载，传递主窗口作为父窗口
                result = self.downloader.run(self.root)
                
                if result:
                    # 下载成功
                    self.status_var.set(f"下载完成: {os.path.basename(result)}")
                    self.status_display.config(foreground="green")
                    messagebox.showinfo("成功", f"成功下载并生成PDF: {result}\n文件保存在: {os.path.abspath(result)}")
                else:
                    # 下载失败
                    self.status_var.set("下载失败")
                    self.status_display.config(foreground="red")
                    messagebox.showerror("错误", "下载失败，请检查日志获取详细信息")
            except Exception as e:
                # 发生异常
                self.status_var.set("下载失败")
                self.status_display.config(foreground="red")
                messagebox.showerror("错误", f"下载过程中发生异常: {str(e)}")
            finally:
                # 恢复按钮状态
                self.download_btn.config(state=tk.NORMAL)
                # 设置PDF生成状态为False
                self.is_pdf_generating = False
        
        # 启动下载线程
        threading.Thread(target=download_thread, daemon=True).start()
    
    def clear_log(self):
        """清空日志区域"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def open_gb_website(self):
        """GB标准查"""
        webbrowser.open("https://openstd.samr.gov.cn/bzgk/gb/")
    
    def on_link_enter(self, event):
        """鼠标悬停在链接上时的效果"""
        self.gb_website_label.config(foreground="red")
    
    def on_link_leave(self, event):
        """鼠标离开链接时的效果"""
        self.gb_website_label.config(foreground=self.original_fg)

def main():
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
