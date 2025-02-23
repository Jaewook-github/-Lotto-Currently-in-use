# main.py
import sys
import matplotlib
import tkinter as tk
import logging
from modules.gui import LottoPredictionGUI

def main():
    """프로그램 실행 진입점"""
    try:
        matplotlib.use('TkAgg')  # Tkinter와 Matplotlib 호환성 보장
        root = tk.Tk()
        app = LottoPredictionGUI(root)
        root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        root.mainloop()
    except Exception as e:
        logging.error(f"프로그램 실행 오류: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()