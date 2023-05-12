import browser_cookie3



def get_browser_cookies():
    cookies = []
    for cookie in browser_cookie3.firefox():
        cookie_info = {
            'domain': cookie.domain,
            'name': cookie.name,
            'value': cookie.value,
            'expires': cookie.expires
        }
        cookies.append(cookie_info)

    return cookies