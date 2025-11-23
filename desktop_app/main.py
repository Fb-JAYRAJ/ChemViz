"""
ChemViz Desktop Client (PyQt5 + Matplotlib)
Final Production-Ready Version
Author: Jayraj Sawant

This desktop client interacts with the Django REST API to:
 - Upload CSV datasets
 - View computed summaries
 - Visualize data using pie + bar charts
 - Access past upload history
 - Download generated PDF reports

Tech Stack (Fixed Requirements):
 - PyQt5 for GUI
 - Matplotlib for visualizations
 - Requests for API communication
"""

import sys
import os
import requests
from requests.auth import HTTPBasicAuth

# PyQt5 UI Components
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Matplotlib for charts
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Local backend URL (updated during deployment)
API_BASE = "http://127.0.0.1:8000"


# -------------------------------------------------------------------
# Helper: Card UI Component (reusable shell for all UI sections)
# -------------------------------------------------------------------
def Card():
    """Creates a styled QFrame representing a 'card' container."""
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame.setObjectName("card")
    frame.setStyleSheet("""
        QFrame#card {
            background: #1e293b;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.06);
        }
    """)
    return frame


# -------------------------------------------------------------------
# Chart Canvas: wraps a Matplotlib figure inside PyQt
# -------------------------------------------------------------------
class ChartCanvas(FigureCanvas):
    """
    Maintains the chart area.
    Initially shows a message, then gets replaced with pie + bar charts.
    """
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        # Single figure containing a placeholder message
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

        # Initial background + placeholder text
        self.fig.patch.set_facecolor("#0f172a")
        ax = self.fig.add_subplot(111)
        ax.text(
            0.5, 0.5,
            "Run analysis to see charts",
            ha="center", va="center",
            color="white",
            fontsize=12
        )
        ax.axis("off")
        self.draw()


