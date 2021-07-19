"""Create and bundle CSS and JS files."""
from flask_assets import Bundle, Environment
from flask import current_app as app


def compile_assets(assets):
    """Configure static asset bundles."""
    assets = Environment(app)
    Environment.auto_build = True
    Environment.debug = False
    # Stylesheets Bundles
    account_less_bundle = Bundle(
        'src/less/account.less',
        filters='less,cssmin',
        output='dist/css/account.css',
        extra={'rel': 'stylesheet/less'}
    )
    # JavaScript Bundle
    js_bundle = Bundle(
        'src/js/main.js',
        filters='jsmin',
        output='dist/js/main.min.js'
    )
    """Configure static home asset bundles."""

    # bundle path for dashboard's root directory is home/static/src/less
    # we need to set root directory as ml_model_microservice to pick up less compiler
    dashboard_less_bundle = Bundle(
        'home_bp/src/less/dashboard.less',
        filters='less,cssmin',
        output='dist/css/dashboard.css',
        extra={'rel': 'stylesheet/less'}
    )
    js_dashboard_bundle = Bundle(
        'home_bp/src/js/dashboard.js',
        filters='jsmin',
        output='dist/js/main.min.js'
    )

    # Register assets
    assets.register('account_less_bundle', account_less_bundle)
    assets.register('js_all', js_bundle)
    assets.register('dashboard_less_bundle', dashboard_less_bundle)
    assets.register('js_dashboard', js_dashboard_bundle)

    # Build assets
    account_less_bundle.build()
    js_bundle.build()
    dashboard_less_bundle.build()
    js_dashboard_bundle.build()


