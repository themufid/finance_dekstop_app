from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import requests

API_KEY = "YOUR_API_KEY"
API_URL = f"https://www.alphavantage.co/query"

class FinanceAIApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Finance Management AI")
        self.setGeometry(100, 100, 1000, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        self.header_image = QLabel()
        image_path = "../Pengelolaan_KeuanganAI/assets/images/finance_trans.png"
        pixmap = QPixmap(image_path)

        width, height = 200, 200
        scaled_pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.header_image.setPixmap(scaled_pixmap)
        self.header_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.header_image)

        input_layout = QHBoxLayout()
        self.budget_label = QLabel("Budget:")
        self.budget_input = QLineEdit()
        self.budget_input.setPlaceholderText("Enter your budget")
        input_layout.addWidget(self.budget_label)
        input_layout.addWidget(self.budget_input)
        layout.addLayout(input_layout)

        self.invest_button = QPushButton("Get Investment Advice")
        self.invest_button.clicked.connect(self.investment_advice)
        layout.addWidget(self.invest_button)

        self.invest_result_label = QLabel("")
        layout.addWidget(self.invest_result_label)

        self.market_button = QPushButton("Predict Market Movement")
        self.market_button.clicked.connect(self.market_prediction)
        layout.addWidget(self.market_button)

        self.market_result_label = QLabel("")
        layout.addWidget(self.market_result_label)

        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(2)
        self.budget_table.setHorizontalHeaderLabels(["Category", "Amount"])
        self.budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.budget_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.budget_table)

        self.add_budget_button = QPushButton("Add Budget Data")
        self.add_budget_button.clicked.connect(self.add_budget_data)
        layout.addWidget(self.add_budget_button)

        self.calculate_total_button = QPushButton("Calculate Total Budget")
        self.calculate_total_button.clicked.connect(self.calculate_total_budget)
        layout.addWidget(self.calculate_total_button)

        self.total_budget_label = QLabel("")
        layout.addWidget(self.total_budget_label)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        download_layout = QHBoxLayout()
        self.download_png_button = QPushButton("Download Report (PNG)")
        self.download_png_button.clicked.connect(self.download_report_png)
        download_layout.addWidget(self.download_png_button)

        self.download_pdf_button = QPushButton("Download Report (PDF)")
        self.download_pdf_button.clicked.connect(self.download_report_pdf)
        download_layout.addWidget(self.download_pdf_button)

        layout.addLayout(download_layout)

        with open("style.qss", "r") as file:
            self.setStyleSheet(file.read())

    def investment_advice(self):
        budget = self.budget_input.text()
        if not budget:
            self.invest_result_label.setText("Please enter your budget.")
        else:
            symbol = "AAPL"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": API_KEY
            }
            response = requests.get(API_URL, params=params)
            data = response.json()

            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                latest_date = list(time_series.keys())[0]
                close_price = float(time_series[latest_date]["4. close"])
                budget = float(budget)
                advice = f"Invest 30% of your budget in {symbol} shares. Latest closing price: ${close_price:.2f}"
                self.invest_result_label.setText(advice)
            else:
                self.invest_result_label.setText("Failed to retrieve market data.")

    def market_prediction(self):
        symbol = "AAPL"
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "1min",
            "apikey": API_KEY
        }
        response = requests.get(API_URL, params=params)
        data = response.json()

        if "Time Series (1min)" in data:
            time_series = data["Time Series (1min)"]
            latest_date = list(time_series.keys())[0]
            close_price = float(time_series[latest_date]["4. close"])
            prediction = f"Market prediction: Current closing price of {symbol}: ${close_price:.2f}"
            self.market_result_label.setText(prediction)
        else:
            self.market_result_label.setText("Failed to retrieve market data.")

    def add_budget_data(self):
        category = self.budget_input.text()
        try:
            amount = float(self.budget_input.text())
        except ValueError:
            self.invest_result_label.setText("Please enter a valid amount.")
            return

        if not category or amount <= 0:
            self.invest_result_label.setText("Please enter a valid category and amount.")
        else:
            row_position = self.budget_table.rowCount()
            self.budget_table.insertRow(row_position)

            self.budget_table.setItem(row_position, 0, QTableWidgetItem(category))
            self.budget_table.setItem(row_position, 1, QTableWidgetItem(f"{amount:.2f}"))

            self.budget_input.clear()

            self.calculate_total_budget()
            
            self.create_budget_graph()

    def calculate_total_budget(self):
        total = 0
        for row in range(self.budget_table.rowCount()):
            amount_item = self.budget_table.item(row, 1)
            amount = float(amount_item.text())
            total += amount

        self.total_budget_label.setText(f"Total Budget: ${total:.2f}")

    def download_report_png(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report (PNG)", "", "PNG Files (*.png)")
        
        if file_path:
            self.create_budget_graph()
            self.figure.savefig(file_path, format="png")
            self.market_result_label.setText(f"Report successfully downloaded: {file_path}")

    def download_report_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report (PDF)", "", "PDF Files (*.pdf)")
        
        if file_path:
            self.create_budget_graph()
            self.figure.savefig(file_path, format="pdf")
            self.market_result_label.setText(f"Report successfully downloaded: {file_path}")

    def create_budget_graph(self):
        category = []
        amount = []

        for row in range(self.budget_table.rowCount()):
            category_item = self.budget_table.item(row, 0)
            amount_item = self.budget_table.item(row, 1)

            if category_item and amount_item:
                category.append(category_item.text())
                amount.append(float(amount_item.text()))

        self.figure.clear()
        
        self.figure.set_size_inches(8, 6)
        
        ax = self.figure.add_subplot(111)
        ax.bar(category, amount)

        ax.set_xlabel("Category")
        ax.set_ylabel("Budget Amount")
        ax.set_title("Budget Graph")

        self.figure.subplots_adjust(top=0.85, bottom=0.15, left=0.1, right=0.9)
        
        self.canvas.draw()

    def update_market_graph(self):
        symbol = "AAPL"
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "1min",
            "apikey": API_KEY
        }
        response = requests.get(API_URL, params=params)
        data = response.json()

        if "Time Series (1min)" in data:
            time_series = data["Time Series (1min)"]
            df_market = pd.DataFrame.from_dict(time_series, orient="index")
            df_market.index.name = "Time"
            df_market = df_market.astype(float)
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            df_market["4. close"].plot(ax=ax)
            
            ax.set_title(f"Market Movement {symbol}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Closing Price")
            
            self.canvas.draw()
        else:
            self.market_result_label.setText("Failed to retrieve market data.")

if __name__ == "__main__":
    app = QApplication([])
    window = FinanceAIApp()
    window.show()
    app.exec()