# -------------------------------------------------------------------
# Main Desktop Application
# -------------------------------------------------------------------
class ChemVizDesktop(QWidget):
    """
    Main application window.
    Handles:
     - User authentication
     - File upload
     - Fetching latest summary
     - Drawing charts
     - Viewing history
     - Downloading PDF reports
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemViz – Desktop App")
        self.setGeometry(150, 120, 1150, 750)
        self.setObjectName("mainWindow")

        # App state
        self.current_dataset = None
        self.history = []
        self.selected_file = None

        # Main UI layout
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(18, 18, 18, 18)

        # App title
        title = QLabel("ChemViz – Desktop App")
        title.setFont(QFont("Inter", 20, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        # ------------------ Upload Section ------------------
        upload_card = Card()
        upload_layout = QVBoxLayout()
        upload_layout.setContentsMargins(16, 16, 16, 16)
        upload_card.setLayout(upload_layout)

        heading = QLabel("1. Upload CSV")
        heading.setFont(QFont("Inter", 14, QFont.Bold))
        heading.setStyleSheet("color: white;")
        upload_layout.addWidget(heading)

        # Authentication inputs
        cred_row = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setFixedHeight(32)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedHeight(32)

        cred_row.addWidget(self.user_input)
        cred_row.addSpacing(10)
        cred_row.addWidget(self.pass_input)
        upload_layout.addLayout(cred_row)

        # File chooser
        file_row = QHBoxLayout()
        self.filepath_label = QLabel("No file chosen")
        self.filepath_label.setStyleSheet("color: #cbd5e1;")
        self.filepath_label.setMinimumWidth(300)

        choose_btn = QPushButton("Choose CSV")
        choose_btn.clicked.connect(self.choose_file)
        choose_btn.setObjectName("choose")

        file_row.addWidget(self.filepath_label)
        file_row.addStretch()
        file_row.addWidget(choose_btn)
        upload_layout.addLayout(file_row)

        # Upload buttons
        btn_row = QHBoxLayout()

        self.upload_btn = QPushButton("Upload & Analyse")
        self.upload_btn.clicked.connect(self.upload_csv)
        self.upload_btn.setObjectName("btn-blue")

        self.load_latest_btn = QPushButton("Load Latest Summary")
        self.load_latest_btn.clicked.connect(self.load_latest_summary)
        self.load_latest_btn.setObjectName("btn-gray")

        self.download_pdf_btn = QPushButton("Download PDF Report")
        self.download_pdf_btn.clicked.connect(self.download_pdf)
        self.download_pdf_btn.setObjectName("btn-green")

        btn_row.addWidget(self.upload_btn)
        btn_row.addWidget(self.load_latest_btn)
        btn_row.addWidget(self.download_pdf_btn)

        upload_layout.addLayout(btn_row)
        layout.addWidget(upload_card)

        # ------------------ Summary Section ------------------
        summary_card = Card()
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_card.setLayout(summary_layout)

        summary_heading = QLabel("2. Summary")
        summary_heading.setFont(QFont("Inter", 14, QFont.Bold))
        summary_heading.setStyleSheet("color: white;")
        summary_layout.addWidget(summary_heading)

        self.summary_text = QLabel("No dataset selected.")
        self.summary_text.setStyleSheet("color: #cbd5e1;")
        summary_layout.addWidget(self.summary_text)

        layout.addWidget(summary_card)

        # ------------------ Charts + History Row ------------------
        charts_history_row = QHBoxLayout()
        charts_history_row.setSpacing(18)

        # Charts
        charts_card = Card()
        charts_layout = QVBoxLayout()
        charts_layout.setContentsMargins(12, 12, 12, 12)
        charts_card.setLayout(charts_layout)

        ch = QLabel("3. Charts")
        ch.setFont(QFont("Inter", 13, QFont.Bold))
        ch.setStyleSheet("color: white;")
        charts_layout.addWidget(ch)

        self.chart_canvas = ChartCanvas(self, width=8, height=3)
        charts_layout.addWidget(self.chart_canvas)

        charts_history_row.addWidget(charts_card, stretch=3)

        # History Sidebar
        history_card = Card()
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(12, 12, 12, 12)
        history_card.setLayout(history_layout)

        hh = QLabel("4. History")
        hh.setFont(QFont("Inter", 13, QFont.Bold))
        hh.setStyleSheet("color: white;")
        history_layout.addWidget(hh)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("color: #e2e8f0;")
        history_layout.addWidget(self.history_list)

        # History action buttons
        h_btns = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.fetch_history)
        refresh.setObjectName("btn-gray")

        view = QPushButton("View Selected")
        view.clicked.connect(self.view_selected_history)
        view.setObjectName("btn-blue")

        h_btns.addWidget(refresh)
        h_btns.addWidget(view)
        history_layout.addLayout(h_btns)

        charts_history_row.addWidget(history_card, stretch=1)
        layout.addLayout(charts_history_row)

        # Footer
        footer = QLabel("v1.0  •  Backend: http://127.0.0.1:8000")
        footer.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px;")
        layout.addWidget(footer, alignment=Qt.AlignRight)

        self.setLayout(layout)
        self.apply_styles()

    # -------------------------------------------------------------------
    # Stylesheet for buttons, inputs, layout colors
    # -------------------------------------------------------------------
    def apply_styles(self):
        qss = """
        QWidget#mainWindow { background: #0f172a; }

        QPushButton#btn-blue {
            background: #3b82f6;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
        }
        QPushButton#btn-blue:hover { background: #2563eb; }

        QPushButton#btn-green {
            background: #22c55e;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
        }
        QPushButton#btn-green:hover { background: #16a34a; }

        QPushButton#btn-gray {
            background: #475569;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
        }

        QPushButton#choose {
            background: #334155;
            color: white;
            padding: 6px 10px;
            border-radius: 6px;
        }

        QLineEdit {
            background: #0f172a;
            color: white;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px;
        }
        QListWidget { background: transparent; border: none; }
        """
        self.setStyleSheet(qss)

    # -------------------------------------------------------------------
    # File chooser dialog
    # -------------------------------------------------------------------
    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose CSV", "", "CSV Files (*.csv)")
        if path:
            self.selected_file = path
            self.filepath_label.setText(os.path.basename(path))

    # -------------------------------------------------------------------
    # Upload CSV to backend
    # -------------------------------------------------------------------
    def upload_csv(self):
        if not self.user_input.text() or not self.pass_input.text():
            QMessageBox.warning(self, "Auth required", "Enter username and password.")
            return

        if not self.selected_file:
            QMessageBox.warning(self, "No file", "Choose a CSV file first.")
            return

        try:
            with open(self.selected_file, "rb") as fh:
                r = requests.post(
                    f"{API_BASE}/api/upload/",
                    files={"file": fh},
                    auth=HTTPBasicAuth(self.user_input.text(), self.pass_input.text()),
                    timeout=20
                )

            if r.status_code in (200, 201):
                self.current_dataset = r.json()
                self.update_summary()
                self.plot_charts()
                self.fetch_history()
                QMessageBox.information(self, "Success", "Upload & analysis complete.")
            else:
                QMessageBox.critical(self, "Upload Failed", r.text or f"HTTP {r.status_code}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {e}")

    # -------------------------------------------------------------------
    # Load latest dataset summary
    # -------------------------------------------------------------------
    def load_latest_summary(self):
        if not self.user_input.text() or not self.pass_input.text():
            QMessageBox.warning(self, "Auth required", "Enter username and password.")
            return

        try:
            r = requests.get(
                f"{API_BASE}/api/summary/latest/",
                auth=HTTPBasicAuth(self.user_input.text(), self.pass_input.text()),
                timeout=20
            )

            if r.status_code in (200, 201):
                self.current_dataset = r.json()
                self.update_summary()
                self.plot_charts()
                QMessageBox.information(self, "Loaded", "Latest summary loaded.")
            else:
                QMessageBox.critical(self, "Load Failed", r.text or f"HTTP {r.status_code}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")

    # -------------------------------------------------------------------
    # Fetch upload history
    # -------------------------------------------------------------------
    def fetch_history(self):
        if not self.user_input.text() or not self.pass_input.text():
            QMessageBox.warning(self, "Auth required", "Enter username and password.")
            return

        try:
            r = requests.get(
                f"{API_BASE}/api/history/",
                auth=HTTPBasicAuth(self.user_input.text(), self.pass_input.text()),
                timeout=20
            )

            if r.status_code == 200:
                self.history = r.json()
                self.populate_history()
            else:
                QMessageBox.critical(self, "History", r.text or f"HTTP {r.status_code}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")

    # Populate history list
    def populate_history(self):
        self.history_list.clear()
        for item in self.history:
            lw = QListWidgetItem(f"{item.get('name')} — {item.get('original_filename')}")
            lw.setData(Qt.UserRole, item)
            self.history_list.addItem(lw)

    # View selected history item
    def view_selected_history(self):
        sel = self.history_list.currentItem()
        if not sel:
            QMessageBox.warning(self, "Select", "Pick an item from history to view.")
            return
        self.current_dataset = sel.data(Qt.UserRole)
        self.update_summary()
        self.plot_charts()

    # -------------------------------------------------------------------
    # Summary text updater
    # -------------------------------------------------------------------
    def update_summary(self):
        if not self.current_dataset:
            self.summary_text.setText("No dataset selected.")
            return

        d = self.current_dataset
        txt = (
            f"Total Count: {d.get('total_count')}\n"
            f"Avg Flowrate: {d.get('avg_flowrate'):.2f}\n"
            f"Avg Pressure: {d.get('avg_pressure'):.2f}\n"
            f"Avg Temperature: {d.get('avg_temperature'):.2f}"
        )
        self.summary_text.setText(txt)

    # -------------------------------------------------------------------
    # Chart drawer (pie + bar)
    # -------------------------------------------------------------------
    def plot_charts(self):
        if not self.current_dataset:
            # Show placeholder again
            self.chart_canvas.fig.clf()
            self.chart_canvas.fig.patch.set_facecolor("#0f172a")
            ax = self.chart_canvas.fig.add_subplot(111)
            ax.text(0.5, 0.5, "Run analysis to see charts",
                    ha="center", va="center",
                    color="white", fontsize=12)
            ax.axis("off")
            self.chart_canvas.draw()
            return

        d = self.current_dataset
        type_dist = d.get("type_distribution", {})
        labels = list(type_dist.keys())
        values = list(type_dist.values())

        # Prepare dual-plot canvas
        self.chart_canvas.fig.clf()
        ax1 = self.chart_canvas.fig.add_subplot(121)
        ax2 = self.chart_canvas.fig.add_subplot(122)

        # Pie chart
        if values:
            ax1.pie(values, labels=labels, autopct="%.1f%%", textprops={"color": "white"})
        else:
            ax1.text(0.5, 0.5, "No data", ha="center", va="center", color="white")
        ax1.set_title("Type Distribution", color="white")

        # Bar chart
        avg_vals = [
            d.get("avg_flowrate", 0),
            d.get("avg_pressure", 0),
            d.get("avg_temperature", 0)
        ]
        ax2.bar(["Flowrate", "Pressure", "Temperature"],
                avg_vals,
                color=["#3B82F6", "#EF4444", "#10B981"])
        ax2.set_title("Average Parameters", color="white")
        ax2.set_ylabel("Average value", color="white")

        # Style both charts
        for ax in (ax1, ax2):
            ax.patch.set_facecolor("#0f172a")
            for spine in ax.spines.values():
                spine.set_color("#334155")
            ax.tick_params(colors="white")

        self.chart_canvas.draw()

    # -------------------------------------------------------------------
    # PDF Download handler
    # -------------------------------------------------------------------
    def download_pdf(self):
        if not self.current_dataset:
            QMessageBox.warning(self, "No dataset", "No dataset selected.")
            return

        try:
            ds_id = self.current_dataset.get("id")
            r = requests.get(
                f"{API_BASE}/api/report/{ds_id}/",
                auth=HTTPBasicAuth(self.user_input.text(), self.pass_input.text()),
                timeout=20
            )

            if r.status_code == 200:
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "Save PDF", f"report_{ds_id}.pdf", "PDF Files (*.pdf)"
                )
                if save_path:
                    with open(save_path, "wb") as fh:
                        fh.write(r.content)
                    QMessageBox.information(self, "Saved", f"PDF saved to {save_path}")
            else:
                QMessageBox.critical(self, "PDF Error", r.text or f"HTTP {r.status_code}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")


# -------------------------------------------------------------------
# Application entry point
# -------------------------------------------------------------------
def main():
    """Application launcher."""
    app = QApplication(sys.argv)
    window = ChemVizDesktop()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()