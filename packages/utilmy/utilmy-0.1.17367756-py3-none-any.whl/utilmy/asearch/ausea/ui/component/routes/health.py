def setup_health_routes(app):
    @app.server.route('/health')
    def health_check():
        return {"status": "healthy"}, 200
