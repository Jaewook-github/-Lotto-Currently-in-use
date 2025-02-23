from flask import Blueprint, render_template, current_app
from app.models.lotto_analysis import LottoAnalysis

main = Blueprint('main', __name__)

@main.route('/')
def index():
    analysis = LottoAnalysis(current_app.config['SQLITE_DB_PATH'])
    latest_numbers = analysis.get_latest_numbers()
    summary_stats = analysis.get_summary_stats()
    return render_template('index.html',
                         latest_numbers=latest_numbers,
                         summary_stats=summary_stats)

@main.route('/analysis')
def analysis():
    analysis = LottoAnalysis(current_app.config['SQLITE_DB_PATH'])
    freq_dfs, stats_df = analysis.analyze()
    return render_template('analysis.html',
                         freq_dfs=freq_dfs,
                         stats_df=stats_df)