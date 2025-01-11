from ptlibs import ptprinthelper, ptjsonlib
import base64
import string
import random
import re
import urllib

import requests
from typing import List, Tuple

class CookieTester:
    def __init__(self):
        pass

    COMMON_COOKIE_NAMES = [
    ["PHPSESSID", "PHP session cookie", "SESSION", "ERROR"],
    ["JSESSIONID", "Java session cookie", "SESSION", "ERROR"],
    ["Lang", "Standard cookie for save of set language", "standard","INFO"],
    ["password", "Typical name for cookie with password", "sensitive","ERROR"]
]

    def run(self, response, args, ptjsonlib: object, test_cookie_issues: bool = True, filter_cookie: str = None):
        self.ptjsonlib = ptjsonlib
        self.args = args
        self.use_json = False
        self.filter_cookie = filter_cookie
        self.test_cookie_issues = test_cookie_issues
        self.base_indent = 4
        self.duplicate_flags = None
        self.set_cookie_list: List[str] = self._get_set_cookie_headers(response)

        # Lists of vulnerable cookies
        cookie_injection_from_headers: list = self.check_cookie_injection_from_headers(url=response.url)
        cookie_acceptance_from_get_params: list = self.check_cookie_acceptance_from_get_param(url=response.url)
        cookie_injection_from_get_params: list = self.check_cookie_injection_from_get_param(url=response.url) if cookie_acceptance_from_get_params else []

        for header, value in response.raw.headers.items():
            if header.lower() == "set-cookie":
                ptprinthelper.ptprint(ptprinthelper.get_colored_text(f"Set-Cookie: {value}", "ADDITIONS"), colortext="WARNING", condition=not self.use_json, indent=(self.base_indent))

        cookie_list = response.cookies

        if not cookie_list and not self.set_cookie_list:
            ptprinthelper.ptprint(f"Site returned no cookies", bullet_type="", condition=not self.use_json)
            return

        for cookie in cookie_list:
            if self.filter_cookie and (self.filter_cookie.lower() != cookie.name.lower()):
                continue

            full_cookie: str = self._find_cookie_in_headers(cookie_list=self.set_cookie_list, cookie_to_find=f"{cookie.name}={cookie.value}") or cookie
            self.duplicate_flags = self.detect_duplicate_attributes(full_cookie)

            cookie_name = f"{cookie.name}={cookie.value}"
            cookie_path = cookie.path
            cookie_domain = cookie.domain
            cookie_expiration_timestamp = cookie.expires
            expires_string = next((m.group(1) for m in [re.search(r'Expires=([^;]+)', full_cookie, re.IGNORECASE)] if m), None)
            #cookie_expiration_text = next((item.split('=')[1] for item in full_cookie.split(":", maxsplit=1)[-1].strip().lower().split('; ') if item.lower().startswith('expires=')), None)

            cookie_secure_flag = cookie.secure
            cookie_http_flag = bool("httponly" in (key.lower() for key in cookie._rest.keys()))
            cookie_samesite_flag = next((value for key, value in cookie._rest.items() if key.lower() == "samesite"), None)

            node = self.ptjsonlib.create_node_object("cookie", properties={
                "name": cookie_name,
                "path": cookie_path,
                "domain": cookie_domain,
                "cookieExpiration": cookie_expiration_timestamp,
                "cookieSecureFlag": cookie_secure_flag,
                "cookieHttpOnlyFlag": cookie_http_flag,
                "cookieSameSiteFlag": cookie_samesite_flag
            }, vulnerabilities=[])

            ptprinthelper.ptprint(f'Name: {ptprinthelper.get_colored_text(cookie.name, "TITLE")}', condition=not self.use_json, newline_above=True, indent=self.base_indent)
            if self.test_cookie_issues:
                self.check_cookie_name(cookie.name)

            ptprinthelper.ptprint(f"Value: {urllib.parse.unquote(cookie.value)}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            if self.test_cookie_issues:
                self.check_cookie_value(urllib.parse.unquote(cookie.value))
            if self.is_base64(urllib.parse.unquote(cookie.value)):
                ptprinthelper.ptprint(f"Decoded value: {repr(self.is_base64(urllib.parse.unquote(cookie.value)))[2:-1]}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent, colortext=True)

            ptprinthelper.ptprint(f"Domain: {cookie_domain}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            if self.test_cookie_issues:
                self.check_cookie_domain(cookie_domain)

            ptprinthelper.ptprint(f"Path: {cookie_path}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            if self.test_cookie_issues:
                self.check_cookie_path(cookie_path)

            ptprinthelper.ptprint(f"Expires: {expires_string if expires_string else cookie_expiration_timestamp}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            if self.test_cookie_issues:
                self.check_cookie_expiration(cookie_expiration_timestamp)

            if self.test_cookie_issues:
                ptprinthelper.ptprint(f"Flags: ", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
                self.check_cookie_samesite_flag(cookie_samesite_flag)
                self.check_cookie_secure_flag(cookie_secure_flag)
                self.check_cookie_httponly_flag(cookie_http_flag)
            else:
                ptprinthelper.ptprint(f"Flags: ", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
                ptprinthelper.ptprint(f"    SameSite: {cookie_samesite_flag}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent+4)
                ptprinthelper.ptprint(f"    Secure: {cookie_secure_flag}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent+4)
                ptprinthelper.ptprint(f"    HttpOnly: {cookie_http_flag}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent+4)

            if cookie.name in cookie_injection_from_headers:
                ptprinthelper.ptprint(f"Application accepts any value from cookie", bullet_type="WARNING", condition=not self.use_json, indent=(self.base_indent), colortext=True)
            if cookie.name in cookie_acceptance_from_get_params:
                ptprinthelper.ptprint(f"Application accepts cookie value from GET parameter", bullet_type="WARNING", condition=not self.use_json, indent=(self.base_indent), colortext=True)
            if cookie.name in cookie_injection_from_get_params:
                ptprinthelper.ptprint(f"Application sets any value passed in GET parameter into the cookie ", bullet_type="WARNING", condition=not self.use_json, indent=(self.base_indent), colortext=True)

    def detect_duplicate_attributes(self, cookie_string):
        attributes = [attr.strip() for attr in cookie_string.split(';')]
        attribute_counts = {}
        for attr in attributes:
            key = attr.split('=')[0].strip().lower()  # Get the attribute name, case-insensitive
            attribute_counts[key] = attribute_counts.get(key, 0) + 1
        duplicates = {key.lower(): count for key, count in attribute_counts.items() if count > 1}
        return list(duplicates.keys())

    def _find_cookie_in_headers(self, cookie_list: list, cookie_to_find: str):
        for cookie in cookie_list:
            if re.findall(re.escape(cookie_to_find), cookie):
                return cookie

    def _get_set_cookie_headers(self, response):
        """Returns Set-Cookie headers from <response.raw.headers>"""
        raw_cookies: list = []
        if [h for h in response.raw.headers.keys() if h.lower() == "set-cookie"]:
            for header, value in response.raw.headers.items():
                if header.lower() == "set-cookie":
                    raw_cookies.append(f"{header}: {value}")
        return raw_cookies

    def _find_technology_by_cookie_value(self, cookie_value: str) -> list:
        """
        Determines which technologies a given cookie value matches based on defined rules.

        The function checks the provided cookie value against predefined technology rules
        in terms of length and format. If the cookie matches the rules for a technology,
        the corresponding technology name is added to the result list.

        Args:
            cookie_value (str): The value of the cookie to be analyzed.

        Returns:
            list: A list of technology names that match the cookie value. If no match is found,
                an empty list is returned.

        Example:
            >>> instance._find_technology_by_cookie_value("abc123def456gh789ijk012lmn345")
            ["PHP"]

            >>> instance._find_technology_by_cookie_value("ABCDEFGHIJKLMNO1234567890PQRST")
            ["JAVA"]
        """
        COMMON_COOKIE_VALUES = {
            "PHP": {"length": [26], "format": r"^[a-z0-9]+$"},
            "ASP.NET": {"length": [24], "format": r"^[a-z0-9]+$"},
            "JAVA": {"length": [32], "format": r"^[A-Z0-9]+$"},
        }

        result: list = []
        cookie_len = len(cookie_value)
        for technology_name, technology_attributes in COMMON_COOKIE_VALUES.items():
            if cookie_len in technology_attributes["length"]:
                if re.match(technology_attributes["format"], cookie_value):
                    result.append(technology_name)
                    continue
        return result

    def _find_technology_by_cookie_name(self, cookie_name):
        for technology_name, message, json_code, bullet_type in self.COMMON_COOKIE_NAMES:
            if technology_name.lower() == cookie_name.lower():
                return (technology_name, message, json_code, bullet_type)

    def check_cookie_expiration(self, expires):
        pass

    def check_cookie_path(self, cookie_path: str):
        pass

    def check_cookie_name(self, cookie_name: str):
        result = self._find_technology_by_cookie_name(cookie_name)
        if result:
            technology_name, message, json_code, bullet_type = result
            vuln_code = "PTV-WEB-INFO-TEDEFSIDNAME"
            #self.ptjsonlib.add_vulnerability(vuln_code) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})
            ptprinthelper.ptprint(f"Cookie has default name for {message}", bullet_type=bullet_type, condition=not self.use_json, colortext=False, indent=self.base_indent+4)
        if not cookie_name.startswith("__Host-"):
            ptprinthelper.ptprint(f"Cookie is missing '__Host-' prefix", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            vuln_code = "PTV-WEB-LSCOO-HSTPREFSENS"
            #self.ptjsonlib.add_vulnerability(vuln_code) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})

    def check_cookie_value(self, cookie_value: str):
        result = self._find_technology_by_cookie_value(cookie_value)
        if result:
            vuln_code = "PTV-WEB-INFO-TEDEFSIDFRM"
            ptprinthelper.ptprint(f"Cookie value has default format for {result if len(result) > 1 else result[0]} session cookie", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            #self.ptjsonlib.add_vulnerability(vuln_code) if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})

    def check_cookie_domain(self, cookie_domain: str):
        if cookie_domain.startswith("."):
            ptprinthelper.ptprint(f"Overscoped cookie issue", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)


    def check_cookie_httponly_flag(self, cookie_http_flag):
        if not cookie_http_flag:
            vuln_code = "PTV-WEB-LSCOO-FLHTTPSENS"
            #self.ptjsonlib.add_vulnerability(vuln_code) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})
            ptprinthelper.ptprint(f"HttpOnly flag missing", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
        else:
            if "httponly" in self.duplicate_flags:
                ptprinthelper.ptprint(f"HttpOnly flag duplicate", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            else:
                ptprinthelper.ptprint(f"HttpOnly flag present", bullet_type="OK", condition=not self.use_json, colortext=False, indent=self.base_indent+4)

    def check_cookie_samesite_flag(self, cookie_samesite_flag):
        if not cookie_samesite_flag:
            vuln_code = "PTV-WEB-LSCOO-FLSAMESENS"
            #self.ptjsonlib.add_vulnerability(vuln_code) if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})
            ptprinthelper.ptprint(f"SameSite flag missing", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
        else:
            if "samesite" in self.duplicate_flags:
                ptprinthelper.ptprint(f"SameSite duplicate", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            else:
                _bullet = "OK" if not cookie_samesite_flag.lower() == "none" else "WARNING"
                ptprinthelper.ptprint(f"SameSite={cookie_samesite_flag}", bullet_type=_bullet, condition=not self.use_json, colortext=False, indent=self.base_indent+4)

    def check_cookie_secure_flag(self, cookie_secure_flag):
        if not cookie_secure_flag:
            vuln_code = "PTV-WEB-LSCOO-FLSAMESENS"
            #self.ptjsonlib.add_vulnerability(vuln_code) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})
            ptprinthelper.ptprint(f"Secure flag missing", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
        else:
            if "secure" in self.duplicate_flags:
                ptprinthelper.ptprint(f"Secure flag duplicate", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            else:
                ptprinthelper.ptprint(f"Secure flag present", bullet_type="OK", condition=not self.use_json, colortext=False, indent=self.base_indent+4)

    def is_base64(self, value):
        try:
            if isinstance(value, str) and re.match('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$', value): # Kontrola, zda hodnota odpovídá formátu Base64
                decoded_value = base64.b64decode(value, validate=True)
                # Check if the decoded value is binary (contains non-printable characters)
                if all(c in string.printable for c in decoded_value.decode('utf-8', errors='ignore')):
                    return decoded_value  # Return the decoded value if it's printable
                else:
                    return None  # Return None if the result is binary (non-printable)
        except (base64.binascii.Error, TypeError):
            return False

    def check_cookie_injection_from_headers(self, url: str):
        """
        Tests if the application accepts arbitrary values in cookies.

        This method:
        1. Takes the cookies from a previous response and generates random values for each cookie, preserving the original cookie length.
        2. Sends a new request to the same URL, but with the modified cookies (random values).
        3. Compares the cookies from the new response to the original set of cookies.

        If any of the original cookies are missing in the response after sending random values,
        it indicates that the server accepted the random cookie values.
        """

        extracted_cookies: List[Tuple] = self._extract_cookie_names_and_values(set_cookie_list=self.set_cookie_list)
        cookies_to_send = {cookie[0]: ''.join(random.choices(string.ascii_letters+string.digits, k=len(cookie[1]))) for cookie in extracted_cookies}
        response = requests.get(url=url, cookies=cookies_to_send, headers=self.args.headers, proxies=self.args.proxy, verify=False)

        cookies_list1 = [cookie[0] for cookie in extracted_cookies]
        cookies_list2 = [cookie[0] for cookie in self._extract_cookie_names_and_values(self._get_set_cookie_headers(response))]
        missing_cookies = [cookie for cookie in cookies_list1 if cookie not in cookies_list2]
        return missing_cookies

    def check_cookie_acceptance_from_get_param(self, url) -> list:
        """Check if the application accepts cookie values passed via GET parameters."""
        extracted_cookies = self._extract_cookie_names_and_values(set_cookie_list=self.set_cookie_list)
        cookies_to_send = {cookie_name: cookie_value for cookie_name, cookie_value in extracted_cookies}

        # Send request with cookies in GET query
        response = requests.get(url, params=cookies_to_send, proxies=self.args.proxy, verify=False)
        response_cookie_names = [c[0] for c in self._extract_cookie_names_and_values(self._get_set_cookie_headers(response))]
        vuln_cookies = [cookie_name for cookie_name, _ in extracted_cookies if cookie_name not in response_cookie_names]
        return vuln_cookies

    def check_cookie_injection_from_get_param(self, url) -> list:
        """Check if the application sets cookie values passed via GET parameters into the response."""
        extracted_cookies = self._extract_cookie_names_and_values(set_cookie_list=self.set_cookie_list)
        cookies_to_send = {cookie_name: ''.join(random.choices(string.ascii_letters + string.digits, k=len(cookie_value))) for cookie_name, cookie_value in extracted_cookies}

        # Send request with cookies in GET query
        response = requests.get(url, params=cookies_to_send, proxies=self.args.proxy, verify=False)
        response_cookies = self._extract_cookie_names_and_values(self._get_set_cookie_headers(response))

        vuln_cookies = [cookie_name for cookie_name, cookie_value in response_cookies if cookie_value == cookies_to_send.get(cookie_name)]
        return vuln_cookies


    def _get_all_cookie_names(self, set_cookie_list: list) -> list:
        """Returns list of all cookie names parsed from response headers."""
        return [re.match(r"set-cookie: (\S+)=.*", header, re.IGNORECASE).group(1) for header in set_cookie_list if re.match(r"set-cookie: (\S+)=.*", header, re.IGNORECASE)]

    def _extract_cookie_names_and_values(self, set_cookie_list: list) -> List[Tuple[str, str]]:
        """Returns a list of tuples containing cookie names and their corresponding values parsed from response headers."""
        return [(match.group(1), match.group(2)) for header in set_cookie_list if (match := re.match(r"set-cookie: (\S+?)=([^;]+)", header, re.IGNORECASE))]

    def repeat_with_max_len(self, base_string="foobar", max_len=40):
        # Repeat the base string enough times to exceed the max length
        repeated = (base_string * (max_len // len(base_string))) + base_string[:max_len % len(base_string)]
        return repeated