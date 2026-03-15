import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTextBrowser, 
                             QLineEdit, QLabel, QSplitter, QPushButton, QTabWidget, QListWidget, QListWidgetItem, QAbstractItemView, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QIcon, QCursor, QColor, QPalette

class EsbabApp(QMainWindow):
    def __init__(self, data_path="data.json", meta_path="quran_meta.json"):
        super().__init__()
        self.data_path = data_path
        self.meta_path = meta_path
        
        # Load Settings
        self.settings = QSettings("EsbabNuzul", "App")
        self.is_dark_mode = self.settings.value("is_dark_mode", True, type=bool)
        self.base_font_size = self.settings.value("base_font_size", 16, type=int)
        
        # Load bookmarks securely via JSON to avoid type corruption
        bookmarks_json = self.settings.value("bookmarks_json", "[]", type=str)
        try:
            self.bookmarks = json.loads(bookmarks_json)
        except:
            self.bookmarks = []
        
        self.raw_data = self.load_data()
        self.meta_data = self.load_meta()
        self.init_ui()
        
    def closeEvent(self, event):
        # Save Settings before closing
        self.settings.setValue("is_dark_mode", self.is_dark_mode)
        self.settings.setValue("base_font_size", self.base_font_size)
        
        # Save last read if available
        if hasattr(self, 'current_item_data') and self.current_item_data:
            self.settings.setValue("last_read", self.current_item_data)
        
        self.settings.setValue("bookmarks_json", json.dumps(self.bookmarks, ensure_ascii=False))
        super().closeEvent(event)
        
    def load_data(self):
        import sys, os
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        full_path = os.path.join(base_path, self.data_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

    def load_meta(self):
        import sys, os
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        full_path = os.path.join(base_path, self.meta_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f).get('data', {})
        except Exception as e:
            print(f"Error loading meta: {e}")
            return {}

    def init_ui(self):
        self.setWindowTitle("Esbab-ı Nüzul")
        self.resize(1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header Toolbar
        header_widget = QWidget()
        header_widget.setObjectName("HeaderWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(25, 5, 25, 5)
        
        title_label = QLabel("Esbab-ı Nüzul")
        title_label.setObjectName("AppTitle")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.btn_theme = QPushButton("☀️" if self.is_dark_mode else "🌙")
        self.btn_theme.setToolTip("Gündüz/Gece Modu")
        self.btn_theme.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_theme.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.btn_theme)

        self.btn_bookmark = QPushButton("Yer İmi Ekle")
        self.btn_bookmark.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_bookmark.clicked.connect(self.add_bookmark)
        header_layout.addWidget(self.btn_bookmark)
        
        self.btn_remove_bookmark = QPushButton("Yer İmi Kaldır")
        self.btn_remove_bookmark.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_remove_bookmark.clicked.connect(self.remove_bookmark)
        header_layout.addWidget(self.btn_remove_bookmark)
        
        self.btn_copy = QPushButton("Metni Kopyala")
        self.btn_copy.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_copy.clicked.connect(self.copy_content)
        header_layout.addWidget(self.btn_copy)
        
        self.btn_zoom_out = QPushButton("A-")
        self.btn_zoom_out.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_zoom_out.setFixedSize(40, 40)
        self.btn_zoom_out.clicked.connect(self.decrease_font)
        header_layout.addWidget(self.btn_zoom_out)
        
        self.btn_zoom_in = QPushButton("A+")
        self.btn_zoom_in.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_zoom_in.setFixedSize(40, 40)
        self.btn_zoom_in.clicked.connect(self.increase_font)
        header_layout.addWidget(self.btn_zoom_in)
        
        main_layout.addWidget(header_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sidebar: Tabs for Sureler, Cüzler, Sayfalar, Yer İmleri
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(15, 15, 10, 15)
        
        # Search Box and Ayah Jump
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Sure Ara...")
        self.search_box.textChanged.connect(self.filter_tree)
        self.search_box.setMinimumHeight(45)
        search_layout.addWidget(self.search_box, 3) # Stretch factor 3
        
        self.ayah_input = QLineEdit()
        self.ayah_input.setPlaceholderText("Ayet No")
        self.ayah_input.setMinimumHeight(45)
        self.ayah_input.returnPressed.connect(self.jump_to_ayah)
        self.ayah_input.setFixedWidth(80)
        search_layout.addWidget(self.ayah_input, 1) # Stretch factor 1
        
        self.btn_jump = QPushButton("Git")
        self.btn_jump.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_jump.setMinimumHeight(45)
        self.btn_jump.setFixedWidth(50)
        self.btn_jump.clicked.connect(self.jump_to_ayah)
        search_layout.addWidget(self.btn_jump, 0)
        
        sidebar_layout.addLayout(search_layout)
        
        self.tabs = QTabWidget()
        
        # 1. Sureler Tab
        self.tree_surah = QTreeWidget()
        self.tree_surah.setHeaderHidden(True)
        self.tree_surah.itemClicked.connect(self.display_content)
        self.tabs.addTab(self.tree_surah, "Sureler")
        
        # 2. Yer İmleri Tab
        self.list_bookmarks = QListWidget()
        self.list_bookmarks.itemClicked.connect(self.load_bookmark)
        self.tabs.addTab(self.list_bookmarks, "Yer İmleri")
        
        sidebar_layout.addWidget(self.tabs)
        
        self.populate_trees()
        self.populate_bookmarks()
        
        # Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 15, 15, 15)
        
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        content_layout.addWidget(self.content_browser)
        
        splitter.addWidget(sidebar_widget)
        splitter.addWidget(content_widget)
        splitter.setSizes([350, 750])
        
        self.apply_styles()
        
        # Restore last read position or default
        last_read = self.settings.value("last_read", None)
        if last_read:
            self.load_item_data(last_read)
        elif self.tree_surah.topLevelItemCount() > 0:
            first_item = self.tree_surah.topLevelItem(0)
            self.tree_surah.setCurrentItem(first_item)
            self.display_content(first_item, 0)
    def load_item_data(self, item_data):
        self.current_item_data = item_data
        html = ""
        
        if item_data.get("type") == "surah":
            surah = item_data["data"]
            html += f"<div class='surah-title'>{surah.get('name', '')}</div><hr>"
            
            if surah.get('intro'):
                html += f"<div class='intro-text'>{surah['intro']}</div>"
                
            for ayah in surah.get('ayahs', []):
                html += self.build_ayah_html(ayah)
                
        elif item_data.get("type") == "ayah":
            surah_name = item_data.get("surah_name", "")
            ayah = item_data["data"]
            
            html += f"<div class='surah-title'>{surah_name}</div><hr>"
            html += self.build_ayah_html(ayah)

        self.current_html_content = html
        self.refresh_html_view()

    def populate_trees(self):
        self.tree_surah.clear()
        
        # 1. Populate Surahs
        for surah_idx, surah in enumerate(self.raw_data):
            surah_name = surah.get("name", f"Sure {surah_idx+1}")
            
            surah_item = QTreeWidgetItem(self.tree_surah)
            surah_item.setText(0, surah_name)
            surah_item.setData(0, Qt.UserRole, {"type": "surah", "data": surah, "name": surah_name})
            
            for ayah_idx, ayah in enumerate(surah.get("ayahs", [])):
                ayah_num = ayah.get("ayah_number", str(ayah_idx + 1))
                
                ayah_item = QTreeWidgetItem(surah_item)
                ayah_item.setText(0, f"{ayah_num}. Ayet")
                ayah_item.setData(0, Qt.UserRole, {"type": "ayah", "surah_name": surah_name, "data": ayah})

    def filter_tree(self, text):
        query = text.lower()
        
        def filter_items(tree):
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                item_match = query in item.text(0).lower()
                
                any_child_match = False
                for j in range(item.childCount()):
                    child = item.child(j)
                    child_match = query in child.text(0).lower()
                    child.setHidden(not (item_match or child_match))
                    if child_match:
                        any_child_match = True
                
                item.setHidden(not (item_match or any_child_match))
                if any_child_match and query:
                    item.setExpanded(True)
                elif not query:
                    item.setExpanded(False)

        filter_items(self.tree_surah)

    def display_content(self, item, column):
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
            
        self.current_item_data = item_data
        html = ""
        
        if item_data["type"] == "surah":
            surah = item_data["data"]
            html += f"<div class='surah-title'>{surah.get('name', '')}</div><hr>"
            
            if surah.get('intro'):
                html += f"<div class='intro-text'>{surah['intro']}</div>"
                
            for ayah in surah.get('ayahs', []):
                html += self.build_ayah_html(ayah)
                
        elif item_data["type"] == "ayah":
            surah_name = item_data["surah_name"]
            ayah = item_data["data"]
            
            html += f"<div class='surah-title'>{surah_name}</div><hr>"
            html += self.build_ayah_html(ayah)

        # Store last rendered html block for copy functionality & refresh
        self.current_html_content = html
        self.refresh_html_view()

    def jump_to_ayah(self):
        target_ayah_str = self.ayah_input.text().strip()
        if not target_ayah_str:
            return
            
        current_tree = self.tabs.currentWidget()
        if current_tree != self.tree_surah:
            self.tabs.setCurrentWidget(self.tree_surah)
            
        # Get selected surah
        sel_items = self.tree_surah.selectedItems()
        if not sel_items:
            if self.tree_surah.topLevelItemCount() > 0:
                item = self.tree_surah.topLevelItem(0)
            else:
                QMessageBox.information(self, "Bilgi", "Lütfen önce bir sure seçin.")
                return
        else:
            item = sel_items[0]
            
        # if item is ayah, get parent
        if item.data(0, Qt.UserRole).get("type") == "ayah":
            item = item.parent()
            
        # Item is now the surah. Let's find child.
        found = False
        import re
        for i in range(item.childCount()):
            child = item.child(i)
            ayah_data = child.data(0, Qt.UserRole).get("data", {})
            ayah_num = str(ayah_data.get("ayah_number", ""))
            
            parts = re.findall(r'\d+', ayah_num)
            
            if target_ayah_str == ayah_num or target_ayah_str in parts:
                self.tree_surah.setCurrentItem(child)
                self.display_content(child, 0)
                found = True
                break
                
        if not found:
            QMessageBox.warning(self, "Uyarı", f"Bu surede {target_ayah_str}. ayet bulunamadı.")

    def add_bookmark(self):
        if hasattr(self, 'current_item_data') and self.current_item_data:
            item = self.current_item_data
            
            title = ""
            if item.get("type") == "surah":
                title = item.get("name", "Sure")
            elif item.get("type") == "ayah":
                sn = item.get("surah_name", "")
                an = item.get("data", {}).get("ayah_number", "")
                title = f"{sn} - {an}. Ayet"
                
            # Avoid duplicates
            for b in self.bookmarks:
                if b.get("title") == title:
                    QMessageBox.information(self, "Bilgi", "Bu yer imi zaten mevcut!")
                    return
                
            bm = {"title": title, "data": item}
            self.bookmarks.append(bm)
            self.populate_bookmarks()
            QMessageBox.information(self, "Başarılı", "Yer imi eklendi!")
            
    def remove_bookmark(self):
        current_item = self.list_bookmarks.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için önce bir yer imi seçin.")
            return
            
        title = current_item.text()
        # Find and remove the bookmark
        for i, bm in enumerate(self.bookmarks):
            if bm.get("title") == title:
                del self.bookmarks[i]
                break
                
        self.populate_bookmarks()
        QMessageBox.information(self, "Başarılı", "Yer imi kaldırıldı!")
        
    def populate_bookmarks(self):
        self.list_bookmarks.clear()
        for bm in self.bookmarks:
            item = QListWidgetItem(bm["title"])
            item.setData(Qt.UserRole, bm["data"])
            self.list_bookmarks.addItem(item)
            
    def load_bookmark(self, item):
        data = item.data(Qt.UserRole)
        if data:
            self.load_item_data(data)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.btn_theme.setText("☀️" if self.is_dark_mode else "🌙")
        self.apply_styles()
        self.refresh_html_view()

    def refresh_html_view(self):
        if not hasattr(self, 'current_html_content'):
            return
            
        bg_color = "#1A1A1A" if self.is_dark_mode else "#FFFFFF"
        text_color = "#E0E0E0" if self.is_dark_mode else "#111111"
        block_bg = "#212121" if self.is_dark_mode else "#F5F5F5"
        border_color = "#333333" if self.is_dark_mode else "#DDDDDD"
        title_color = "#64FFDA" if self.is_dark_mode else "#00796B"
        ayah_header = "#FFFFFF" if self.is_dark_mode else "#000000"
        reason_title = "#FFD54F" if self.is_dark_mode else "#F57F17"
        citation_bg = "#2A2A2A" if self.is_dark_mode else "#EBEBEB"
        citation_text = "#9E9E9E" if self.is_dark_mode else "#555555"
            
        doc_style = f"""
        <style>
            body {{ font-family: "Segoe UI", Arial, sans-serif; line-height: 1.6; color: {text_color}; background-color: {bg_color}; }}
            .surah-title {{ font-size: {self.base_font_size + 12}px; font-weight: bold; color: {title_color}; margin-bottom: 20px; }}
            hr {{ border-top: 1px solid {border_color}; margin: 20px 0; }}
            .intro-text {{ font-size: {self.base_font_size + 1}px; color: #B0BEC5; margin-bottom: 30px; line-height: 1.8; }}
            .ayah-block {{ background-color: {block_bg}; padding: 25px; border-radius: 12px; margin-bottom: 25px; border-left: 5px solid #00BFA5; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .ayah-header {{ font-size: {self.base_font_size + 4}px; font-weight: bold; color: {ayah_header}; margin-bottom: 12px; letter-spacing: 0.5px; }}
            .ayah-text {{ font-size: {self.base_font_size + 2}px; margin-bottom: 20px; line-height: 1.7; color: {text_color}; }}
            .reason-title {{ font-size: {self.base_font_size + 4}px; font-weight: bold; color: {reason_title}; margin-bottom: 12px; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px; }}
            .reason-text {{ font-size: {self.base_font_size + 2}px; color: {text_color}; line-height: 1.8; margin-bottom: 15px; }}
            .citation-block {{ margin-top: 20px; padding: 18px; background-color: {citation_bg}; border-radius: 10px; border-left: 5px solid #757575; }}
            .citation-title {{ font-size: {self.base_font_size + 1}px; font-weight: bold; color: {citation_text}; margin-bottom: 8px; }}
            .citation-text {{ font-size: {self.base_font_size}px; color: {citation_text}; line-height: 1.6; margin-bottom: 6px; }}
        </style>
        """
        self.content_browser.setHtml(doc_style + self.current_html_content)

    def increase_font(self):
        if self.base_font_size < 36:
            self.base_font_size += 2
            self.refresh_html_view()

    def decrease_font(self):
        if self.base_font_size > 10:
            self.base_font_size -= 2
            self.refresh_html_view()

    def copy_content(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content_browser.toPlainText())

    def build_ayah_html(self, ayah):
        import re
        ayah_num = ayah.get('ayah_number', '')
        ayah_text = ayah.get('ayah_text', '')
        reason = ayah.get('reason', '')
        
        # Extract citations
        # A citation block usually starts with [1] on a new line. We can split using regex matching `\n[1] ` or similar.
        main_reason = reason
        citations = ""
        citation_html = ""
        citation_match = re.search(r'(?:\n|^)(\[\d+\])\s', reason)
        if citation_match:
            split_index = citation_match.start()
            main_reason = reason[:split_index].strip()
            citations = reason[split_index:].strip()
            
            if citations:
                citation_html = "<div class='citation-block'><div class='citation-title'>Kaynakça:</div>"
                for line in citations.split('\n'):
                    line = line.strip()
                    if line:
                        citation_html += f"<div class='citation-text'>{line}</div>"
                citation_html += "</div>"
        
        html = f"""
        <div class='ayah-block'>
            <div class='ayah-header'>{ayah_num}. Ayet</div>
            <div class='ayah-text'>{ayah_text}</div>
        """
        if reason:
            # Wrap text nicely: Split by \n\n (paragraphs), replace \n inside with space, join by <br><br>
            paragraphs = main_reason.split('\n\n')
            cleaned_paragraphs = []
            for p in paragraphs:
                cleaned = p.replace('\n', ' ').strip()
                if cleaned:
                    cleaned_paragraphs.append(cleaned)
                    
            formatted_reason = '<br><br>'.join(cleaned_paragraphs)
            html += f"""
            <div class='reason-title'>Nüzul Sebebi:</div>
            <div class='reason-text'>{formatted_reason}</div>
            {citation_html}
            """
        html += "</div>"
        return html

    def apply_styles(self):
        if self.is_dark_mode:
            qss = """
            QMainWindow { background-color: #121212; }
            QWidget { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; font-size: 15px; color: #E0E0E0; }
            #HeaderWidget { background-color: #1E1E1E; border-bottom: 1px solid #333333; }
            #AppTitle { font-size: 24px; font-weight: bold; color: #FFFFFF; letter-spacing: 1px; }
            QPushButton { background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #404040; border-radius: 6px; padding: 8px 15px; font-weight: 600; }
            QPushButton:hover { background-color: #3D3D3D; border: 1px solid #505050; }
            QPushButton:pressed { background-color: #00BFA5; color: #000000; border: 1px solid #00BFA5; }
            QLineEdit { background-color: #242424; border: 1px solid #333333; border-radius: 10px; padding: 14px; color: #FFFFFF; font-size: 18px; margin-bottom: 5px; font-weight: bold; }
            QLineEdit:focus { border: 1px solid #00BFA5; background-color: #2A2A2A; }
            QTabWidget::pane { border: 1px solid #2A2A2A; border-radius: 8px; background-color: #1A1A1A; }
            QTabBar::tab { background-color: #2D2D2D; color: #B0BEC5; padding: 10px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #00BFA5; color: #000000; font-weight: bold; }
            QTabBar::tab:hover:!selected { background-color: #3D3D3D; }
            QTreeWidget, QListWidget { background-color: #1A1A1A; border: none; padding: 5px; outline: none; color: #E0E0E0; }
            QTreeWidget::item, QListWidget::item { padding: 10px; border-radius: 6px; margin-bottom: 2px; }
            QTreeWidget::item:selected, QListWidget::item:selected { background-color: #004D40; color: #FFFFFF; font-weight: bold; border-left: 3px solid #00BFA5; }
            QTreeWidget::item:hover:!selected, QListWidget::item:hover:!selected { background-color: #2D2D2D; }
            QTextBrowser { background-color: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 8px; padding: 25px; }
            QScrollBar:vertical { border: none; background: #1A1A1A; width: 12px; margin: 0px 0px 0px 0px; }
            QScrollBar::handle:vertical { background: #424242; min-height: 30px; border-radius: 6px; }
            QScrollBar::handle:vertical:hover { background: #505050; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QSplitter::handle { background-color: transparent; }
            """
        else:
            qss = """
            QMainWindow { background-color: #F5F5F5; }
            QWidget { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; font-size: 15px; color: #333333; }
            #HeaderWidget { background-color: #FFFFFF; border-bottom: 1px solid #E0E0E0; }
            #AppTitle { font-size: 24px; font-weight: bold; color: #111111; letter-spacing: 1px; }
            QPushButton { background-color: #EEEEEE; color: #333333; border: 1px solid #CCCCCC; border-radius: 6px; padding: 8px 15px; font-weight: 600; }
            QPushButton:hover { background-color: #DDDDDD; border: 1px solid #BBBBBB; }
            QPushButton:pressed { background-color: #00BFA5; color: #FFFFFF; border: 1px solid #00BFA5; }
            QLineEdit { background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 10px; padding: 14px; color: #111111; font-size: 18px; margin-bottom: 5px; font-weight: bold; }
            QLineEdit:focus { border: 1px solid #00BFA5; }
            QTabWidget::pane { border: 1px solid #CCCCCC; border-radius: 8px; background-color: #FFFFFF; }
            QTabBar::tab { background-color: #E0E0E0; color: #555555; padding: 10px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #00BFA5; color: #FFFFFF; font-weight: bold; }
            QTabBar::tab:hover:!selected { background-color: #D0D0D0; }
            QTreeWidget, QListWidget { background-color: #FFFFFF; border: none; padding: 5px; outline: none; color: #333333; }
            QTreeWidget::item, QListWidget::item { padding: 10px; border-radius: 6px; margin-bottom: 2px; }
            QTreeWidget::item:selected, QListWidget::item:selected { background-color: #E0F2F1; color: #00695C; font-weight: bold; border-left: 3px solid #00BFA5; }
            QTreeWidget::item:hover:!selected, QListWidget::item:hover:!selected { background-color: #F5F5F5; }
            QTextBrowser { background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 8px; padding: 25px; }
            QScrollBar:vertical { border: none; background: #E0E0E0; width: 12px; margin: 0px 0px 0px 0px; }
            QScrollBar::handle:vertical { background: #BDBDBD; min-height: 30px; border-radius: 6px; }
            QScrollBar::handle:vertical:hover { background: #9E9E9E; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QSplitter::handle { background-color: transparent; }
            """
        
        self.setStyleSheet(qss)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = EsbabApp()
    window.show()
    sys.exit(app.exec_())

