import sys
import time
from datetime import date, datetime, timedelta
from functools import cmp_to_key
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException, ElementNotInteractableException


def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = []
    for i in range((end - start).days + 1):
        # 월요일(0), 화요일(1), 수요일(2), 목요일(3), 금요일(4), 토요일(5), 일요일(6)
        if (start + timedelta(days=i)).weekday() == 0 or (start + timedelta(days=i)).weekday() == 3:
            # if (start + timedelta(days=i)).weekday() == 1 or (start + timedelta(days=i)).weekday() == 4:
            dates += [(start + timedelta(days=i)).strftime("%Y-%m-%d")]
        else:
            continue

    dates.reverse()
    return dates


def get_week_first(current_date=None):
    if current_date is not None:
        return datetime.strftime(current_date + timedelta(days=current_date.weekday() * -1), "%Y-%m-%d")
    else:
        # 2 weeks later
        return datetime.strftime(datetime.today() + timedelta(days=(datetime.today().weekday() * -1) + 7 + 7), "%Y-%m-%d")


def get_week_last(current_date=None):
    if current_date is not None:
        return datetime.strftime(current_date + timedelta(days=6 + (current_date.weekday() * -1)), "%Y-%m-%d")
    else:
        # 2 weeks later
        return datetime.strftime(datetime.today() + timedelta(days=6 + (datetime.today().weekday() * -1) + 7 + 7), "%Y-%m-%d")


def compare(x, y):
    xx = datetime.strptime(x.get_attribute("time"), "%H:%M")
    yy = datetime.strptime(y.get_attribute("time"), "%H:%M")
    if xx.hour > yy.hour:
        if xx.minute > yy.minute:
            return -1
        elif xx.minute < yy.minute:
            return 1
        else:
            return 0
    elif xx.hour < yy.hour:
        if xx.minute > yy.minute:
            return -1
        elif xx.minute < yy.minute:
            return 1
        else:
            return 0
    else:
        if xx.minute > yy.minute:
            return -1
        elif xx.minute < yy.minute:
            return 1
        else:
            return 0


def list_rearrange(elem, fav_from, fav_to, div_minutes=30):
    # Tee-Time list log
    print("예약 가능한 Tee time count: {}", len(elem))
    print("예약 가능 Tee time list:")
    print(*[e.get_attribute("time") for e in elem], sep='\n')

    # NOTE: caddy yes / no 분리
    with_caddy_elements = [e for e in elem if "Y" in e.get_attribute("caddy")]
    no_caddy_elements = [e for e in elem if "N" in e.get_attribute("caddy")]

    if len(with_caddy_elements) > 0:
        print("With caddy time: ", *[(caddy.get_attribute("time"), caddy.get_attribute(
            "caddy")) for caddy in with_caddy_elements], sep=' | ')
    if len(no_caddy_elements) > 0:
        print("No caddy time: ", *[(no.get_attribute("time"), no.get_attribute("caddy"))
              for no in no_caddy_elements], sep=' | ')

    prev_div_minutes = []
    next_div_minutes = []
    nocaddy_prev_div_minutes = []
    nocaddy_next_div_minutes = []

    # NOTE: 1. with caddy
    for f in range(fav_from, fav_to + 1):
        if len(with_caddy_elements) <= 0:
            break
        f_list = [t for t in with_caddy_elements if datetime.strptime(
            t.get_attribute("time"), "%H:%M").hour == f]
        prev_div_minutes += [f for f in f_list if datetime.strptime(
            f.get_attribute("time"), "%H:%M").minute <= div_minutes]
        next_div_minutes += [f for f in f_list if datetime.strptime(
            f.get_attribute("time"), "%H:%M").minute > div_minutes]

    sorted(prev_div_minutes, key=cmp_to_key(compare))

    # TEST: print list
    # for p in prev_div_minutes:
    #   print(p.get_attribute("date"), p.get_attribute("time"))
    # print("=" * 60)
    # for n in next_div_minutes:
    #   print(n.get_attribute("date"), n.get_attribute("time"))
    # print("=" * 60)

    # NOTE: 2. no caddy
    for f in range(fav_from, fav_to + 1):
        if len(no_caddy_elements) <= 0:
            break
        f_list = [t for t in no_caddy_elements if datetime.strptime(
            t.get_attribute("time"), "%H:%M").hour == f]
        nocaddy_prev_div_minutes += [f for f in f_list if datetime.strptime(
            f.get_attribute("time"), "%H:%M").minute <= div_minutes]
        nocaddy_next_div_minutes += [f for f in f_list if datetime.strptime(
            f.get_attribute("time"), "%H:%M").minute > div_minutes]

    sorted(nocaddy_prev_div_minutes, key=cmp_to_key(compare))

    # TEST: print list
    # for p in nocaddy_prev_div_minutes:
    #   print(p.get_attribute("date"), p.get_attribute("time"))
    # print("=" * 60)
    # for n in nocaddy_next_div_minutes:
    #   print(n.get_attribute("date"), n.get_attribute("time"))
    # print("=" * 60)

    return next_div_minutes + prev_div_minutes + nocaddy_next_div_minutes + nocaddy_prev_div_minutes


