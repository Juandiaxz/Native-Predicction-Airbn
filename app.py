import dash

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True)


server = app.server

# Asegúrate de que esté tal cual así:
app.config.suppress_callback_exceptions = True