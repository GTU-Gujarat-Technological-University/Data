try:
    import requests

    from flask import Flask, jsonify, send_file, redirect, request, render_template
    from io import BytesIO
    from lxml import html
except:
    print("""
    Please install the required libraries:

    pip install requests flask lxml
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    run above command and re-run the script.
    """.strip().replace("    ", ""))
    exit(1)


app = Flask(__name__)
app.secret_key = '9202c551sasda47s82ff96f4f9bf464240acfbb9'


class StudentDetails:
    URL_AWS_1 = "https://studentphoto.s3.us-west-2.amazonaws.com/Student_up_p/{enroll}.jpg"
    URL_AWS_2 = "https://studentphoto.s3.us-west-2.amazonaws.com/Photo_thumb/Photo_thumb/{enroll}.jpg"

    url_map = {
        "100": {
            "BASE_URL": "https://www.100points.gtu.ac.in",
            "URL": "{BASE_URL}/student_registration"
        },
        "de": {
            "BASE_URL": "https://de.gtu.ac.in",
            "URL": "{BASE_URL}/Account/StudentRegistration"
        },
        "pmms": {
            "BASE_URL": "https://pmms.gtu.ac.in",
            "URL": "{BASE_URL}/Layouts/ReqForStudentRegistration"
        },
        "billdesk": {
            "BASE_URL": "https://billdesk.gtu.ac.in",
            "URL": "{BASE_URL}/checkpaymentstatus.aspx"
        }
    }

    COMMON_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, enroll, key="100"):
        self.enroll = enroll
        self.session = requests.Session()
        self.state = False

        try:
            self.BASE_URL = self.url_map[key]["BASE_URL"]
            self.URL = self.url_map[key]["URL"].replace("{BASE_URL}", self.BASE_URL)
        except KeyError:
            return

        self.state = True
        self.headers = {
            **self.COMMON_HEADERS,
            "origin": self.BASE_URL,
            "referer": self.URL,
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "x-microsoftajax": "Delta=true",
        }

        build_payload_function_name = f"build_payload_{key}"
        self.dy_build_payload = getattr(self, build_payload_function_name, None)

        get_details_function_name = f"get_details_{key}"
        self.dy_get_details = getattr(self, get_details_function_name, None)

    def extract(self, tree, xpath):
        return "".join(tree.xpath(xpath)).strip()

    def get_details_100(self, text):
        tree = html.fromstring(text)
        if not (name := self.extract(tree, '//*[@name="txtStudentName"]/@value | //*[@name="txtStudentname"]/@value')):
            return {}

        items = {
            "Name": name.title(),
            "Email": self.extract(tree, '//*[@name="txtEmail"]/@value'),
            "Institute": self.extract(tree, '//*[@name="txtInstcode"]/@value'),
            "Branch": self.extract(tree, '//*[@name="txtbranch"]/@value'),
            "Discipline": self.extract(tree, '//*[@name="ddlstDiscipline"]/option[@selected]/text() | //*[@name="txtextype"]/@value'),
        }
        items["text"] = f"""
            <div>
                <div class="info-title">Email</div>
                <div class="info-value">{items["Email"]}</div>
            </div>
            <div>
                <div class="info-title">College Code</div>
                <div class="info-value">{items["Institute"]}</div>
            </div>
            <div>
                <div class="info-title">Department Code</div>
                <div class="info-value">{items["Branch"]}</div>
            </div>
            <div>
                <div class="info-title">Discipline</div>
                <div class="info-value">{items["Discipline"]}</div>
            </div>
        """
        return items

    def get_details_de(self, text):
        tree = html.fromstring(text)
        if not (name := self.extract(tree, '//*[@name="txtStudentName"]/@value | //*[@name="txtStudentname"]/@value')):
            return {}

        items = {
            "Name": name.title(),
            "Year": self.extract(tree, '//*[@name="txtYear"]/@value'),
            "College": self.extract(tree, '//*[@name="ddlstCollege"]/option[@selected]/text()'),
            "Department": self.extract(tree, '//*[@name="ddlstDepartment"]/option[@selected]/text()'),
            "Discipline": self.extract(tree, '//*[@name="ddlstDiscipline"]/option[@selected]/text() | //*[@name="txtextype"]/@value'),
        }
        items["text"] = f"""
            <div>
                <div class="info-title">Year</div>
                <div class="info-value">{items["Year"]}</div>
            </div>
            <div>
                <div class="info-title">College Name</div>
                <div class="info-value">{items["College"]}</div>
            </div>
            <div>
                <div class="info-title">Department</div>
                <div class="info-value">{items["Department"]}</div>
            </div>
            <div>
                <div class="info-title">Discipline</div>
                <div class="info-value">{items["Discipline"]}</div>
            </div>
        """
        return items

    def get_details_pmms(self, text):
        tree = html.fromstring(text)
        if not (name := self.extract(tree, '//*[@name="txtStudentName"]/@value | //*[@name="txtStudentname"]/@value')):
            return {}

        items = {
            "Name": name.title(),
            "Year": self.extract(tree, '//*[@name="txtYear"]/@value'),
            "College": self.extract(tree, '//*[@name="ddlstCollege"]/option[@selected]/text()'),
            "Department": self.extract(tree, '//*[@name="ddlstDepartment"]/option[@selected]/text()'),
            "Discipline": self.extract(tree, '//*[@name="ddlstDiscipline"]/option[@selected]/text() | //*[@name="txtextype"]/@value'),
        }
        items["text"] = f"""
            <div>
                <div class="info-title">Year</div>
                <div class="info-value">{items["Year"]}</div>
            </div>
            <div>
                <div class="info-title">College Name</div>
                <div class="info-value">{items["College"]}</div>
            </div>
            <div>
                <div class="info-title">Department</div>
                <div class="info-value">{items["Department"]}</div>
            </div>
            <div>
                <div class="info-title">Discipline</div>
                <div class="info-value">{items["Discipline"]}</div>
            </div>
        """
        return items

    def get_details_billdesk(self, text):
        tree = html.fromstring(text)
        if not (name := self.extract(tree, '//*[@id="lblname"]/text()')):
            return {}

        return {
            "Name": name.title(),
            "text": "",
        }

    def get_tokens(self, url=None, get_res=None):
        try:
            response = self.session.get(url or self.URL, headers=self.COMMON_HEADERS)
            response.raise_for_status()
        except requests.RequestException:
            return None if get_res else {}

        if get_res:
            return response

        tree = html.fromstring(response.text)
        return {
            "__VIEWSTATE": self.extract(tree, '//input[@id="__VIEWSTATE"]/@value'),
            "__VIEWSTATEGENERATOR": self.extract(tree, '//input[@id="__VIEWSTATEGENERATOR"]/@value'),
            "__EVENTVALIDATION": self.extract(tree, '//input[@id="__EVENTVALIDATION"]/@value'),
        }

    def build_payload_100(self, tokens):
        return {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": tokens.get("__VIEWSTATE", ""),
            "__VIEWSTATEGENERATOR": tokens.get("__VIEWSTATEGENERATOR", ""),
            "__EVENTVALIDATION": tokens.get("__EVENTVALIDATION", ""),
            "txtEnrollmentno": self.enroll,
            "btngo": "Go",
            "txtPassword": "",
            "txtEmail": "",
            "txtmobile": "",
        }

    def build_payload_de(self, tokens):
        return {
            "ScriptManager1": "UpdatePanel1|txtEnrolmentNo",
            "__LASTFOCUS": "",
            "__EVENTTARGET": "txtEnrolmentNo",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": tokens.get("__VIEWSTATE", ""),
            "__VIEWSTATEGENERATOR": tokens.get("__VIEWSTATEGENERATOR", "") or "C5760561",
            "__PREVIOUSPAGE": "HJM93fQ_VrukulBqmdKi1e00zLeTFjKuVeIW45dcBBphWeDkVHIpPkxMTzi8nuoIgCDKsKuRdseaLYSgECF5e5SOOU3lJfrddPaePRu5XYg--6LfdkoHjZsKzM_zQ9pS0",
            "__EVENTVALIDATION": tokens.get("__EVENTVALIDATION", ""),
            "txtEnrolmentNo": self.enroll,
            "txtYear": "",
            "ddlstCollege": "Select",
            "ddlstDepartment": "Select",
            "ddlstDiscipline": "Select",
            "ddlstSemester": "Select",
            "txtfirstname": "",
            "txtmiddelname": "",
            "txtlastname": "",
            "txtStudentName": "",
            "txtEmail": "",
            "txtConfirmEmailID": "",
            "txtMobileNo": "",
            "txtContactNo": "",
            "txtCaptcha": "",
            "__ASYNCPOST": "true",
        }

    def build_payload_pmms(self, tokens):
        return {
            "ScriptManager1": "UpdatePanel1|txtEnrolmentNo",
            "__LASTFOCUS": "",
            "__EVENTTARGET": "txtEnrolmentNo",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": tokens.get("__VIEWSTATE", ""),
            "__VIEWSTATEGENERATOR": tokens.get("__VIEWSTATEGENERATOR", "") or "37782284",
            "__PREVIOUSPAGE": "QxvGQtMtqT6N-31Dt7oBzre5KlK7U7KDCkVro4Q5GEfq3L75hElN1wJZM6wrKsb6GH9N6OTygjJb_ttZ1XUyX69NDwyFwZLN3c22jKWzGzgUiij9YXwlY18Jebi_LIjm0",
            "__EVENTVALIDATION": tokens.get("__EVENTVALIDATION", ""),
            "txtEnrolmentNo": self.enroll,
            "txtYear": "",
            "ddlstCollege": "Select",
            "ddlstDepartment": "Select",
            "ddlstDiscipline": "Select",
            "ddlstSemester": "Select",
            "txtfirstname": "",
            "txtmiddelname": "",
            "txtlastname": "",
            "txtStudentName": "",
            "txtEmail": "",
            "txtConfirmEmailID": "",
            "txtMobileNo": "",
            "txtContactNo": "",
            "__ASYNCPOST": "true",
        }

    def build_payload_billdesk(self, tokens):
        return {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": tokens.get("__VIEWSTATE", ""),
            "__VIEWSTATEGENERATOR": tokens.get("__VIEWSTATEGENERATOR", "") or "44F8D85A",
            "__EVENTVALIDATION": tokens.get("__EVENTVALIDATION", ""),
            "ddlAppType": "0",
            "txtmapnumber": self.enroll,
            "btnAdSearchMap": "Search",
            "rdsearch": "All Transactions",
        }

    def fetch_detail(self):
        if not self.state or not (tokens := self.get_tokens()):
            return {}

        try:
            response = self.session.post(self.URL, headers=self.headers, data=self.dy_build_payload(tokens))
            response.raise_for_status()
        except requests.RequestException:
            return {}

        items = self.dy_get_details(response.text)
        items['originaltext'] = response.text.replace('src="', f'src="{self.BASE_URL}/').replace('href="', f'href="{self.BASE_URL}/')
        items['source_link'] = self.URL
        return items

    def fetch_image(self):
        if not (response := self.get_tokens(url=self.URL_AWS_1.format(enroll=self.enroll), get_res=True)):
            response = self.get_tokens(url=self.URL_AWS_2.format(enroll=self.enroll), get_res=True)

        if response:
            return send_file(BytesIO(response.content), mimetype='image/jpeg')

        context = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00\x84\x00\t\x06\x07\x08\x07\x06\t\x08\x07\x08\n\n\t\x0b\r\x16\x0f\r\x0c\x0c\r\x1b\x14\x15\x10\x16 \x1d"" \x1d\x1f\x1f$(4,$&1\'\x1f\x1f-=-157:::#+?D?8C49:7\x01\n\n\n\r\x0c\r\x1a\x0f\x0f\x1a7%\x1f%77777777777777777777777777777777777777777777777777\xff\xc0\x00\x11\x08\x00\x94\x00\x94\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1b\x00\x01\x00\x03\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x05\x06\x03\x02\x01\x07\xff\xc4\x005\x10\x00\x02\x02\x01\x01\x04\x07\x05\x08\x03\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x11\x05!\x92\xd1\x12\x151AQSq\x13BRa\x91"24b\x81\xa1\xb1\xf0#C\xc1\x14\xff\xc4\x00\x15\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xc4\x00\x16\x11\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\x01\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfdl\x00T\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc2\xdc\xbcz\x9e\x96]\x04\xfc\x13\xd5\x9c\xd6\xd2\xc3\x7f\xeeK\xd6,\t`\xf1]\xb5\xda\xb5\xaeq\x9a\xfc\xafS\xd8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\xee\xb6\x14\xd6\xec\xb1\xe9\x18\x94Y\x9bF\xdc\x86\xe3\x16\xe1_\xc2\x9fo\xa8\xda\x99o"\xfe\x84[\xf6p\xdd\x1f\x9b\xefd"\xa0\x00\x03\xd4\'*\xe4\xa5\\\xa5\x19.\xf8\xbd\x0b\x9d\x9f\xb4\xd5\xb2Ud\xe8\xa7\xee\xcf\xb1?R\x90\x01\xae\x04\x1d\x95\x94\xf2(\xe8\xcd\xebe{\x9f\xcdw2q\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x008gZ\xe9\xc4\xb6\xc5\xb9\xa8\xe8\xbd^\xef\xfaw \xed\x9f\xc0\xcb\xe7$\x06|\x00T\x00\x00\x00\x00L\xd96\xba\xb3\xa1\xf0\xcf\xec\xbf\xef\xa9\xa22\xd8\xdf\x89\xabO\x8e?\xc9\xa9\x1a\xa0\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00E\xda\x95\xbb0mK\xb5%/\xa3%\x1f\x1aM4\xf7\xa6\xb4`d\x81\xdf2\x87\x8d\x91:\xde\xba\'\xb9\xf8\xa3\x81P\x00\x00\x00\x01\'g\xc3\xdaf\xd2\xbc%\xab\xf4[\xcd)S\xb11\x9aR\xc8\x97\xbc\xba1\xf4\xef-\x88\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xc0#g\xe1\xc7.\xa4\xbb,\x8f\xdd\x973=uS\xa6\xc7\x0bSR^&\xac\x8f\x94\xb1\xa7\x0e\x8eK\xafE\xd9\xd2{\xd0\x19\x90X]\x8b\x80\x9b\xf6y\xaa?\'\x17/\xe0\xe5\x1clf\xf7\xe7CO\x95r*"\x13p0%\x95%)\xa7\x1a|~/\x92%\xe2\xe3l\xe8\xb4\xdd\xd0\xb2^\x12\x96\xef\xa1k\x1d\x1a\xd6:5\xe2\x82\x91\x8a\x8cTb\x92KrH\xfa\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02.vl1!\xbf\xedNKt@\x91e\x90\xaa\x0evMF+\xb5\xb2\xaf#l%\xaa\xc6\x87K\xf3I\xe9\xfb\x15\xb9\x19\x16\xe4\xcf\xa7l\xb5}\xcb\xb9\x1cK\x04\x8b\xb32.\xd7\xa7l\xb4\xf0[\x97\xecG\xd0\x00\x80\x00\x01\xea\x13\x95oZ\xe4\xe2\xfcS<\x80\'\xd1\xb5rkzM\xabc\xe1-\xcf\xeaZb\xed\x1a24I\xf4\'\xf0\xcb\xbf\xd1\x99\xc0\x06\xb8\x14x\x1bJu8\xd7{s\xaf\xb1K\xbe<\xcb\xb8\xca2\x8a\x94Zi\xadS]\xe4W\xd0\x00\x00\x00\x00\x00\x1c32#\x8bC\xb2[\xdfdW\x8b3v\xd9;l\x95\x96=e.\xd6L\xdb\x17\xbbr\x9d~\xed{\xbf^\xf2\x01@\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00,vVk\xa6\xc5M\x8f\xfcr{\x9b\xf7Y\\\x00\xd7\x02.\xcd\xbf\xff\x00F\x1c$\xfe\xf2\xfb/\xf4%\x11@\x00\x00\x00\x19\xdb0s\'d\xe5\xece\xab\x93}\xab\x99\xe7\xab\xb3<\x87\xc4\xb9\x9a@\x06o\xab\xb3<\x87\xc4\xb9\x8e\xae\xcc\xf2\x1f\x12\xe6i\x01i\x19\xbe\xae\xcc\xf2\x1f\x12\xe6:\xbb3\xc8|K\x99\xa4\x02\x91\x9b\xea\xec\xcf!\xf1.c\xab\xb3<\x87\xc4\xb9\x9a@)\x19\xbe\xae\xcc\xf2\x1f\x12\xe6:\xbb3\xc8|K\x99\xa4\x02\x91\x9b\xea\xec\xcf!\xf1.c\xab\xb3<\x87\xc4\xb9\x9a@)\x19\xbe\xae\xcc\xf2\x1f\x12\xe6:\xbb3\xc8|K\x99\xa4\x02\x91]\xb1\xe8\xbf\x1e6\xc6\xea\xdcS\xd1\xad\xeb\x7f\xf7qb\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xff\xd9'
        return send_file(BytesIO(context), mimetype='image/jpeg')


@app.route('/', methods=['GET'])
def student_details():
    return render_template("index.html")


@app.route('/<enrollment>/', methods=['GET', 'POST'])
def get_student(enrollment):
    if request.method == 'GET':
        return redirect(f'/?enrollment={enrollment}')

    details = StudentDetails(enrollment, request.args.get("source")).fetch_detail()
    return jsonify(details)


@app.route('/<enrollment>/media/', methods=['GET'])
def get_student_media(enrollment):
    media = StudentDetails(enrollment).fetch_image()
    return media


@app.errorhandler(404)
def not_found(error):
    return redirect('/?error=404-not-found')


if __name__ == '__main__':
    app.run()