def is_open_reservation(date) -> bool:
    try:
        browser.refresh()
        WebDriverWait(browser, 1).until(EC.element_to_be_clickable(
            (By.XPATH, f"//./div[@class='mReserv-2']/.//a[@class='mR-open resv' and @date[contains(., '{date}')]]")))
        return True
    except TimeoutException:
        return False


def reservation_test(target_date, fav_time_from, fav_time_to):
    try:
        elem = WebDriverWait(browser, 2).until(EC.element_to_be_clickable(
            (By.XPATH, f"//./div[@class='mR-calendar']/.//a[@class='mR-open resv' and @date[contains(., '2022-03-11')]]"))).click()

        fav_position = "2"
        elem = WebDriverWait(browser, 2).until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[contains(@class, 't_list_box{fav_position}')]/.//p[@course = '{fav_position}' and (number(substring-before(@time, ':')) >= {fav_time_from} and number(substring-before(@time, ':')) <= {fav_time_to})]")))

        # NOTE: 예약 시도 타임 재배열 (캐디/노캐디, 선호 시간 기준으로 30분 이전 것은 역순으로 시도, 30분 이후는 정방향 시도)
        elem = list_rearrange(elem, fav_time_from, fav_time_to)
        print(elem)
    except TimeoutException or NoSuchElementException as e:
        print("해당 날짜의 예약이 오픈되지 않았거나 사라짐!! ", target_date)
        # print(e)
        return


