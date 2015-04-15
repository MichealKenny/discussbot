from bottle import route, request, run
from praw import Reddit
import webbrowser


#Variables.
client_id = 'reddit app client_id here'
client_secret = 'reddit_app client_secret here'
user_agent = 'refresh_token generator for discussbot'

#Load instance of Reddit.
reddit = Reddit(user_agent=user_agent)
reddit.set_oauth_app_info(client_id=client_id, client_secret=client_secret,
                          redirect_uri='http://127.0.0.1:65010/authorize_callback')

url = reddit.get_authorize_url('uniqueKey', 'identity,submit,read', True)
webbrowser.open_new_tab(url)

@route('/authorize_callback')
def main():
    code = request.query.get('code', '')
    access_information = reddit.get_access_information(code)
    return('refresh token: ' + access_information['refresh_token'])

run(host='localhost', port=65010)