from bottle import route, request, run
from praw import Reddit
from json import loads
import webbrowser

#Load configuration file.
try:
    config_file = open('config.json', 'r')
    config = loads(config_file.read())
    config_file.close()

except FileNotFoundError:
    print('[Error]: config.json not found, make sure to edit and rename sample_config.json')
    exit()

settings = config['settings']
version = '0.9'
user_agent = settings['user_agent'].format(version=version)

#Load instance of Reddit.
reddit = Reddit(user_agent=user_agent)
reddit.set_oauth_app_info(client_id=settings['client_id'], client_secret=settings['client_secret'],
                          redirect_uri=settings['redirect_uri'])

url = reddit.get_authorize_url('uniqueKey', 'identity,submit,read', True)
webbrowser.open_new_tab(url)

@route('/authorize_callback')
def main():
    code = request.query.get('code', '')
    access_information = reddit.get_access_information(code)
    return('refresh token: ' + access_information['refresh_token'])

run(host='localhost', port=65010)