def reservation_by_specific_date(target_date, fav_time_from, fav_time_to, isReal=False):
    retry = 0
    time.sleep(0.5)
    try:
        # 날짜별 예약 버튼
        elem = WebDriverWait(browser, 3).until(EC.element_to_be_clickable(
            (By.XPATH, f"//./div[@class='mR-calendar']/.//a[@class='mR-open resv' and @date[contains(., '{target_date}')]]")))
        elem.click()
    except TimeoutException or NoSuchElementException as ex:
        print("해당 날짜의 예약이 오픈되지 않았거나 사라짐!! ", target_date)
        print(ex)
        return
    except UnexpectedAlertPresentException as ex:
        # NOTE: 여기서 예약불가 처리를 하는 것으로... 해당날짜에 기존 예약이 존재하는 경우 더이상 예약이 불가하므로, return
        alert = browser.switch_to.alert
        print(f"Unexpected Alert in date: {alert.text}", ex)
        return
    except ElementNotInteractableException as ex:
        print(f"element not interactable: {ex}")
        retry = retry + 1
        if(retry < 11):
            reservation_by_specific_date(
                target_date, fav_time_from, fav_time_to, isReal)
        else:
            print(f"exceed retry attempt: {retry}")
            return

    try:
        # myRest-table > course
        # course = 1 > LK 코스
        # course = 2 > VL 코스
        # course = 3 > MT 코스
        fav_position = "1"
        WebDriverWait(browser, 3).until(EC.element_to_be_clickable(
            (By.XPATH, f"//./div[@class='myRes-tables']/.//p[@class='resv' and @course='{fav_position}' and (number(substring-before(@time, ':')) >= {fav_time_from} and number(substring-before(@time, ':')) <= {fav_time_to})]")))

        elem = browser.find_elements(
            By.XPATH, f"//./div[@class='myRes-tables']/.//p[@class='resv' and @course='{fav_position}' and (number(substring-before(@time, ':')) >= {fav_time_from} and number(substring-before(@time, ':')) <= {fav_time_to})]")

        # NOTE: 선택 날짜의 전체 예약 가능 시간 출력
        all_resv_elem = browser.find_elements(
            By.XPATH, f"//./div[@class='myRes-tables']/.//p[@class='resv']")
        print(f"[INFO] {target_date}")
        print(f"[INFO] all available tee-time : ", *[(resvElem.get_attribute("course"),
              resvElem.get_attribute("time")) for resvElem in all_resv_elem], sep=' | ')

        # NOTE: 예약 시도 타임 재배열 (캐디/노캐디, 선호 시간 기준으로 30분 이전 것은 역순으로 시도, 30분 이후는 정방향 시도)
        if len(elem) > 1:
            elem = list_rearrange(elem, fav_time_from, fav_time_to)
            print("reservation available times (final): ", *
                  [teeTime.get_attribute("time") for teeTime in elem], sep=' | ')
    except ElementNotInteractableException as ex:
        print(f"{target_date} 에서 Tee-Time List를 불러오지 못함 (not interactable)")
        print(ex)
        return
    except Exception as ex:
        print(f"{target_date} 에서 Tee-Time List를 불러오지 못함 (general exception)")
        print(ex)
        return

    for e in elem:
        try:
            print(
                f"course: {e.get_attribute('course')}, date: {e.get_attribute('date')}, time: {e.get_attribute('time')} 를 시도합니다.")
            e.click()

            # 예약하시겠습니까?
            WebDriverWait(browser, 2).until(EC.alert_is_present())
            alert = browser.switch_to.alert
            alertText = alert.text

            # 이미 스틸 당한 경우임 -> 다음 시간 시도
            if "다른" in alertText:
                alert.accept()
                print(f"other people occupied: {alertText}")
                continue
            else:
                print(alertText)
                if isReal:
                    # NOTE: real world
                    try:
                        # 예약하시겠습니까? (NOTE: 노캐디 포함도 안내문 나오면서 바로 예약 처리 됨.)
                        alert.accept()

                        # NOTE: '예약 되었습니다.' 와 함께 예약 세부내역 alert 이 나오는 것으로 추정 (확인 완료됨)
                        WebDriverWait(browser, 3).until(
                            EC.alert_is_present())
                        complete_alert = browser.switch_to.alert
                        complete_text = complete_alert.text
                        # NOTE: '예약하시겠습니까?' 이후 complete_text 에서 예약 완료된 시간입니다.' 가 나오는 경우가 racing condition
                        # 다시 시도해야함
                        if("예약 완료된 시간" in complete_text):
                            print(complete_text)
                            print("다른 Tee-Time 으로 재시도")
                            complete_alert.accept()
                            continue

                        print(complete_text)
                        complete_alert.accept()

                        return
                    except TimeoutException or NoAlertPresentException as ex:
                        print(f"failed to reserve: {ex}")
                        continue
                else:
                    # NOTE: develope world
                    # 노캐디의 경우 바로 예약이 들어옴
                    alert.dismiss()
                    time.sleep(0.6)
                    print(
                        f"dismiss by [develope]: {e.get_attribute('course')}, {e.get_attribute('date')}, {e.get_attribute('time')}")
                    continue
        except ElementNotInteractableException as ex:
            print(f"{date} {e} 시도 실패 (not interactable): {ex}")
            continue
        except TimeoutException as ex:
            print(f"{date} {e} 시도 실패: {ex}")
            browser.refresh()
            continue
        except UnexpectedAlertPresentException as ex:
            # NOTE: 대기예약을 걸어놓은 경우, 아래와 같이 나옴
            # 예약시 대기예약이 자동 취소됩니다.
            # 예약하시겠습니까? -> 대기예약이 없는 경우 그냥 이 메시지만 나옴
            alert = browser.switch_to.alert
            if alert is not None:
                alertText = alert.text
                print(alertText)
                alert.accept()
            print(f"Unexpected Alert: ", ex)
            return


