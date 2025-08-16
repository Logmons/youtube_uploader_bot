from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
    def clear_sessions(self):
        try:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)

        except Exception as e:
            self.log_upload("SESSION ERROR", "SYSTEM", f"Failed to clear sessions: {str(e)}")
    def create_accounts_credentials(self):
        try:
            with open(self.accounts_entry.get(), 'r', encoding='utf-8') as f:
                accounts = [line.strip() for line in f.readlines() if line.strip()]

            success = 0
            for account in accounts:
                if self.create_credentials_for_account(account):
                    success += 1
                    self.log_upload("CREDENTIALS", account, "Credentials created successfully")

            messagebox.showinfo("Credentials Created",
                                f"Successfully created credentials for {success}/{len(accounts)} accounts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create credentials: {str(e)}")
            self.log_upload("CREDENTIALS ERROR", "SYSTEM", str(e))
    def authenticate_with_account(self, account_info):
        try:
            account_name = os.path.splitext(os.path.basename(account_info))[0]

            creds_file = os.path.join(os.path.dirname(__file__), f"credentials_{account_name}.json")

            if not os.path.exists(creds_file):
                self.log_upload("AUTH ERROR", account_info, "Credentials file not found")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                creds_file,
                scopes=['https://www.googleapis.com/auth/youtube.upload']
            )
            credentials = flow.run_local_server(port=0)
            return build('youtube', 'v3', credentials=credentials)
        except Exception as e:
            self.log_upload("AUTH ERROR", account_info, str(e))
            return None

    def create_credentials_for_account(self, account_info):
        try:
            account_name = os.path.splitext(os.path.basename(account_info))[0]

            creds_file = os.path.join(os.path.dirname(__file__), f"credentials_{account_name}.json")

            if os.path.exists(creds_file):
                return True

            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json',
                scopes=['https://www.googleapis.com/auth/youtube.upload']
            )
            credentials = flow.run_local_server(port=0)

            with open(creds_file, 'w') as token:
                token.write(credentials.to_json())

            return True
        except Exception as e:
            self.log_upload("CREDENTIALS ERROR", account_info, str(e))
            return False
    def authenticate_youtube(self):
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        # 1. Set up OAuth 2.0 credentials
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )

        # 2. Run local server for authentication
        credentials = flow.run_local_server(port=0)

        # 3. Build YouTube service
        youtube = build('youtube', 'v3', credentials=credentials)
        return youtube

    def upload_video(self, youtube, video_path, title, description):
        from googleapiclient.http import MediaFileUpload

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "categoryId": "22"  # 22 is for People & Blogs
                },
                "status": {
                    "privacyStatus": "public"  # Can be "public", "private", or "unlisted"
                }
            },
            media_body=MediaFileUpload(video_path)
        )

        response = request.execute()
        return response

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Upload Bot")
        self.setup_ui()
        self.current_proxy_index = 0

    def setup_ui(self):
        # Video Folder
        tk.Label(self.root, text="Videos Folder:").grid(row=0, column=0, padx=5, pady=5)
        self.video_folder_entry = tk.Entry(self.root, width=50)
        self.video_folder_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_video_folder).grid(row=0, column=2, padx=5, pady=5)

        # Accounts File
        tk.Label(self.root, text="Accounts File:").grid(row=1, column=0, padx=5, pady=5)
        self.accounts_entry = tk.Entry(self.root, width=50)
        self.accounts_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse",
                  command=lambda: self.browse_file(self.accounts_entry, "accounts.txt")).grid(row=1, column=2, padx=5,
                                                                                              pady=5)

        # Titles File
        tk.Label(self.root, text="Titles File:").grid(row=2, column=0, padx=5, pady=5)
        self.titles_entry = tk.Entry(self.root, width=50)
        self.titles_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse",
                  command=lambda: self.browse_file(self.titles_entry, "titles.txt")).grid(row=2, column=2, padx=5,
                                                                                          pady=5)

        # Descriptions File
        tk.Label(self.root, text="Descriptions File:").grid(row=3, column=0, padx=5, pady=5)
        self.descriptions_entry = tk.Entry(self.root, width=50)
        self.descriptions_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse",
                  command=lambda: self.browse_file(self.descriptions_entry, "descriptions.txt")).grid(row=3, column=2,
                                                                                                      padx=5, pady=5)

        # Videos per Account
        tk.Label(self.root, text="Videos per Account:").grid(row=4, column=0, padx=5, pady=5)
        self.videos_per_account = tk.Spinbox(self.root, from_=1, to=10, width=5)
        self.videos_per_account.grid(row=4, column=1, sticky="w")
        self.videos_per_account.delete(0, "end")
        self.videos_per_account.insert(0, "2")

        # Sleep Time
        tk.Label(self.root, text="Sleep Time (sec):").grid(row=5, column=0, padx=5, pady=5)
        self.sleep_time = tk.Spinbox(self.root, from_=1, to=3600, width=5)
        self.sleep_time.grid(row=5, column=1, sticky="w")
        self.sleep_time.delete(0, "end")
        self.sleep_time.insert(0, "60")

        # Proxies File
        tk.Label(self.root, text="Proxies File:").grid(row=6, column=0, padx=5, pady=5)
        self.proxies_entry = tk.Entry(self.root, width=50)
        self.proxies_entry.grid(row=6, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse",
                  command=lambda: self.browse_file(self.proxies_entry, "proxies.txt")).grid(row=6, column=2, padx=5,
                                                                                            pady=5)

        # Upload Button
        tk.Button(self.root, text="Start Upload", command=self.start_upload).grid(row=10, column=1, pady=10)
        tk.Button(self.root, text="Create Account Credentials", command=self.create_accounts_credentials).grid(row=11,
                                                                                                         column=1,
                                                                                                               pady=10)
    def browse_video_folder(self):
        folder = filedialog.askdirectory()
        self.video_folder_entry.delete(0, tk.END)
        self.video_folder_entry.insert(0, folder)

    def load_config_file(self, label_text, file_name, row_num):
        tk.Label(self.root, text=label_text).grid(row=row_num, column=0, padx=5, pady=5)
        entry = tk.Entry(self.root, width=50)
        entry.grid(row=row_num, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse",
                  command=lambda: self.browse_file(entry, file_name)).grid(row=row_num, column=2, padx=5, pady=5)
        return entry

    def browse_file(self, entry, default_name):
        file_path = filedialog.askopenfilename(initialfile=default_name)
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def check_duration(self, video_path):
        import cv2
        try:
            video = cv2.VideoCapture(video_path)
            fps = video.get(cv2.CAP_PROP_FPS)
            frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frames / fps
            video.release()
            return duration <= 25
        except:
            return False

    def rotate_proxy(self):
        try:
            if not os.path.exists(self.proxies_entry.get()):
                return None

            with open(self.proxies_entry.get(), 'r') as f:
                proxies = [p.strip() for p in f.readlines() if p.strip()]
                if not proxies:
                    return None

                proxy = proxies[self.current_proxy_index % len(proxies)]
                self.current_proxy_index += 1

                os.environ['HTTP_PROXY'] = f'http://{proxy}'
                os.environ['HTTPS_PROXY'] = f'http://{proxy}'
                return True
        except Exception as e:
            messagebox.showwarning("Proxy Error", f"Failed to load proxies: {str(e)}")
            return False

    def log_upload(self, filename, account, status):
        log_msg = f"""
        [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
        Account: {account}
        Video: {filename}
        Status: {status}
        {'-' * 40}"""
        with open("output.log", "a", encoding="utf-8") as f:
            f.write(log_msg)

    def start_upload(self):
        try:
            required_files = [
                (self.accounts_entry.get(), "Accounts file"),
                (self.titles_entry.get(), "Titles file"),
                (self.descriptions_entry.get(), "Descriptions file")
            ]

            for file_path, file_name in required_files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"{file_name} not found at {file_path}")
            with open(self.accounts_entry.get(), 'r', encoding='utf-8') as f:
                accounts = [line.strip() for line in f.readlines() if line.strip()]

            if not accounts:
                raise ValueError("No accounts found in accounts file")

            video_folder = self.video_folder_entry.get()
            video_files = [f for f in os.listdir(video_folder)
                           if f.lower().endswith(('.mp4', '.avi', '.mov'))]

            with open(self.titles_entry.get(), 'r', encoding='utf-8') as f:
                titles = [line.strip() for line in f.readlines() if line.strip()]

            with open(self.descriptions_entry.get(), 'r', encoding='utf-8') as f:
                descriptions = [line.strip() for line in f.readlines() if line.strip()]
            required_files = [
                (self.accounts_entry.get(), "Accounts file"),
                (self.titles_entry.get(), "Titles file"),
                (self.descriptions_entry.get(), "Descriptions file")
            ]

            for file_path, file_name in required_files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"{file_name} not found at {file_path}")
            uploaded_total = 0
            max_per_account = int(self.videos_per_account.get())
            total_videos = min(len(video_files), len(titles), len(descriptions))

            current_video_index = 0

            for account in accounts:
                try:
                    if self.proxies_entry.get():
                        self.rotate_proxy()

                    youtube = self.authenticate_with_account(account) if hasattr(self,
                                                                                 'authenticate_with_account') else self.authenticate_youtube()

                    uploaded_for_account = 0
                    for _ in range(min(max_per_account, total_videos - current_video_index)):
                        if current_video_index >= total_videos:
                            break

                        video_path = os.path.join(video_folder, video_files[current_video_index])
                        title = titles[current_video_index]
                        description = descriptions[current_video_index]

                        if not self.check_duration(video_path):
                            self.log_upload(video_files[current_video_index], account, "SKIPPED (Duration  25s)")
                            current_video_index += 1
                            continue

                        try:
                            response = self.upload_video(youtube, video_path, title, description)
                            uploaded_for_account += 1
                            uploaded_total += 1
                            self.log_upload(video_files[current_video_index], account,
                                            f"SUCCESS | Video ID: {response['id']}")
                            current_video_index += 1

                            if uploaded_for_account < max_per_account:
                                sleep_time = int(self.sleep_time.get()) if hasattr(self, 'sleep_time') else 60
                                time.sleep(sleep_time)

                        except Exception as upload_error:
                            self.log_upload(video_files[current_video_index], account, f"ERROR: {str(upload_error)}")
                            current_video_index += 1
                            continue

                except Exception as account_error:
                    self.log_upload("ACCOUNT ERROR", account, str(account_error))
                    continue

            messagebox.showinfo("Upload Complete",
                                f"Total Uploaded: {uploaded_total} videos across {len(accounts)} accounts")

        except Exception as main_error:
            messagebox.showerror("System Error", f"Operation failed: {str(main_error)}")
            self.log_upload("SYSTEM", "CRITICAL ERROR", str(main_error))
if __name__ == "__main__":
    app = None
    try:
        app = YouTubeUploader()
        app.root.mainloop()
    except Exception as e:
        error_msg = f"[{datetime.now()}] CRITICAL ERROR: {str(e)}\n"
        with open("error_log.txt", "a") as f:
            f.write(error_msg)
        messagebox.showerror("Fatal Error", f"The application crashed: {str(e)}")
    finally:
        if app:
            app.clear_sessions()