def login_attempt(nTimes=3):
    # NOTE: 중복로그인의 케이스가 있으므로, 기본적으로 3회 시도
    for n in range(nTimes):
        try:
            # 아이디 입력
            elem = WebDriverWait(browser, 2).until(EC.presence_of_element_located(
                (By.XPATH, "//./div[@class='logIn']/.//input[@name='login_id']")))
            elem.send_keys(idpw)
            # 패스워드 입력
            elem = WebDriverWait(browser, 2).until(EC.presence_of_element_located(
                (By.XPATH, "//./div[@class='logIn']/.//input[@name='pwd']")))
            elem.send_keys(idpw)
            # 로그인 버튼 클릭
            elem = WebDriverWait(browser, 2).until(EC.presence_of_element_located(
                (By.XPATH, "//./div[@class='logIn']/.//div[@class='brn-btns']")))
            elem.click()

            print(f"{n} 회차: 로그인 성공")
            return True
        except UnexpectedAlertPresentException:
            # 다른 곳에서 로그인 한 경우...
            alert = browser.switch_to.alert
            alertMessage = alert.text
            print(f"{n} 회차: unexpected alert -> {alertMessage}")
            alert.accept()
            continue
        except NoSuchElementException:
            # 아이디, 패스워드 입력 창 안뜬 경우...
            browser.refresh()
            continue
    return False


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("No Args!")
    else:
        for i in range(1, len(sys.argv)):
            print(i, ":", sys.argv[i])

    url = "https://www.sejongemerson.co.kr/reservation/real_calendar.asp"
    idpw = "501933"
    chromedriver = "/usr/src/chrome/chromedriver"

    # selenium init
    options = Options()
    options.add_argument(
        f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29')
    options.add_argument("--headless")
    options.add_argument("window-size=1920x1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    service = Service(chromedriver)
    # service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)

    ################################ for headless start ################################
    # fake javascript
    # browser.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    # lanuages
    # browser.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    # fake GPU
    # browser.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
    ################################ for headless end ################################

    # develope, real switch
    isReal = bool(sys.argv[5]) if len(sys.argv) == 6 else False

    # 개발환경과 실제환경 분리 - date 관련 실수 예방
    if isReal:
        # real scenario
        from_date = get_week_first()
        to_date = get_week_last()
    else:
        # develope scenario
        from_date = sys.argv[1] if len(sys.argv) >= 5 else get_week_first()
        to_date = sys.argv[2] if len(sys.argv) >= 5 else get_week_last()

    # 선호 예약일 (월, 토, 일 자동 제외)
    target_dates = date_range(from_date, to_date)
    print(*target_dates, sep='\n')

    # 선호 예약시간 from, to
    fav_time_from = int(sys.argv[3]) if len(sys.argv) >= 5 else 17
    fav_time_to = int(sys.argv[4]) if len(sys.argv) >= 5 else 18

    browser.get(url)

    # NOTE: 모든 팝업 제거로 로직 변경 (2021-11-03)
    popups = browser.find_elements(
        By.XPATH, "//div[@id[contains(., \"pop_layer\")]]")
    if len(popups) > 0:
        for p in popups:
            browser.execute_script(
                "document.getElementById('" + p.get_attribute("id") + "').style.display='none';")

    # 로그인 시도 기본 3회 시도하여 실패하면 프로그램 종료
    isLoginSucceed = login_attempt()
    if not isLoginSucceed:
        print("로그인 실패, 기본 3회 시도함.")
        browser.quit()
        quit()

    # 날짜별 윈도우 핸들 저장을 위한 dictionary
    dict_target_dates = dict()

    # 오픈 탭 -> 메인 핸들은 이미 있으므로 하나 적게 오픈
    for i in range(len(target_dates) - 1):
        browser.execute_script(f"window.open('{url}', '_blank');")

    # 전체 핸들리스트를 날짜별 매핑
    for i, date in enumerate(target_dates):
        dict_target_dates[date] = browser.window_handles[i]

    # NOTE: check whether calendar is set -> maxTry 회 시도
    maxTry = 190
    circuitBreaker = True
    try:
        for i in range(maxTry):
            for key, value in dict_target_dates.items():
                browser.switch_to.window(value)
                if is_open_reservation(key):
                    print("go ahead")
                    circuitBreaker = False
                    break
                else:
                    print(f"{i + 1} 번째 : '{key}' 시도")
                    if i + 1 == maxTry:
                        raise Exception("up to max try")
                    # refresh = browser.find_element(
                    #     By.XPATH, "//./div[@class='mR-refresh-btn']")
                    # refresh.click()
                    # browser.refresh()
                    pass
            if circuitBreaker == False:
                break
    except Exception as e:
        print(f"{target_dates} is not open yet or {e}")
        browser.quit()
        quit()

    # NOTE: 예약 작업 시도 전 가능한 날짜 검색 (마감 되어 있는 것이 있을 수 있음, 물론 화요일 오전 10시에 시도하면 이런 경우는 없다고 봐야 함)
    # eligibleDates = browser.find_elements(By.XPATH, f"//div[@class='calendar']/ul/li/p[@class='j resv']")
    # available_dates = [d.get_attribute("date") for d in eligibleDates if d.get_attribute("date") in target_dates]
    #########################################################################################################
    for key, value in dict_target_dates.items():
        browser.switch_to.window(value)
        # browser.find_element(By.XPATH, "//./div[@class='mR-refresh-btn']").click()
        browser.refresh()
        print(f"{key} 예약작업 시작 in {value}")
        # reservation_test(key, fav_time_from, fav_time_to) # TEST
        reservation_by_specific_date(
            key, fav_time_from, fav_time_to, isReal=isReal)
    #########################################################################################################

    browser.get("https://www.sejongemerson.co.kr/reservation/real_calendar.asp")

    # NOTE: 다음 회차 오픈 일자를 검색 후, 스케줄링을 위해 정보 출력
    # TODO: 이를 기반으로 호출하는 측에서 스케줄링 로직 구현 -> C# Hangfire
    # TODO: 향후 공휴일 검증 API 완성 후 다음 주 예약 오픈 일자가 공휴일 인지 체크 해서 이전 or 이후 날짜로 대체 하도록...
    try:
        next_week = datetime.strptime(
            target_dates[-1], "%Y-%m-%d") + timedelta(days=7)
        elem = browser.find_element(
            By.XPATH, f"//./div[@class='mReserv-2']/.//h3[contains(text(), '{next_week.strftime('%Y년 %m월')}')]/parent::div/.//li/p[contains(text(), '{next_week.strftime('%e').lstrip()}')]/../span")
        # NOTE: 윈도우에서는 Day (01 - 31) 과 같은 표시는 %d (Linux python 동일)
        # NOTE: 1 - 31 과 같은 표시는 %e (Linux python 에서는 %-d)
        print(f"Next week open date: {elem.text}")
    except NoSuchElementException as e:
        print(f"Couldn't get next week element. EXCEPTION: {e}")
        pass

    # 로그아웃 처리
    print("Terminating a script...(logout)")
    browser.find_element(
        By.XPATH, "//./div[@class='login-btn']/a[@href='/member/logout.asp']").click()

    browser.quit()
